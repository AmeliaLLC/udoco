from django import forms
from django.utils.safestring import mark_safe

from udoco import choices, models


class ContinueSignUpForm(forms.Form):
    display_name = forms.CharField(label='Derby name', max_length=100)
    game_history = forms.URLField(required=False)


class SimplifiedLeagueSelect(forms.widgets.Select):
    """A widget that changes appearance based on queryset data.

    This will render as a select box if there are more than one
    option to choose from. Otherwise, it will only show a single,
    readonly text box.
    """

    def render(self, name, value, attrs=None):
        if self.choices.queryset.count() > 1:
            return super(SimplifiedLeagueSelect, self).render(name, value, attrs)
        else:
            league = self.choices.queryset[0]
            return mark_safe(
                '<input name="{name}" type="hidden" value="{value}"/>{league}'.format(
                    **{
                        'league': league.name,
                        'name': name,
                        'value': league.id,
                    }))


class DateTimePicker(forms.widgets.DateTimeInput):
    """A DateTime picker.

    This uses the DateTime javascript picker from
    https://github.com/ripjar/material-datetime-picker
    """

    # TODO: rockstar (8 May 2016) - Fix this to work, likely requiring some
    # bullshit django-npm package.
    TEXT = '''<script>
/*
var MaterialDateTimePicker = require('material-datetime-picker');
var element = document.querySelector('.datetimepicker');
var picker = new MaterialDatePicker({
    el: element, openedBy: 'focus'
    });
*/
</script>
'''

    def render(self, name, value, attrs=None):
        val = super(DateTimePicker, self).render(name, value, attrs=None)
        return val + self.TEXT


class AddEventForm(forms.Form):

    league = forms.ModelChoiceField(
        queryset=models.League.objects.none(),
        widget=SimplifiedLeagueSelect)
    title = forms.CharField()
    start = forms.DateTimeField(widget=DateTimePicker)
    location = forms.CharField(max_length=1000)
    association = forms.ChoiceField(choices=choices.AssociationChoices.choices)
    game_type = forms.ChoiceField(choices=choices.GameTypeChoices.choices)


class GameApplicationForm(forms.Form):
    """Form for applying to officiate a game."""

    so_first_choice = forms.ChoiceField(
        label='First choice (skating official)',
        choices=choices.SkatingPositions.choices)
    so_second_choice = forms.ChoiceField(
        label='First choice (skating official)',
        choices=choices.SkatingPositions.choices)
    so_third_choice = forms.ChoiceField(
        label='First choice (skating official)',
        choices=choices.SkatingPositions.choices)

    nso_first_choice = forms.ChoiceField(
        label='First choice (skating official)',
        choices=choices.NonskatingPositions.choices)
    nso_second_choice = forms.ChoiceField(
        label='First choice (skating official)',
        choices=choices.NonskatingPositions.choices)
    nso_third_choice = forms.ChoiceField(
        label='First choice (skating official)',
        choices=choices.NonskatingPositions.choices)
