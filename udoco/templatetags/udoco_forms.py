from django import forms, template

from udoco import models
from udoco.forms import DateTimePicker, SimplifiedLeagueSelect

MDLFORM_MAP = {
    forms.HiddenInput: {'class': ''},
    forms.Textarea: {
        'class': 'mdl-textfield__input'},
    forms.widgets.EmailInput: {
        'class': 'mdl-textfield__input'},
    forms.widgets.TextInput: {
        'class': 'mdl-textfield__input'},
    forms.widgets.Select: {
        'class': 'mdl-selectfield__select'},
    forms.widgets.URLInput: {
        'class': 'mdl-textfield__input'},
    SimplifiedLeagueSelect: {
        'class': 'mdl-selectfield__select'},
    DateTimePicker: {
        'class': 'mdl-textfield__input datetimepicker'},
}
register = template.Library()


@register.filter
def mdl(field):
    try:
        widget = field.field.widget
    except AttributeError:
        # Only happens on loserify. I don't understand django form
        # class api.
        widget = field.widget
    widget_type = type(widget)
    try:
        attrs = MDLFORM_MAP[widget_type]
        for key, val in attrs.items():
            widget.attrs[key] = val
    except KeyError:
        pass

    try:
        parent_class = widget.attrs['class'].split('__')[0]
        js_class = parent_class.replace('mdl-', 'mdl-js-')
        floating_label_class = '{}--floating-label'.format(parent_class)
        div_class = ' '.join([parent_class, js_class, floating_label_class])
        if len(field.errors):
            div_class = ' '.join([div_class, 'is-invalid'])
    except KeyError:
        parent_class = div_class = ''

    label_class = ''
    if parent_class:
        try:
            label_class = '__'.join([parent_class, 'label'])
        except KeyError:
            pass

    form_element = field.as_widget()
    label = field.label
    if "hidden" in form_element:
        # Don't show a label on a hidden form element.
        label = ''
    error = ''
    if len(field.errors) > 0:
        error = ' '.join([e for e in field.errors])
        error = '<span class="udoco-form-errors">{}</span>'.format(error)
    return '''
<div class="{div_class}">
<label for="{name}" class="{class}">{label}</label>
{form_element}
{errors}
</div>
'''.format(**{
        'name': field.name,
        'class': label_class,
        'form_element': form_element,
        'label': label,
        'div_class': div_class,
        'errors': error,
    })


@register.filter
def loserify(field):
    """Get the loser version of the same field."""
    loser_field = '{}_'.format(field.name)
    if loser_field not in field.form.fields:
        return None
    return field.form[loser_field]


@register.filter
def entries_in(official, event):
    if type(official) is models.Official:
        return models.ApplicationEntry.objects.filter(
            event=event, official=official).order_by('index')
    elif type(official) is models.Loser:
        return models.LoserApplicationEntry.objects.filter(
            event=event, official=official).order_by('index')
