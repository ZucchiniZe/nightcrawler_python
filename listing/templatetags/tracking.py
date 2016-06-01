from django import template

register = template.Library()


@register.filter
def was_read_by(obj, user):
    return obj.was_read_by(user)