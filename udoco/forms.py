from django import forms


class ContactOfficialsForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
