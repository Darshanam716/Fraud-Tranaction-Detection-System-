from django import template

register = template.Library()

@register.filter
def getitem(form, field_name):
    return form[field_name]
