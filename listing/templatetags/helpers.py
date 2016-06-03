import re
import types
from django.template import Library

register = Library()


@register.filter
def active_link(url, path):
    if url == path:
        return "pure-menu-active"
    return ""

def silence_without_field(fn):
    def wrapped(field, attr):
        if not field:
            return ""
        return fn(field, attr)
    return wrapped


def _process_field_attributes(field, attr, process):

    # split attribute name and value from 'attr:value' string
    params = attr.split(':', 1)
    attribute = params[0]
    value = params[1] if len(params) == 2 else ''

    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs, attribute, value)
        html = old_as_widget(widget, attrs, only_initial)
        self.as_widget = old_as_widget
        return html

    field.as_widget = types.MethodType(as_widget, field)
    return field


@register.filter("attr")
@silence_without_field
def set_attr(field, attr):

    def process(widget, attrs, attribute, value):
        attrs[attribute] = value

    return _process_field_attributes(field, attr, process)


@register.filter("add_error_attr")
@silence_without_field
def add_error_attr(field, attr):
    if hasattr(field, 'errors') and field.errors:
        return set_attr(field, attr)
    return field


@register.filter("append_attr")
@silence_without_field
def append_attr(field, attr):
    def process(widget, attrs, attribute, value):
        if attrs.get(attribute):
            attrs[attribute] += ' ' + value
        elif widget.attrs.get(attribute):
            attrs[attribute] = widget.attrs[attribute] + ' ' + value
        else:
            attrs[attribute] = value
    return _process_field_attributes(field, attr, process)


@register.filter("add_class")
@silence_without_field
def add_class(field, css_class):
    return append_attr(field, 'class:' + css_class)


@register.filter("add_error_class")
@silence_without_field
def add_error_class(field, css_class):
    if hasattr(field, 'errors') and field.errors:
        return add_class(field, css_class)
    return field


@register.filter("set_data")
@silence_without_field
def set_data(field, data):
    return set_attr(field, 'data-' + data)

@register.filter(name='field_type')
def field_type(field):
    """
    Template filter that returns field class name (in lower case).
    E.g. if field is CharField then {{ field|field_type }} will
    return 'charfield'.
    """
    if hasattr(field, 'field') and field.field:
        return field.field.__class__.__name__.lower()
    return ''


@register.filter(name='widget_type')
def widget_type(field):
    """
    Template filter that returns field widget class name (in lower case).
    E.g. if field's widget is TextInput then {{ field|widget_type }} will
    return 'textinput'.
    """
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and field.field.widget:
        return field.field.widget.__class__.__name__.lower()
    return ''
