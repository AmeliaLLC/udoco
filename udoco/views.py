from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, render_to_response
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
        events = models.Game.objects.all().order_by('start')
        return render(request, self.template, {'events': events})


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
        if event.official_can_apply(request.user) and form is None:
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
            form = self.form({
                'display_name': display_name,
                'game_history': request.user.game_history,
            })
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            request.user.display_name = form.cleaned_data['display_name']
            request.user.game_history = form.cleaned_data['game_history']
            request.user.save()
            messages.add_message(request, messages.INFO, 'Profile saved')
            return redirect('profile')
        else:
            return self.get(request, form=form)
