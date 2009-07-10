from django.utils.safestring import mark_safe
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.template.loader import render_to_string
from django.utils.translation import ugettext_noop
import re

class DivErrorList(ErrorList):
    def __unicode__(self):    
        return self.always()
    
    def always(self):
        """
        even if no errors : make room for them
        prevents the 'jumpy' effet
        """
        if not self: return mark_safe(u'<div>&nbsp;</div>')
        return mark_safe(u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self]))

class BaseBlockForm(forms.BaseForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
             initial=None, error_class=DivErrorList, label_suffix=''):
        """
        use DivErrorList by default and no label suffix
        """
        forms.BaseForm.__init__(self, data, files, auto_id, prefix, 
             initial, error_class, label_suffix)

    def as_block(self):        
        "new display method to display errors after"
        return self._html_output(u'%(label)s<br />%(field)s<span class="formhelp">%(help_text)s</span>%(errors)s', u'%s<br />', '', u'<br />%s', False)

class BlockForm(BaseBlockForm):
    __metaclass__ = forms.forms.DeclarativeFieldsMetaclass
    
def alpha():
    tab = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    index = -1 
    while 1: 
        index += 1
        yield tab[index % len(tab)]

def cleanup_tox(input):
    input = input.replace('</h2>','')
    input = input.replace('<br />','')
    input = input.replace('<br/>','')
    numberator = alpha()
    input = re.sub('<h2>',lambda x:numberator.next()+ ". ",input)
    return input
    
def get_tou_txt():
    tou_html = render_to_string('static/tou_content.html')
    return cleanup_tox(tou_html)

def get_tos_txt():
    tos_html = render_to_string('static/tos_content.html')
    return cleanup_tox(tos_html)

# hardcoded names for translation
# _______________________________

ROLES_INFO = {
ugettext_noop("None"):[ugettext_lazy(u"no permission"),ugettext_lazy(u"text is private")], 
ugettext_noop("Observer"):[ugettext_lazy(u"read text"),ugettext_lazy(u"read comments")], 
ugettext_noop("Commenter"):[ugettext_lazy(u"read text"),ugettext_lazy(u"read and create comments")],
ugettext_noop("Moderator"):[ugettext_lazy(u"read text"),ugettext_lazy(u"read, create and moderate comments")],
ugettext_noop("Editor"):[ugettext_lazy(u"read and edit text"),ugettext_lazy(u"read, create and moderate comments")],
ugettext_noop("Owner"):[ugettext_lazy(u"read, edit and manage rights on text"),ugettext_lazy(u"read, create and moderate comments")],
}

SIMPLE_WORKFLOW_STATE_NAMES = [
_(u"pending"),
_(u"visible"),
_(u"published"),
_(u"rejected"),
               ]
RICH_WORKFLOW_STATE_NAMES = [
_(u"pending"),
_(u"visible"),
_(u"published"),
_(u"rejected"),
_(u"ignored"),
_(u"redundant"),
_(u"issue"),
_(u"oked"),
_(u"done"),
_(u"amendment"),
               ]