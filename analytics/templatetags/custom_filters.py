from django import template

register = template.Library()

@register.filter
def dot_format(value):
    return str(value).replace(',', '.')