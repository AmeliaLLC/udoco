from datetime import datetime

from dateutil import parser as date_parser
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators import csrf
from django.views.generic import View
import pytz
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from udoco import choices, forms, models, serializers


class _EventView(View):
    """An event view."""

    @method_decorator(csrf.csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(_EventView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, event_id):
        """Apply to the event."""
        try:
            event = models.Game.objects.get(id=event_id)
        except models.Game.DoesNotExist:
            raise Http404

        if request.user in event.applicants:
            return HttpResponseBadRequest()

        if not event.official_can_apply(request.user):
            return HttpResponseBadRequest()

        preferences = request.POST.getlist('preferences[]')

        for pref in preferences:
            models.ApplicationEntry.objects.create(
                official=request.user, event=event,
                index=preferences.index(pref),
                preference=pref)
        return JsonResponse({'data': {}})


class _EventWithdrawView(View):
    """Event withdrawal mechanism."""

    @method_decorator(csrf.csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(_EventWithdrawView, self).dispatch(
            request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, event_id):
        """Apply to the event."""
        try:
            event = models.Game.objects.get(id=event_id)
        except models.Game.DoesNotExist:
            raise Http404

        if request.user not in event.applicants:
            return HttpResponseBadRequest()

        models.ApplicationEntry.objects.filter(
            official=request.user, event=event).delete()
        return JsonResponse({'data': {}})


class AddEventView(View):
    """A view for adding a new event."""
    template = 'udoco/add_event.html'
    form = forms.AddEventForm

    @method_decorator(login_required)
    def get(self, request, event_id=None):
        if event_id is not None:
            event = models.Game.objects.get(id=event_id)
            if request.user not in event.league.schedulers.all():
                raise Http404
            initial = {
                'league': event.league,
                'title': event.title,
                'start': event.start,
                'location': event.location,
                'association': event.association,
                'game_type': event.game_type,
            }
            form = self.form(initial=initial)
            form.fields['league'].queryset = request.user.scheduling.all()
            form.fields['league'].readonly = True
        else:
            form = self.form()
            form.fields['league'].queryset = request.user.scheduling.all()
        return render(request, self.template, {'form': form})

    @method_decorator(login_required)
    def post(self, request, event_id=None):
        form = self.form(request.POST)
        form.fields['league'].queryset = request.user.scheduling.all()
        if form.is_valid():
            if event_id is not None:
                game = models.Game.objects.get(id=event_id)
                if request.user not in game.league.schedulers.all():
                    raise Http404
            else:
                game = models.Game()
            game.title = form.cleaned_data['title']
            game.start = form.cleaned_data['start']
            # TODO: support multi-day events
            game.end = form.cleaned_data['start']
            game.location = form.cleaned_data['location']

            game.association = form.cleaned_data['association']
            game.game_type = form.cleaned_data['game_type']

            game.league = form.cleaned_data['league']
            game.creator = request.user
            game.save()
            if event_id is not None:
                messages.add_message(request, messages.INFO, 'Game updated')
            else:
                messages.add_message(request, messages.INFO, 'Game created')
            return redirect('view_event', event_id=game.id)
        else:
            return render(request, self.template, {'form': form})


class EventView(View):
    """A view for applying to a game."""

    def get(self, request, event_id):
        return redirect('/#events/{}'.format(event_id))


class EventWithdrawalView(View):
    """A view for withdrawing a roster."""

    @method_decorator(login_required)
    def post(self, request, event_id):
        event = models.Game.objects.get(id=event_id)
        try:
            models.ApplicationEntry.objects.filter(
                official=request.user, event=event).delete()
            messages.add_message(
                request, messages.INFO,
                'You have withdrawn from the event.')
            return redirect('events')
        except models.ApplicationEntry.DoesNotExist:
            raise Http404


class ContactEventView(View):
    """A view for contacting members of a roster."""
    template = 'udoco/contact_roster.html'
    form = forms.ContactOfficialsForm

    @method_decorator(login_required)
    def get(self, request, event_id, form=None):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()

        if event.complete:
            officials = event.staff
            losers = event.staffed_losers
        else:
            officials = event.applicants.all()
            losers = event.losers

        context = {
            'form': self.form(),
            'officials': officials,
            'losers': losers,
        }
        return render(request, self.template, context)

    @method_decorator(login_required)
    def post(self, request, event_id):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()

        form = self.form(request.POST)
        if not form.is_valid():
            return self.get(request, event_id, form=form)

        with mail.get_connection() as connection:
            mail.EmailMessage(
                'A message from {}'.format(event.league.name),
                form.cleaned_data['message'],
                'United Derby Officials Colorado <no-reply@udoco.org>',
                ['United Derby Officials Colorado <no-reply@udoco.org>'],
                bcc=event.emails, connection=connection).send()

        messages.add_message(
            request, messages.INFO,
            'Your message has been sent.')

        return redirect('leagues')


class SchedulingView(View):
    """A view for scheduling officials for games."""
    template = 'udoco/schedule_event.html'

    @method_decorator(login_required)
    def get(self, request, event_id, form=None):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()

        if event.complete:
            return redirect('view_event', event_id)

        blank_form = forms.SchedulingForm(event)
        if form is not None and form.cleaned_data['roster'] is None:
            blank_form = form

        roster_forms = []
        for roster in event.rosters.all().order_by('id'):
            if form is not None and roster.id == form.cleaned_data['roster']:
                roster_forms.append(form)
                continue
            initial = {
                'roster': roster.id,
                'hr': roster.hr,
                'ipr': roster.ipr,
                'jr1': roster.jr1,
                'jr2': roster.jr2,
                'opr1': roster.opr1,
                'opr2': roster.opr2,
                'opr3': roster.opr3,
                'alt': roster.alt,
                'jt': roster.jt,
                'sk1': roster.sk1,
                'sk2': roster.sk2,
                'pbm': roster.pbm,
                'pbt1': roster.pbt1,
                'pbt2': roster.pbt2,
                'pt1': roster.pt1,
                'pt2': roster.pt2,
                'pw': roster.pw,
                'iwb': roster.iwb,
                'lt1': roster.lt1,
                'lt2': roster.lt2,
                'so': roster.so,
                'hnso': roster.hnso,
                'ptimer': roster.ptimer,
                'nsoalt': roster.nsoalt,

                'hr_': roster.hr_x,
                'ipr_': roster.ipr_x,
                'jr1_': roster.jr1_x,
                'jr2_': roster.jr2_x,
                'opr1_': roster.opr1_x,
                'opr2_': roster.opr2_x,
                'opr3_': roster.opr3_x,
                'alt_': roster.alt_x,
                'jt_': roster.jt_x,
                'sk1_': roster.sk1_x,
                'sk2_': roster.sk2_x,
                'pbm_': roster.pbm_x,
                'pbt1_': roster.pbt1_x,
                'pbt2_': roster.pbt2_x,
                'pt1_': roster.pt1_x,
                'pt2_': roster.pt2_x,
                'pw_': roster.pw_x,
                'iwb_': roster.iwb_x,
                'lt1_': roster.lt1_x,
                'lt2_': roster.lt2_x,
                'so_': roster.so_x,
                'hnso_': roster.hnso_x,
                'ptimer_': roster.ptimer_x,
                'nsoalt_': roster.nsoalt_x,
            }
            roster_forms.append(forms.SchedulingForm(
                event,
                initial=initial))

        context = {
            'blank_form': blank_form,
            'forms': roster_forms,
            'event': event,
        }
        return render(request, self.template, context)

    @method_decorator(login_required)
    def post(self, request, event_id):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()

        if request.POST.get('action', '').startswith('Remove'):
            try:
                roster_id = int(request.POST.get('roster'))
                models.Roster.objects.get(pk=roster_id).delete()
                return redirect('schedule_event', event_id)
            except (TypeError, models.Roster.DoesNotExist):
                return HttpResponseBadRequest()

        form = forms.SchedulingForm(event, request.POST)
        if not form.is_valid():
            return self.get(request, event_id, form=form)

        if form.cleaned_data['roster']:
            roster = models.Roster.objects.get(
                id=form.cleaned_data['roster'])
        else:
            roster = models.Roster()
            roster.game = event
        roster.hr = form.cleaned_data['hr']
        roster.ipr = form.cleaned_data['ipr']
        roster.jr1 = form.cleaned_data['jr1']
        roster.jr2 = form.cleaned_data['jr2']
        roster.opr1 = form.cleaned_data['opr1']
        roster.opr2 = form.cleaned_data['opr2']
        roster.opr3 = form.cleaned_data['opr3']
        roster.alt = form.cleaned_data['alt']
        roster.jt = form.cleaned_data['jt']
        roster.sk1 = form.cleaned_data['sk1']
        roster.sk2 = form.cleaned_data['sk2']
        roster.pbm = form.cleaned_data['pbm']
        roster.pbt1 = form.cleaned_data['pbt1']
        roster.pbt2 = form.cleaned_data['pbt2']
        roster.pt1 = form.cleaned_data['pt1']
        roster.pt2 = form.cleaned_data['pt2']
        roster.pw = form.cleaned_data['pw']
        roster.iwb = form.cleaned_data['iwb']
        roster.lt1 = form.cleaned_data['lt1']
        roster.lt2 = form.cleaned_data['lt2']
        roster.so = form.cleaned_data['so']
        roster.hnso = form.cleaned_data['hnso']
        roster.ptimer = form.cleaned_data['ptimer']
        roster.nsoalt = form.cleaned_data['nsoalt']

        roster.hr_x = form.cleaned_data['hr_']
        roster.ipr_x = form.cleaned_data['ipr_']
        roster.jr1_x = form.cleaned_data['jr1_']
        roster.jr2_x = form.cleaned_data['jr2_']
        roster.opr1_x = form.cleaned_data['opr1_']
        roster.opr2_x = form.cleaned_data['opr2_']
        roster.opr3_x = form.cleaned_data['opr3_']
        roster.alt_x = form.cleaned_data['alt_']
        roster.jt_x = form.cleaned_data['jt_']
        roster.sk1_x = form.cleaned_data['sk1_']
        roster.sk2_x = form.cleaned_data['sk2_']
        roster.pbm_x = form.cleaned_data['pbm_']
        roster.pbt1_x = form.cleaned_data['pbt1_']
        roster.pbt2_x = form.cleaned_data['pbt2_']
        roster.pt1_x = form.cleaned_data['pt1_']
        roster.pt2_x = form.cleaned_data['pt2_']
        roster.pw_x = form.cleaned_data['pw_']
        roster.iwb_x = form.cleaned_data['iwb_']
        roster.lt1_x = form.cleaned_data['lt1_']
        roster.lt2_x = form.cleaned_data['lt2_']
        roster.so_x = form.cleaned_data['so_']
        roster.hnso_x = form.cleaned_data['hnso_']
        roster.ptimer_x = form.cleaned_data['ptimer_']
        roster.nsoalt_x = form.cleaned_data['nsoalt_']

        roster.save()

        if request.POST.get('action', '').startswith('Commit'):
            return redirect('commit_event', event_id)
        else:
            messages.add_message(
                request, messages.INFO, 'Game roster has been saved.')
            return redirect('schedule_event', event_id)


class CommitScheduleView(View):
    """A view for committing officials for games."""
    template = 'udoco/commit_event.html'

    @method_decorator(login_required)
    def get(self, request, event_id):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()

        context = {
            'event': event,
            'email': render_to_string('email/scheduling_body.txt', {
                'event': event}),
        }
        return render(request, self.template, context)

    @method_decorator(login_required)
    def post(self, request, event_id):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()

        event.complete = True
        event.save()
        event = models.Game.objects.get(id=event.id)  # Refresh object

        with mail.get_connection() as connection:
            mail.EmailMessage(
                render_to_string(
                    'email/scheduling_title.txt',
                    {'event': event}),
                render_to_string(
                    'email/scheduling_body.txt',
                    {'event': event}),
                'United Derby Officials Colorado <no-reply@udoco.org>',
                ['United Derby Officials Colorado <no-reply@udoco.org>'],
                bcc=event.emails,
                connection=connection).send()

            # XXX: rockstar (25 Apr 2017) - The non-rostered emails were going
            # out incorrectly. Fix this.
            #mail.EmailMessage(
            #    render_to_string(
            #        'email/scheduling_title.txt',
            #        {'event': event}),
            #    render_to_string(
            #        'email/nonrostered_body.txt',
            #        {'event': event}),
            #    'United Derby Officials Colorado <no-reply@udoco.org>',
            #    ['United Derby Officials Colorado <no-reply@udoco.org>'],
            #    bcc=[user.email for user in event.nonrostered],
            #    connection=connection).send()
        messages.add_message(
            request, messages.INFO,
            'Schedule finalized and officials notified.')
        return redirect('view_event', event_id)


class ProfileView(View):
    """A view for viewing and editing a profile."""
    template = 'udoco/continue_signup.html'
    form = forms.ContinueSignUpForm

    @method_decorator(login_required)
    def get(self, request, form=None):
        display_name = request.user.display_name
        if len(display_name) is 0:
            display_name = '{} {}'.format(
                request.user.first_name, request.user.last_name)
        if form is None:
            form = self.form(initial={
                'display_name': display_name,
                'email': request.user.email,
                'game_history': request.user.game_history,
                'phone_number': request.user.phone_number,
                'emergency_contact_name': request.user.emergency_contact_name,
                'emergency_contact_number': request.user.emergency_contact_number,  # NOQA
                'league_affiliation': request.user.league_affiliation,
            })
        return render(request, self.template, {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            request.user.display_name = form.cleaned_data['display_name']
            request.user.email = form.cleaned_data['email']
            request.user.game_history = form.cleaned_data['game_history']
            request.user.phone_number = form.cleaned_data['phone_number']
            request.user.emergency_contact_name = form.cleaned_data['emergency_contact_name']  # NOQA
            request.user.emergency_contact_number = form.cleaned_data['emergency_contact_number']  # NOQA
            request.user.league_affiliation = form.cleaned_data['league_affiliation']  # NOQA
            request.user.save()
            messages.add_message(request, messages.INFO, 'Profile saved')
            return redirect(request.GET.get('next', 'profile'))
        else:
            return self.get(request, form=form)


class LeagueView(View):
    """A view for league management."""
    template = 'udoco/league_events.html'

    @method_decorator(login_required)
    def get(self, request):
        events = models.Game.objects.filter(
            league__in=request.user.scheduling.all(),
            start__gt=timezone.now()).order_by('start')

        context = {'events': events}
        return render(request, self.template, context)


class EditLeagueView(View):
    """A view for league management."""
    template = 'udoco/league.html'
    form = forms.LeagueEditForm

    @method_decorator(login_required)
    def get(self, request, form=None):
        if form is None:
            # XXX: rockstar (19 Sep 2016) - This only works for scheduler
            # who has access to a single league.
            league = request.user.scheduling.all()[0]
            form = self.form(initial={
                'league': league,
                'email_template': league.email_template
            })
            form.fields['league'].queryset = request.user.scheduling.all()

        return render(request, self.template, {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = self.form(request.POST)
        form.fields['league'].queryset = request.user.scheduling.all()
        if not form.is_valid():
            return self.get(request, form=form)

        league = form.cleaned_data['league']
        league.email_template = form.cleaned_data['email_template']
        league.save()
        messages.add_message(
            request, messages.INFO, 'League settings changed')
        return redirect('leagues')


class ContactLeaguesView(View):
    """Contact the league schedulers."""
    template = 'udoco/contact.html'
    form = forms.ContactOfficialsForm

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ContactLeaguesView, self).dispatch(
            request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request):
        officials = models.Official.objects.filter(scheduling__gte=1)

        context = {
            'form': self.form(),
            'officials': officials,
        }
        return render(request, self.template, context)

    @method_decorator(login_required)
    def post(self, request):
        officials = models.Official.objects.filter(scheduling__gte=1)

        form = self.form(request.POST)
        if not form.is_valid():
            return self.get(request, form=form)

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
        if request.GET.get('old', False):
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


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.League.objects.none()
    serializer_class = serializers.LeagueSerializer

    def list(self, request):
        if request.user.is_authenticated():
            queryset = request.user.scheduling.all()
        else:
            queryset = models.League.objects.none()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if not request.user.is_authenticated():
            raise Http404
        league = get_object_or_404(
            request.user.scheduling.all(), pk=pk)
        serializer = self.serializer_class(league)
        return Response(serializer.data)


class OfficialViewSet(viewsets.ModelViewSet):
    queryset = models.Official.objects.none()
    serializer_class = serializers.OfficialSerializer
    permissions = []

    def retrieve(self, request, pk=None):
        if not request.user.is_authenticated():
            raise Http404
        official = get_object_or_404(
            models.Official.objects.all(), pk=pk)
        serializer = self.serializer_class(official)
        return Response(serializer.data)

    def update(self, request, pk=None):
        if request.user.id != int(pk):
            raise Http404
        official = models.Official.objects.get(pk=pk)
        official.display_name = request.data['display_name']
        official.email = request.data['email']
        official.phone_number = request.data['phone_number']
        official.emergency_contact_name = request.data[
            'emergency_contact_name']
        official.emergency_contact_number = request.data[
            'emergency_contact_number']
        official.game_history = request.data['game_history']
        official.league_affiliation = request.data['league_affiliation']
        official.save()
        serializer = self.serializer_class(official)
        return Response(serializer.data)


class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Game.objects.filter(start__gt=datetime.now())
    serializer_class = serializers.GameSerializer

    def create(self, request):
        user = request.user
        if not user.is_authenticated() or user.league is None:
            raise Http404

        game = models.Game()
        game.title = request.data['title']
        game.location = request.data['location']
        game.league = user.league
        game.creator = user

        game.start = game.end = date_parser.parse(request.data['dateTime'])

        # This is temporary
        game.association = choices.AssociationChoices.OTHER
        game.game_type = choices.GameTypeChoices.OTHER
        game.save()

        serializer = self.serializer_class(
            game, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        if not request.user.is_authenticated():
            raise Http404
        event = self.queryset.get(pk=pk)
        if request.user not in event.league.schedulers.all():
            raise Http404

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

    def list(self, request):
        user = request.user
        if not user.is_authenticated() or user.league is None:
            raise Http404

        queryset = self.queryset.filter(league__in=user.scheduling.all())
        serializer = self.serializer_class(
            data=queryset, context={'request': request}, many=True)
        serializer.is_valid()
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Game.objects.filter(start__gt=datetime.now())
    serializer_class = serializers.GameSerializer

    def list(self, request):
        if not request.user.is_authenticated():
            raise Http404
        user = request.user
        rosters = models.Roster.objects.filter(
            Q(hr=user) | Q(ipr=user) | Q(jr1=user) | Q(jr2=user) |
            Q(opr1=user) | Q(opr2=user) | Q(opr3=user) | Q(alt=user) |
            Q(jt=user) | Q(sk1=user) | Q(sk2=user) | Q(pbm=user) |
            Q(pbt1=user) | Q(pbt2=user) | Q(pt1=user) | Q(pt2=user) |
            Q(pw=user) | Q(iwb=user) | Q(lt1=user) | Q(lt2=user) |
            Q(so=user) | Q(hnso=user) | Q(nsoalt=user) | Q(ptimer=user)
        )
        # TODO: Should we add in applications?
        queryset = self.queryset.filter(id__in=[r.game.id for r in rosters])
        serializer = self.serializer_class(
            data=queryset, context={'request': request}, many=True)
        serializer.is_valid()
        return Response(serializer.data)


class RosterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Roster.objects.none()
    serializer_class = serializers.RosterSerializer

    def list(self, request, event_pk=None):
        if not request.user.is_authenticated():
            raise Http404
        event = models.Game.objects.get(pk=event_pk)
        if request.user not in event.league.schedulers.all():
            raise Http404
        serializer = self.serializer_class(
            event.rosters.all(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, event_pk=None, pk=None):
        if not request.user.is_authenticated():
            raise Http404
        event = models.Game.objects.get(pk=event_pk)
        if request.user not in event.league.schedulers.all():
            raise Http404
        roster = event.rosters.get(pk=pk)
        serializer = self.serializer_class(roster)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = models.Official.objects.none()
    serializer_class = serializers.ApplicationSerializer

    def list(self, request, event_pk=None):
        if not request.user.is_authenticated():
            raise Http404
        event = models.Game.objects.get(pk=event_pk)
        if request.user not in event.league.schedulers.all():
            raise Http404
        officials = models.Official.objects.filter(
            applicationentries__in=event.applicationentries.all()
        ).distinct()
        context = {'event': event}
        serializer = serializers.ApplicationSerializer(
            officials, context=context, many=True)
        return Response(serializer.data)

    def create(self, request, event_pk=None):
        if not request.user.is_authenticated():
            raise Http404

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

    def delete(self, request, event_pk=None):
        if not request.user.is_authenticated():
            raise Http404

        event = models.Game.objects.get(pk=event_pk)
        if request.user not in event.applicants:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        models.ApplicationEntry.objects.filter(
            official=request.user, event=event).delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LoserApplicationViewSet(viewsets.ViewSet):
    queryset = models.Loser.objects.none()
    serializer_class = serializers.LoserApplicationSerializer

    def list(self, request, event_pk=None):
        if not request.user.is_authenticated():
            raise Http404
        event = models.Game.objects.get(pk=event_pk)
        if request.user not in event.league.schedulers.all():
            raise Http404
        losers = models.Loser.objects.filter(
            applicationentries__in=event.loserapplicationentries.all()
        ).distinct()
        context = {'event': event}
        serializer = serializers.LoserApplicationSerializer(
            losers, context=context, many=True)
        return Response(serializer.data)

    def create(self, request, event_pk=None):
        if request.user.is_authenticated():
            raise Http404
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
