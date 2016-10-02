from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.http import Http404
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View

from udoco import models
from udoco import forms


def splash(request):
    """A standard splash page."""
    if request.user.is_authenticated():
        return redirect('events')
    return render(request, 'udoco/splash.html', {})


class EventsView(View):
    """A view for seeing all events."""
    # TODO: this should become a calendar view.

    template = 'udoco/events.html'

    @method_decorator(login_required)
    def get(self, request):
        admin_events = models.Game.objects.filter(
            league__in=request.user.scheduling.all(),
            start__gt=timezone.now()).order_by('start')

        # XXX: rockstar (20 Sep 2016) - Since making Roster a
        # ForeignKey, this doesn't work.
        applications = models.Game.objects.filter(
            applications__in=models.Application.objects.filter(
                official=request.user),
            start__gt=timezone.now()).exclude(
            rosters__in=models.Roster.objects.all()).order_by('start')

        rosters = []
        rosters = models.Game.objects.filter(
            Q(rosters__hr=request.user) |
            Q(rosters__ipr=request.user) |
            Q(rosters__jr1=request.user) |
            Q(rosters__jr2=request.user) |
            Q(rosters__opr1=request.user) |
            Q(rosters__opr2=request.user) |
            Q(rosters__opr3=request.user)).filter(
            start__gt=timezone.now()).order_by('start')
        return render(request, self.template, {
            'rosters': rosters,
            'applications': applications,
            'admin_events': admin_events,
            })


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
    template = 'udoco/event.html'
    form = forms.GameApplicationForm

    def get(self, request, event_id, form=None):
        event = models.Game.objects.get(id=event_id)
        context = {
            'can_schedule': event.can_schedule(request.user),
            'event': event,
            'form': form,
            }
        if request.user.is_authenticated() \
                and event.official_can_apply(request.user) \
                and form is None:
            context['form'] = self.form()
        return render(request, self.template, context)

    @method_decorator(login_required)
    def post(self, request, event_id):
        event = models.Game.objects.get(id=event_id)
        if not event.official_can_apply(request.user):
            messages.add_message(
                request, messages.INFO, 'You cannot apply to this game.')
            return redirect('view_event', event_id)
        form = self.form(request.POST)
        if form.is_valid():
            application = models.Application()
            application.official = request.user
            application.game = event
            application.so_first_choice = form.cleaned_data['so_first_choice']
            application.so_second_choice = form.cleaned_data['so_second_choice']
            application.so_third_choice = form.cleaned_data['so_third_choice']
            application.nso_first_choice = form.cleaned_data['nso_first_choice']
            application.nso_second_choice = form.cleaned_data['nso_second_choice']
            application.nso_third_choice = form.cleaned_data['nso_third_choice']
            application.save()
            messages.add_message(
                request, messages.INFO, 'Your application has been received.')

            return redirect('view_event', event_id)
        else:
            return self.get(request, event_id, form=form)


class EventWithdrawalView(View):
    """A view for withdrawing a roster."""

    @method_decorator(login_required)
    def post(self, request, event_id):
        event = models.Game.objects.get(id=event_id)
        try:
            application = models.Application.objects.get(
                official=request.user, game=event)
            application.delete()
            messages.add_message(
                request, messages.INFO,
                'You have withdrawn from the event.')
            return redirect('events')
        except models.Application.DoesNotExist:
            raise Http404


class EventDeleteView(View):
    """A view for deleting events."""

    @method_decorator(login_required)
    def post(self, request, event_id):
        event = models.Game.objects.get(id=event_id)

        if event.complete:
            recipients = [user.email for user in event.staff]
        else:
            recipients = [application.official.email for application in event.applications.all()]
        with mail.get_connection() as connection:
            mail.EmailMessage(
                render_to_string(
                    'email/cancelled_title.txt',
                    {'event': event}),
                render_to_string(
                    'email/cancelled_body.txt',
                    {'event': event}),
                'United Derby Officials Colorado <no-reply@udoco.org>',
                recipients, connection=connection).send()

        event.delete()
        messages.add_message(request, messages.INFO, 'Game has been deleted.')
        return redirect('events')


class SchedulingView(View):
    """A view for scheduling officials for games."""
    template = 'udoco/schedule_event.html'

    @method_decorator(login_required)
    def get(self, request, event_id, form=None):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()

        blank_form = forms.SchedulingForm(
            models.Official.objects.filter(
                applications__in=models.Application.objects.filter(game=event)))
        if form is not None and form.cleaned_data['roster'] is None:
            blank_form = form

        roster_forms = []
        for roster in event.rosters.all():
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
            }
            roster_forms.append(forms.SchedulingForm(
                models.Official.objects.filter(
                    applications__in=models.Application.objects.filter(game=event)),
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

        form = forms.SchedulingForm(
            models.Official.objects.filter(
                applications__in=models.Application.objects.filter(game=event)),
            request.POST)
        if not form.is_valid():
            return self.get(request, event_id, form=form)

        if form.cleaned_data['roster']:
            roster = models.Roster.objects.get(id=form.cleaned_data['roster'])
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
        roster.save()

        if request.POST.get('action', '').startswith('Commit'):
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
                    [user.email for user in event.staff],
                    connection=connection).send()

                mail.EmailMessage(
                    render_to_string(
                        'email/scheduling_title.txt',
                        {'event': event}),
                    render_to_string(
                        'email/nonrostered_body.txt',
                        {'event': event}),
                    'United Derby Officials Colorado <no-reply@udoco.org>',
                    [user.email for user in event.nonrostered],
                    connection=connection).send()

        messages.add_message(
            request, messages.INFO, 'Game roster has been saved.')
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
                'emergency_contact_number': request.user.emergency_contact_number,
                'official_type': request.user.official_type,
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
            request.user.emergency_contact_name = form.cleaned_data['emergency_contact_name']
            request.user.emergency_contact_number = form.cleaned_data['emergency_contact_number']
            request.user.official_type = form.cleaned_data['official_type']
            request.user.league_affiliation = form.cleaned_data['league_affiliation']
            request.user.save()
            messages.add_message(request, messages.INFO, 'Profile saved')
            return redirect(request.GET.get('next', 'profile'))
        else:
            return self.get(request, form=form)


class LeagueView(View):
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
