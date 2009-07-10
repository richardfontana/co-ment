from django import template

register = template.Library()

@register.filter
def in_list(value,arg):
    return value in arg

@register.filter
def in_dict(value,arg):
    return arg.get(value,None)


import sys
@register.filter
def int_display(value):
    if value == sys.maxint:
        return '-'
    else:
        return str(value)
int_display.is_safe = True

from django.utils.translation import ugettext as _
from django.utils.dateformat import format
from datetime import datetime
from time import struct_time
@register.filter
def local_date(value):
    """Formats a date according to the given local date format."""
    if not value:
        return u''    
    if isinstance(value,struct_time): 
        publication_date = datetime(value.tm_year,value.tm_mon,value.tm_mday,value.tm_hour,value.tm_min,value.tm_sec)
        value = publication_date
    arg = _(u"F j, Y \\a\\t g:i a") 
    return format(value, arg)
local_date.is_safe = False

from cm.views.public_texts import START_SEL_KEY,END_SEL_KEY
@register.filter
def replace_high(value):
    return value.replace(START_SEL_KEY,'<span class="strong">').replace(END_SEL_KEY,'</span>')
