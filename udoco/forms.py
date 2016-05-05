from django import forms

from udoco import choices


class ContinueSignUpForm(forms.Form):
    display_name = forms.CharField(label='Derby name', max_length=100)
    game_history = forms.URLField(required=False)


class AddEventForm(forms.Form):

    league = forms.CharField()
    title = forms.CharField()
    start = forms.DateTimeField()
    location = forms.CharField(max_length=1000)
    association = forms.ChoiceField(choices=choices.AssociationChoices.choices)
    game_type = forms.ChoiceField(choices=choices.GameTypeChoices.choices)

    def __init__(self, request, *args, **kwargs):
        super(AddEventForm, self).__init__(*args, **kwargs)
        self.fields['league'] = forms.ModelChoiceField(
            queryset=request.user.scheduling.all())


class GameApplicationForm(forms.Form):
    """Form for applying to officiate a game."""

    so_first_choice = forms.ChoiceField(choices=choices.SkatingPositions.choices)
    so_second_choice = forms.ChoiceField(choices=choices.SkatingPositions.choices)
    so_third_choice = forms.ChoiceField(choices=choices.SkatingPositions.choices)

    nso_first_choice = forms.ChoiceField(choices=choices.NonskatingPositions.choices)
    nso_second_choice = forms.ChoiceField(choices=choices.NonskatingPositions.choices)
    nso_third_choice = forms.ChoiceField(choices=choices.NonskatingPositions.choices)
