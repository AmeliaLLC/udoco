from django import forms
from django.utils.safestring import mark_safe

from udoco import choices, models, validators


class ContinueSignUpForm(forms.Form):
    display_name = forms.CharField(label='Derby name', max_length=100)
    game_history = forms.URLField(required=False)

    phone_number = forms.CharField(
        label='Phone number', max_length=16,
        validators=[validators.PHONE_NUMBER_VALIDATOR])

    emergency_contact_name = forms.CharField(
        label='Emergency Contact Name', max_length=256)
    emergency_contact_number = forms.CharField(
        label='Emergency Contact Number', max_length=16,
        validators=[validators.PHONE_NUMBER_VALIDATOR])


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

    TEXT = '''<script>
$('.datetimepicker').bootstrapMaterialDatePicker({
    format: 'YYYY-MM-DD HH:mm',
    shortTime: true,
    minDate: moment()
});
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
        label='First choice (Skating official)',
        required=False,
        choices=[(100, ' - ')] + list(choices.SkatingPositions.choices))
    so_second_choice = forms.ChoiceField(
        label='Second choice (Skating official)',
        required=False,
        choices=[(100, ' - ')] + list(choices.SkatingPositions.choices))
    so_third_choice = forms.ChoiceField(
        label='Third choice (Skating official)',
        required=False,
        choices=[(100, ' - ')] + list(choices.SkatingPositions.choices))

    nso_first_choice = forms.ChoiceField(
        label='First choice (Non-skating official)',
        required=False,
        choices=[(100, ' - ')] + list(choices.NonskatingPositions.choices))
    nso_second_choice = forms.ChoiceField(
        label='Second choice (Non-skating official)',
        required=False,
        choices=[(100, ' - ')] + list(choices.NonskatingPositions.choices))
    nso_third_choice = forms.ChoiceField(
        label='Third choice (Non-skating official)',
        required=False,
        choices=[(100, ' - ')] + list(choices.NonskatingPositions.choices))


class SchedulingForm(forms.Form):
    """Form for scheduling an event."""

    hr = forms.ModelChoiceField(
        label='Head Ref', empty_label='', queryset=None)
    ipr = forms.ModelChoiceField(
        label='Inside Pack Ref', empty_label='', queryset=None,
        required=False)
    jr1 = forms.ModelChoiceField(
        label='Jam Ref', empty_label='', queryset=None)
    jr2 = forms.ModelChoiceField(
        label='Jam Ref', empty_label='', queryset=None)
    opr1 = forms.ModelChoiceField(
        label='Outside Pack Ref', empty_label='', queryset=None,
        required=False)
    opr2 = forms.ModelChoiceField(
        label='Outside Pack Ref', empty_label='', queryset=None,
        required=False)
    opr3 = forms.ModelChoiceField(
        label='Outside Pack Ref', empty_label='', queryset=None,
        required=False)
    alt = forms.ModelChoiceField(
        label='Alternate', empty_label='', queryset=None,
        required=False)

    def __init__(self, qs, *args, **kwargs):
        super(SchedulingForm, self).__init__(*args, **kwargs)
        for label, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.queryset = qs
