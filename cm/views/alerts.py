from cm.models import EmailAlert
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def emailalert_remove(request, key):
    text = EmailAlert.objects.delete_alert_by_key(key)
    redirect_to = reverse('index')
    if text : 
        request.session['message'] = _(u"You have been unsubscribed from the text '%(text_title)s'") %{'text_title' : text.get_latest_version().title}
    else :
        request.session['message'] = _(u"You have already been unsubscribed from the text") 
        
    return HttpResponseRedirect(redirect_to)
    
    