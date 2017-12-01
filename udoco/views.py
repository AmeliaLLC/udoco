from datetime import datetime

from dateutil import parser as date_parser
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core import mail
from django.db.models import Q
from django.http import (
    HttpResponse, HttpResponseBadRequest, HttpResponseNotFound)
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic import View
import pytz
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework import permissions
from rest_framework.response import Response

from udoco import choices, forms, models, serializers


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
                'United Derby Officials Colorado <no-reply@udoco.org>',
                ['United Derby Officials Colorado <no-reply@udoco.org>'],
                bcc=[o.email for o in officials], connection=connection).send()

        messages.add_message(
            request, messages.INFO,
            'Your message has been sent.')

        return redirect('contact_leagues')


# REST Framework
@api_view(['GET', 'PUT'])
def me(request):
    if not request.user.is_authenticated():
        if request.GET.get('old', False):  # pragma: no cover
            return Response(None)
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


class IsScheduler(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated()
                and request.user.league is not None)


class CanScheduleEvent(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated()
                and request.user in obj.league.schedulers.all())


class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Game.objects.filter(start__gt=datetime.now())
    serializer_class = serializers.GameSerializer
    permission_classes = [CanScheduleEvent, IsScheduler]

    def create(self, request):
        game = models.Game()
        game.title = request.data['title']
        game.location = request.data['location']
        game.league = request.user.league
        game.creator = request.user

        game.start = game.end = date_parser.parse(request.data['start'])

        # This is temporary
        game.association = choices.AssociationChoices.OTHER
        game.game_type = choices.GameTypeChoices.OTHER
        game.save()

        serializer = self.serializer_class(
            game, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        qs = self.queryset.get(pk=pk)
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
            game.title = request.data.get('title', game.title)
            game.location = request.data.get('location', game.location)
            game.start = game.end = date_parser.parse(request.data['start'])

        game.save()
        game = self.queryset.get(pk=pk)

        if completing:
            with mail.get_connection() as connection:
                mail.EmailMessage(
                    render_to_string(
                        'email/scheduling_title.txt',
                        {'event': game}),
                    render_to_string(
                        'email/scheduling_body.txt',
                        {'event': game}),
                    'United Derby Officials Colorado <no-reply@udoco.org>',
                    ['United Derby Officials Colorado <no-reply@udoco.org>'],
                    bcc=game.emails,
                    connection=connection).send()

        serializer = self.serializer_class(
            game, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk):
        event = self.queryset.get(pk=pk)
        self.check_object_permissions(self.request, event)
        if event.complete:
            recipients = [user.email for user in event.staff]
        else:
            recipients = [
                official.email for official in event.applicants]
        with mail.get_connection() as connection:
            mail.EmailMessage(
                render_to_string(
                    'email/cancelled_title.txt',
                    {'event': event}),
                render_to_string(
                    'email/cancelled_body.txt',
                    {'event': event}),
                'United Derby Officials Colorado <no-reply@udoco.org>',
                ['United Derby Officials Colorado <no-reply@udoco.org>'],
                bcc=recipients, connection=connection).send()

        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LeagueScheduleViewSet(EventViewSet):
    """League-specific listing."""
    permission_classes = [IsScheduler]

    def list(self, request):
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
            Q(so=user) | Q(hnso=user) | Q(nsoalt=user) | Q(ptimer=user)
        )
        # TODO: Should we add in applications?
        return models.Game.objects.filter(
            start__gt=datetime.now(),
            id__in=[r.game.id for r in rosters])

    def list(self, request):
        serializer = self.serializer_class(
            data=self.get_queryset(), context={'request': request}, many=True)
        serializer.is_valid()
        return Response(serializer.data)


def _update_roster_from_data(roster, data):
    """Update a roster based on json data.

    This updates the roster *in place*, but does not call save on the
    resulting changes.
    """
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


class CanScheduleEvent(permissions.BasePermission):
    """Whether the user can schedule an event.

    This is gross, because it parses the PATH_INFO of the
    request to get the event id.  That's probably bad, but
    I don't see a better way to do it.
    """
    NONADMIN_METHODS = []

    def _get_event(self, request):
        parts = request.META['PATH_INFO'].split('/')
        event_id = int(parts[3])
        return models.Game.objects.get(pk=event_id)

    def has_permission(self, request, *args, **kwargs):
        if request.method in self.NONADMIN_METHODS:
            return True
        event = self._get_event(request)
        return request.user in event.league.schedulers.all()
    has_object_permission = has_permission


