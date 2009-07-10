from cm.models import user_has_perm_on_text, Text, number_has_perm_on_text
from django import template
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import re

register = template.Library()

class LocalTextPermsNode(template.Node):
    def __init__(self, user, text, perm_name, var_name):
        self.user = template.Variable(user)
        self.text = template.Variable(text)
        self.perm_name = perm_name
        self.var_name = var_name

    def render(self, context):
        ctype = ContentType.objects.get_for_model(Text)
        permission = Permission.objects.filter(content_type=ctype,codename=self.perm_name)[0]
        context[self.var_name] =  user_has_perm_on_text(self.user.resolve(context),
                                                        permission,
                                                        (self.text.resolve(context)).id)        
        return ''

@register.tag(name="get_local_text_perm")
def do_local_text_perm(parser, token):
    try:
        # Splitting by None == splitting by spaces.
        tag_name,arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) (.*?) (.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    user, text, perm_name, var_name = m.groups()
    #if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
    #    raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return LocalTextPermsNode(user, text, perm_name, var_name)

class NumberLocalTextPermsNode(template.Node):
    def __init__(self, text, perm_name, var_name):
        self.text = template.Variable(text)
        self.perm_name = perm_name
        self.var_name = var_name

    def render(self, context):
        ctype = ContentType.objects.get_for_model(Text)
        permission = Permission.objects.filter(content_type=ctype,codename=self.perm_name)[0]
        context[self.var_name] =  number_has_perm_on_text(permission,
                                                        (self.text.resolve(context)).id)        
        return ''

@register.tag(name="get_number_local_text_perm")
def do_number_local_text_perm(parser, token):
    try:
        # Splitting by None == splitting by spaces.
        tag_name,arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) (.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag_name
    text, perm_name, var_name = m.groups()
    #if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
    #    raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return NumberLocalTextPermsNode(text, perm_name, var_name)    