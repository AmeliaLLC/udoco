from datetime import datetime, timedelta

from dateutil import parser as date_parser
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseNotFound)
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import pytz
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework.response import Response

from udoco import choices, forms, models, serializers


def redirect_old_apply_url(request, game_id):
    """Redirect the old apply url to the new apply url.

    This is a temporary view while the outstanding links are still
    active.
    """
    return redirect('/games/{}/apply'.format(game_id))


def certbot_view(request, public):
    """A view for handling cerbot.

    When renewing a `certbot` cert, a service will check that a url on your
    site has been updated with a private/public key challenge. This view allows
    us to update CERTBOT_KEY and then deploy and get negotiation for free.
    """
    key, _ = settings.CERTBOT_KEY.split('.')
    if public != key:
        return HttpResponseNotFound()
    return HttpResponse(settings.CERTBOT_KEY)


class ContactLeaguesView(View):
    """Contact the league schedulers."""
    template = 'udoco/contact.html'
    form = forms.ContactOfficialsForm

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ContactLeaguesView, self).dispatch(
            request, *args, **kwargs)

    def get(self, request):
        officials = models.Official.objects.filter(scheduling__gte=1)

        context = {
            'form': self.form(),
            'officials': officials,
        }
        return render(request, self.template, context)

    def post(self, request):
        officials = models.Official.objects.filter(scheduling__gte=1)

        form = self.form(request.POST)
        form.full_clean()

        with mail.get_connection() as connection:
            mail.EmailMessage(
                'A message from the UDOCO admins',
                form.cleaned_data['message'],
                'United Derby Officials Colorado <no-reply@mg.udoco.org>',
                ['United Derby Officials Colorado <no-reply@mg.udoco.org>'],
                bcc=[o.email for o in officials], connection=connection).send()

        messages.add_message(
            request, messages.INFO,
            'Your message has been sent.')

        return redirect('contact_leagues')


@csrf_exempt
def email_hook(request):
    """Handle in bound emails from Mailgun.

    See https://mailgun-documentation.readthedocs.io/en/latest/user_manual.html#receiving-forwarding-and-storing-messages
    """
    recipient = request.POST['recipient']
    sender = request.POST['sender']
    subject = request.POST['subject']
    body = request.POST['body-plain']

    email = '''Recipient: {}
Sender: {}
Body: {}'''.format(recipient, sender, body)

    with mail.get_connection() as connection:
        mail.EmailMessage(
            subject,
            email,
            'United Derby Officials Colorado <no-reply@mg.udoco.org>',
            [admin[1] for admin in settings.ADMINS],
            connection=connection).send()



# REST Framework
@api_view(['GET', 'PUT'])
def me(request):
    if not request.user.is_authenticated:
        return Response(None, status=401)

    if request.method == 'PUT':
        data = request.data
        request.user.display_name = data['display_name']
        request.user.email = data['email']
        request.user.emergency_contact_name = data['emergency_contact_name']
        request.user.emergency_contact_number = data['emergency_contact_number']
        request.user.game_history = data['game_history']
        request.user.phone_number = data['phone_number']
        request.user.league_affiliation = data['league_affiliation']
        request.user.save()
    serializer = serializers.OfficialSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
def feedback(request):
    """A view for providing feedback."""
    if not request.user.is_authenticated:
        return Response(None, status=401)

    try:
        message = request.data['message']
        if len(message) < 1:
            raise ValueError
        context = {
            'user': request.user,
            'message': message,
        }
    except (KeyError, ValueError):
        return HttpResponseBadRequest()
    with mail.get_connection() as connection:
        mail.EmailMessage(
            render_to_string('email/feedback_title.txt',),
            render_to_string('email/feedback_body.txt', context),
            'United Derby Officials Colorado <no-reply@mg.udoco.org>',
            [admin[1] for admin in settings.ADMINS],
            connection=connection).send()
    return Response('')


class IsScheduler(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated and
                request.user.league is not None)


class CanScheduleGame(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and
                request.user in obj.league.schedulers.all())


