from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render, render_to_response
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View

from udoco import models
from udoco import forms


def splash(request):
    """A standard splash page."""
    if request.user.is_authenticated():
        return redirect('events')
    return render_to_response('udoco/splash.html')


def health_check(request):
    """A health check endpoint."""
    return HttpResponse('')


class EventsView(View):
    """A view for seeing all events."""
    # TODO: this should become a calendar view.

    template = 'udoco/events.html'

    @method_decorator(login_required)
    def get(self, request):
        admin_events = models.Game.objects.filter(
            league__in=request.user.scheduling.all(),
            start__gt=timezone.now()).order_by('start')

        events = models.Game.objects.filter(
            start__gt=timezone.now()).order_by('start')
        return render(request, self.template, {
            'events': events,
            'admin_events': admin_events,
            })


class AddEventView(View):
    """A view for adding a new event."""
    template = 'udoco/add_event.html'
    form = forms.AddEventForm

    def get(self, request):
        form = self.form()
        form.fields['league'].queryset = request.user.scheduling.all()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = self.form(request.POST)
        form.fields['league'].queryset = request.user.scheduling.all()
        if form.is_valid():
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

    def post(self, request, event_id):
        # XXX: rockstar (8 Sep 2016) - Emit an email notification
        # to applications that the event has been cancelled.
        event = models.Game.objects.get(id=event_id)
        event.delete()
        messages.add_message(request, messages.INFO, 'Game has been deleted.')
        return redirect('events')


class SchedulingView(View):
    """A view for scheduling officials for games."""
    template = 'udoco/schedule_event.html'

    def get(self, request, event_id, form=None):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()
        if form is None:
            initial = {}
            if event.roster is not None:
                initial = {
                    'hr': event.roster.hr,
                    'ipr': event.roster.ipr,
                    'jr1': event.roster.jr1,
                    'jr2': event.roster.jr2,
                    'opr1': event.roster.opr1,
                    'opr2': event.roster.opr2,
                    'opr3': event.roster.opr3,
                }
            form = forms.SchedulingForm(
                models.Application.objects.filter(game=event),
                initial=initial)
        context = {
            'form': form,
            'event': event,
            }
        return render(request, self.template, context)

    def post(self, request, event_id):
        event = models.Game.objects.get(id=event_id)
        if not event.can_schedule(request.user):
            raise Http404()
        form = forms.SchedulingForm(
            models.Application.objects.filter(game=event),
            request.POST)
        if form.is_valid():
            roster = models.Roster()
            roster.game = event
            roster.hr = form.cleaned_data['hr'].official
            try:
                roster.ipr = form.cleaned_data['ipr'].official
            except AttributeError:
                pass
            roster.jr1 = form.cleaned_data['jr1'].official
            roster.jr2 = form.cleaned_data['jr2'].official
            try:
                roster.opr1 = form.cleaned_data['opr1'].official
            except AttributeError:
                pass
            try:
                roster.opr2 = form.cleaned_data['opr2'].official
            except AttributeError:
                pass
            try:
                roster.opr3 = form.cleaned_data['opr3'].official
            except AttributeError:
                pass
            try:
                roster.alt = form.cleaned_data['alt'].official
            except AttributeError:
                pass
            roster.save()
            messages.add_message(
                request, messages.INFO, 'Game roster has been saved.')
            return redirect('view_event', event_id)
        else:
            return self.get(request, event_id, form=form)


class ProfileView(View):
    """A view for viewing and editing a profile."""
    template = 'udoco/continue_signup.html'
    form = forms.ContinueSignUpForm

    def get(self, request, form=None):
        display_name = request.user.display_name
        if len(display_name) is 0:
            display_name = '{} {}'.format(
                request.user.first_name, request.user.last_name)
        if form is None:
            form = self.form(initial={
                'display_name': display_name,
                'game_history': request.user.game_history,
                'phone_number': request.user.phone_number,
                'emergency_contact_name': request.user.emergency_contact_name,
                'emergency_contact_number': request.user.emergency_contact_number,
            })
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            request.user.display_name = form.cleaned_data['display_name']
            request.user.game_history = form.cleaned_data['game_history']
            request.user.phone_number = form.cleaned_data['phone_number']
            request.user.emergency_contact_name = form.cleaned_data['emergency_contact_name']
            request.user.emergency_contact_number = form.cleaned_data['emergency_contact_number']
            request.user.save()
            messages.add_message(request, messages.INFO, 'Profile saved')
            return redirect(request.GET.get('next', 'profile'))
        else:
            return self.get(request, form=form)
