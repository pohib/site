from django import template

register = template.Library()

@register.filter
def dot_format(value):
    return str(value).replace(',', '.')

@register.filter(name='mul')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value