class CanViewScheduleEvent(CanScheduleEvent):
    """Some endpoints are for scheduling AND applying."""
    NONADMIN_METHODS = ['POST', 'DELETE']


class RosterViewSet(viewsets.ModelViewSet):
    queryset = models.Roster.objects.none()
    serializer_class = serializers.RosterSerializer
    permission_classes = [permissions.IsAuthenticated, CanScheduleEvent]

    def get_queryset(self, event_pk, pk=None):
        if pk is not None:
            return models.Roster.objects.get(pk=pk, game__id=event_pk)
        else:
            return models.Roster.objects.filter(game__id=event_pk)

    def list(self, request, event_pk):
        qs = self.get_queryset(event_pk)
        self.check_object_permissions(self.request, qs)
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, event_pk, pk):
        qs = self.get_queryset(event_pk, pk)
        self.check_object_permissions(self.request, qs)
        serializer = self.serializer_class(qs)
        return Response(serializer.data)

    def create(self, request, event_pk):
        roster = models.Roster(game_id=event_pk)
        self.check_object_permissions(self.request, roster)
        _update_roster_from_data(roster, request.data)
        roster.save()
        serializer = self.serializer_class(roster)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, event_pk, pk):
        roster = self.get_queryset(event_pk, pk)
        self.check_object_permissions(self.request, roster)
        _update_roster_from_data(roster, request.data)
        roster.save()
        serializer = self.serializer_class(roster)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, event_pk, pk):
        roster = self.get_queryset(event_pk, pk)
        self.check_object_permissions(self.request, roster)
        roster.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = models.Official.objects.none()
    serializer_class = serializers.ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewScheduleEvent]

    def get_queryset(self, event_pk, pk=None):
        event = models.Game.objects.get(pk=event_pk)
        return models.Official.objects.filter(
            applicationentries__in=event.applicationentries.all()
        ).distinct()

    def list(self, request, event_pk):
        officials = self.get_queryset(event_pk)
        event = models.Game.objects.get(pk=event_pk)
        serializer = serializers.ApplicationSerializer(
            officials, context={'event': event}, many=True)
        return Response(serializer.data)

    def create(self, request, event_pk):
        event = models.Game.objects.get(pk=event_pk)
        if not event.official_can_apply(request.user):
            return Response(None, status=status.HTTP_409_CONFLICT)

        preferences = [int(p) for p in request.data]
        for p in preferences:
            models.ApplicationEntry.objects.create(
                official=request.user, event=event,
                index=preferences.index(p),
                preference=p)

        context = {'event': event}
        serializer = serializers.ApplicationSerializer(
            request.user, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # XXX: rockstar (30 Nov 2017) - We don't care about the application
    # event. We just pass 0 as the pk.
    def destroy(self, request, event_pk, pk=None):
        event = models.Game.objects.get(pk=event_pk)
        if request.user not in event.applicants:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        models.ApplicationEntry.objects.filter(
            official=request.user, event=event).delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LoserApplicationViewPermission(CanScheduleEvent):
    def has_permission(self, request, *args, **kwargs):
        event = self._get_event(request)
        return (
            (request.method == 'GET' and
                request.user in event.league.schedulers.all()) or
            (request.method == 'POST' and
                request.user.is_anonymous()))


class LoserApplicationViewSet(viewsets.ViewSet):
    queryset = models.Loser.objects.none()
    serializer_class = serializers.LoserApplicationSerializer
    permission_classes = [LoserApplicationViewPermission]

    def list(self, request, event_pk=None):
        event = models.Game.objects.get(pk=event_pk)
        losers = models.Loser.objects.filter(
            applicationentries__in=event.loserapplicationentries.all()
        ).distinct()
        context = {'event': event}
        serializer = serializers.LoserApplicationSerializer(
            losers, context=context, many=True)
        return Response(serializer.data)

    def create(self, request, event_pk=None):
        event = models.Game.objects.get(pk=event_pk)
        if event.start < datetime.utcnow().replace(tzinfo=pytz.UTC):
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        try:
            loser = models.Loser.objects.create(
                derby_name=request.data['name'],
                email_address=request.data['email'],
            )
            loser.save()
            preferences = request.data['preferences']
        except KeyError:
            return HttpResponseBadRequest()

        if len(preferences) < 1:
            return HttpResponseBadRequest()
        for preference in preferences:
            models.LoserApplicationEntry.objects.create(
                official=loser, event=event,
                index=preferences.index(preference),
                preference=preference).save()
        context = {'event': event}
        serializer = serializers.LoserApplicationSerializer(
            loser, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
