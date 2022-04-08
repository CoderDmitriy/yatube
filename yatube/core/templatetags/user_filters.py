from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def addstyle(field, css):
    return field.as_widget(attrs={'style': css})
