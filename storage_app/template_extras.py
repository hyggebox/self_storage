from datetime import datetime
from django import template


register = template.Library()


@register.filter
def days_left(a_date):
    time_left = a_date - datetime.now().date()
    return time_left.days