class GameViewSet(viewsets.ModelViewSet):
    queryset = models.Game.objects.filter(start__gt=datetime.now())
    serializer_class = serializers.GameSerializer
    permission_classes = [CanScheduleGame, IsScheduler]

    def create(self, request):
        game = models.Game()
        game.title = request.data['title']
        game.location = request.data['location']
        game.league = request.user.league
        game.creator = request.user

        game.start = date_parser.parse(request.data['start'])

        # This is temporary
        game.association = choices.AssociationChoices.OTHER
        game.game_type = choices.GameTypeChoices.OTHER
        game.save()

        serializer = self.serializer_class(
            game, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        try:
            qs = self.queryset.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(qs, context={'request': request})
        return Response(serializer.data)

    def partial_update(self, request, pk):
        game = self.queryset.get(pk=pk)
        self.check_object_permissions(self.request, game)

        completing = False

        if request.data.get('complete', False) and game.complete is False:
            game.complete = request.data['complete']
            completing = True

        if 'title' in request.data:
            # Updating event info, but not completing
            game.title = request.data.get('title', game.title)
            game.location = request.data.get('location', game.location)
            game.start = date_parser.parse(request.data['start'])

        game.save()
        game = self.queryset.get(pk=pk)

        if completing:
            # Completing game schedule, not updating info
            with mail.get_connection() as connection:
                mail.EmailMessage(
                    render_to_string(
                        'email/scheduling_title.txt',
                        {'game': game}),
                    render_to_string(
                        'email/scheduling_body.txt',
                        {'game': game}),
                    'United Derby Officials Colorado <no-reply@mg.udoco.org>',
                    ['United Derby Officials Colorado <no-reply@mg.udoco.org>'],
                    bcc=game.emails,
                    connection=connection).send()

        serializer = self.serializer_class(
            game, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        game = self.queryset.get(pk=pk)
        self.check_object_permissions(self.request, game)
        if game.complete:
            recipients = [user.email for user in game.staff]
        else:
            recipients = [
                official.email for official in game.applicants]
        with mail.get_connection() as connection:
            mail.EmailMessage(
                render_to_string(
                    'email/cancelled_title.txt',
                    {'game': game}),
                render_to_string(
                    'email/cancelled_body.txt',
                    {'game': game}),
                'United Derby Officials Colorado <no-reply@mg.udoco.org>',
                ['United Derby Officials Colorado <no-reply@mg.udoco.org>'],
                bcc=recipients, connection=connection).send()

        game.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LeagueScheduleViewSet(GameViewSet):
    """League-specific listing."""
    permission_classes = [IsScheduler]

    def list(self, request):
        if getattr(request.user, 'league', None) is None:
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)
        queryset = self.queryset.filter(league=request.user.league)
        serializer = self.serializer_class(
            data=queryset, context={'request': request}, many=True)
        serializer.is_valid()
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Game.objects.none()
    serializer_class = serializers.GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        rosters = models.Roster.objects.filter(
            Q(hr=user) | Q(ipr=user) | Q(jr1=user) | Q(jr2=user) |
            Q(opr1=user) | Q(opr2=user) | Q(opr3=user) | Q(alt=user) |
            Q(jt=user) | Q(sk1=user) | Q(sk2=user) | Q(pbm=user) |
            Q(pbt1=user) | Q(pbt2=user) | Q(pt1=user) | Q(pt2=user) |
            Q(pw=user) | Q(iwb=user) | Q(lt1=user) | Q(lt2=user) |
            Q(so=user) | Q(hnso=user) | Q(nsoalt=user) | Q(ptimer=user),
            game__complete=True
        )
        applications = models.ApplicationEntry.objects.filter(
            game__complete=False, official=user)
        ids = set(
            [r.game.id for r in rosters] + [a.game.id for a in applications])
        return models.Game.objects.filter(
            start__gt=datetime.now(), id__in=ids)

    def list(self, request):
        serializer = self.serializer_class(
            data=self.get_queryset(), context={'request': request}, many=True)
        serializer.is_valid()
        return Response(serializer.data)


def _update_roster_from_data(roster, data):
    """Update a roster based on json data.

    This function will update the roster and save it. It will return a list
    of newly rostered officials that were not previously rostered.
    """
    old_rostered = roster.game.rostered
    for key, val in data.items():
        if val is None or val == '':
            setattr(roster, key, None)
            setattr(roster, '{}_x'.format(key), None)
        elif int(val) > 0:
            official = models.Official.objects.get(pk=val)
            setattr(roster, key, official)
            setattr(roster, '{}_x'.format(key), None)
        elif int(val) < 0:
            official = models.Loser.objects.get(pk=abs(val))
            setattr(roster, '{}_x'.format(key), official)
            setattr(roster, key, None)
    roster.save()
    return [e for e in roster.game.rostered if e not in old_rostered]


def _remove_adjacent_applications(game, rostered):
    """Remove applications on adjacent games.

    When two games are time-adjacent, judged by the THRESHOLD variable,
    the moment one league schedules the official, their application is
    withdrawn from the adjacent events.

    There *may* be cases where this adjacent event logic is overly
    aggressive. In those cases, it's easy to work around by re-applying
    to the adjacent event, as this logic only kicks on for newly
    rostered officials.
    """
    # It's possible we'll want to include this information in the
    # "Save the date!" email.
    THRESHOLD = timedelta(hours=3)
    adjacent_games = models.Game.objects.filter(
        start__gte=game.start - THRESHOLD,
        start__lte=game.start + THRESHOLD)
    models.ApplicationEntry.objects.filter(
        official_id__in=[o.id for o in rostered],
        game_id__in=[
            g.id for g in adjacent_games
            if g.id != game.id]).delete()


class CanScheduleGame(permissions.BasePermission):
    """Whether the user can schedule an game.

    This is gross, because it parses the PATH_INFO of the
    request to get the game id.  That's probably bad, but
    I don't see a better way to do it.
    """
    NONADMIN_METHODS = []

    def _get_game(self, request):
        parts = request.META['PATH_INFO'].split('/')
        game_id = int(parts[3])
        return models.Game.objects.get(pk=game_id)

    def has_permission(self, request, *args, **kwargs):
        if request.method in self.NONADMIN_METHODS:
            return True
        game = self._get_game(request)
        return request.user in game.league.schedulers.all()
    has_object_permission = has_permission


class CanViewScheduleGame(CanScheduleGame):
    """Some endpoints are for scheduling AND applying."""
    NONADMIN_METHODS = ['POST', 'DELETE']


class RosterViewSet(viewsets.ModelViewSet):
    queryset = models.Roster.objects.none()
    serializer_class = serializers.RosterSerializer
    permission_classes = [permissions.IsAuthenticated, CanScheduleGame]

    def get_queryset(self, game_pk=None, pk=None):
        # XXX: rockstar (1 Jan 2019) - Wtf. Why did this work without the
        # default?
        if game_pk is None:
            return None
        if pk is not None:
            return models.Roster.objects.get(pk=pk, game__id=game_pk)
        else:
            return models.Roster.objects.filter(game__id=game_pk)

    def list(self, request, game_pk):
        qs = self.get_queryset(game_pk)
        self.check_object_permissions(self.request, qs)
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, game_pk, pk):
        qs = self.get_queryset(game_pk, pk)
        self.check_object_permissions(self.request, qs)
        serializer = self.serializer_class(qs)
        return Response(serializer.data)

    def create(self, request, game_pk):
        roster = models.Roster(game_id=game_pk)
        self.check_object_permissions(self.request, roster)
        rostered = _update_roster_from_data(roster, request.data)
        if len(rostered) > 0:
            _remove_adjacent_applications(roster.game, rostered)
            with mail.get_connection() as connection:
                mail.EmailMessage(
                    render_to_string(
                        'email/rostered_title.txt',
                        {'game': roster.game}),
                    render_to_string(
                        'email/rostered_body.txt',
                        {'game': roster.game}),
                    'United Derby Officials Colorado <no-reply@mg.udoco.org>',
                    ['United Derby Officials Colorado <no-reply@mg.udoco.org>'],
                    bcc=[r.email for r in rostered],
                    connection=connection).send()
        serializer = self.serializer_class(roster)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, game_pk, pk):
        roster = self.get_queryset(game_pk, pk)
        self.check_object_permissions(self.request, roster)
        rostered = _update_roster_from_data(roster, request.data)
        if len(rostered) > 0:
            _remove_adjacent_applications(roster.game, rostered)
            with mail.get_connection() as connection:
                mail.EmailMessage(
                    render_to_string(
                        'email/rostered_title.txt',
                        {'game': roster.game}),
                    render_to_string(
                        'email/rostered_body.txt',
                        {'game': roster.game}),
                    'United Derby Officials Colorado <no-reply@mg.udoco.org>',
                    ['United Derby Officials Colorado <no-reply@mg.udoco.org>'],
                    bcc=[r.email for r in rostered],
                    connection=connection).send()
        serializer = self.serializer_class(roster)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, game_pk, pk):
        roster = self.get_queryset(game_pk, pk)
        self.check_object_permissions(self.request, roster)
        roster.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = models.Official.objects.none()
    serializer_class = serializers.ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewScheduleGame]

    def get_queryset(self, game_pk=None, pk=None):
        # XXX: rockstar (1 Jan 2019) - Wtf. Why did this work without the
        # default?
        if game_pk is None:
            return None
        game = models.Game.objects.get(pk=game_pk)
        return models.Official.objects.filter(
            applicationentries__in=game.applicationentries.all()
        ).distinct()

    def list(self, request, game_pk):
        officials = self.get_queryset(game_pk)
        game = models.Game.objects.get(pk=game_pk)
        serializer = serializers.ApplicationSerializer(
            officials, context={'game': game}, many=True)
        return Response(serializer.data)

    def create(self, request, game_pk):
        game = models.Game.objects.get(pk=game_pk)
        if not game.official_can_apply(request.user):
            return Response(None, status=status.HTTP_409_CONFLICT)

        preferences = [int(p) for p in request.data['preferences']]
        for p in preferences:
            models.ApplicationEntry.objects.create(
                official=request.user, game=game,
                index=preferences.index(p),
                preference=p)

        notes = request.data.get('notes')
        if notes is not None and len(notes) > 0:
            models.ApplicationNotes.objects.create(
                official=request.user, game=game,
                content=request.data.get('notes'))

        context = {'game': game}
        serializer = serializers.ApplicationSerializer(
            request.user, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # XXX: rockstar (30 Nov 2017) - We don't care about the application
    # id. We just pass 0 as the pk.
    def destroy(self, request, game_pk, pk=None):
        game = models.Game.objects.get(pk=game_pk)
        if request.user not in game.applicants:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        models.ApplicationEntry.objects.filter(
            official=request.user, game=game).delete()
        models.ApplicationNotes.objects.filter(
            official=request.user, game=game).delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LoserApplicationViewPermission(CanScheduleGame):
    def has_permission(self, request, *args, **kwargs):
        game = self._get_game(request)
        return (
            (request.method == 'GET' and
                request.user in game.league.schedulers.all()) or
            (request.method == 'POST' and
                request.user.is_anonymous))


class LoserApplicationViewSet(viewsets.ViewSet):
    queryset = models.Loser.objects.none()
    serializer_class = serializers.LoserApplicationSerializer
    permission_classes = [LoserApplicationViewPermission]

    def list(self, request, game_pk=None):
        game = models.Game.objects.get(pk=game_pk)
        losers = models.Loser.objects.filter(
            applicationentries__in=game.loserapplicationentries.all()
        ).distinct()
        context = {'game': game}
        serializer = serializers.LoserApplicationSerializer(
            losers, context=context, many=True)
        return Response(serializer.data)

    def create(self, request, game_pk=None):
        game = models.Game.objects.get(pk=game_pk)
        if game.start < datetime.utcnow().replace(tzinfo=pytz.UTC):
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        try:
            loser = models.Loser.objects.create(
                derby_name=request.data['name'],
                email=request.data['email'],
                notes=request.data.get('notes', ''),
            )
            loser.save()
            preferences = request.data['preferences']
        except KeyError:
            return HttpResponseBadRequest()

        if len(preferences) < 1:
            return HttpResponseBadRequest()
        for preference in preferences:
            models.LoserApplicationEntry.objects.create(
                official=loser, game=game,
                index=preferences.index(preference),
                preference=preference).save()
        context = {'game': game}
        serializer = serializers.LoserApplicationSerializer(
            loser, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
