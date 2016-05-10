from django import forms, template

from udoco.forms import DateTimePicker, SimplifiedLeagueSelect

MDLFORM_MAP = {
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
    widget_type = type(field.field.widget)
    try:
        attrs = MDLFORM_MAP[widget_type]
        for key, val in attrs.items():
            field.field.widget.attrs[key] = val
    except KeyError:
        print(widget_type)
        pass

    try:
        parent_class = field.field.widget.attrs['class'].split('__')[0]
        if widget_type in (forms.widgets.Select,):
            parent_class = '{} {}'.format(
                parent_class, 'mdl-selectfield--floating-label')
        js_class = parent_class.replace('mdl-', 'mdl-js-')
        div_class = '{} {}'.format(parent_class, js_class)
    except KeyError:
        parent_class = div_class = ''

    label_class = ''
    if parent_class:
        try:
            label_class = '__'.join([parent_class, 'label'])
        except KeyError:
            pass

    form_element = field.as_widget()
    # XXX: rockstar (8 May 2016) - This is gross. Don't show a label
    # if the form item is a hidden element (in the case of
    # SimplifiedLeagueSelect.
    label = field.label
    if "hidden" in form_element:
        label = ''
    return '''
<div class="{div_class}">
<label for="{name}" class="{class}">{label}</label>
{form_element}
</div>
'''.format(**{
        'name': field.name,
        'class': label_class,
        'form_element': form_element,
        'label': label,
        'div_class': div_class,
        })
    return '<input type="" name="" value="" class="" />'
