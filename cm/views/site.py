from cm.models import Comment, TextVersion, Profile, Text
from cm.utils.cache import get_tag_cloud
from cm.utils.connections import register_mailman
from cm.utils.mail import EmailMessage
from cm.views import BaseBlockForm, BlockForm
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import mail_admins, send_mail
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import urlencode
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext as _, ugettext_lazy
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from tagging.utils import LOGARITHMIC
import feedparser


#from cm.views.accounts import DELAYED_REGISTRATION_SESSION_KEY

DELAYED_REGISTRATION_SESSION_KEY = 'registration_data'

def is_unattached_openid(request):
    if not settings.OPENID:
        return False
    if request.openid and request.openid.openid:
        from django_openidauth.models import UserOpenID, associate_openid        
        res = UserOpenID.objects.filter(openid=request.openid.openid)
        if res:
            # connected openid user exists: login user
            user = res[0].user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)            
            return False
        elif DELAYED_REGISTRATION_SESSION_KEY in request.session:
            # 1. create account previously registered
            # 2. associate with OpenID
            # 3. login
            
            # 1.
            data = request.session[DELAYED_REGISTRATION_SESSION_KEY]
            user = Profile.objects.create_inactive_user(data['username'],
                                 data['email'],
                                 data['password'],
                                 data['preferred_language'],
                                 send_email = False,
                                 )
            user.first_name = data['firstname']
            user.last_name = data['lastname']
            profile = user.get_profile() 
            profile.is_temp = False
            profile.save()
            
            # 2.
            associate_openid(user,request.openid)
            
            # 3.
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)                
        else:
            return True
    return False

def check_unattached_openid(request):
    if not request.user.is_anonymous():
        return None
    if is_unattached_openid(request) :
        request.session['message'] = _(u"You've successfully logged in with OpenId. Please complete your registration.")
        redirect_url = reverse('register')            
        return HttpResponseRedirect(redirect_url)        
    return None

def index(request):
    if settings.CUST_ALLOWREGISTRATION:
        response_openid_logged = check_unattached_openid(request)
        if response_openid_logged:
            return response_openid_logged
    return render_to_response('site/index.html', {}, context_instance=RequestContext(request))

def debug_trace(request):
    if request.method == 'POST':
        mail_admins('debug_trace', str(request.POST), fail_silently=True)
    return HttpResponse()

class SearchForm(BlockForm):    
    q = forms.CharField(
                            label = ugettext_lazy(u"search"),                        
                            max_length=100,
                            widget=forms.widgets.TextInput(attrs={'size' : 14}),
                            )
def unauthorized(request):
    resp = render_to_response('site/unauthorized.html', context_instance=RequestContext(request))
    resp.status_code = 403
    return resp

def embeded_unauthorized(request):
    resp = render_to_response('site/embeded_unauthorized.html', context_instance=RequestContext(request))
    resp.status_code = 403
    return resp

TOPIC_CHOICES = [
                ("feedback" , ugettext_lazy(u"General feedback") ),
                ("technical_pb" , ugettext_lazy(u"Technical problems")  ),
                ("pro" , ugettext_lazy(u"Professional services")  ),
                ("other" , ugettext_lazy(u"Other")  ), 
              ]

TOPIC_DICT = dict(TOPIC_CHOICES)

class HeaderContactForm(BlockForm):                 
    name = forms.CharField(
                           max_length=100, 
                           label= ugettext_lazy(u"Your name"),
                           )
    email = forms.EmailField(label= ugettext_lazy(u"Your email address"),)

class BodyContactForm(BlockForm):
    title = forms.CharField(label= ugettext_lazy(u"Subject of the message"),max_length=100)
    body = forms.CharField(label= ugettext_lazy(u"Body of the message"),widget=forms.Textarea)
    copy = forms.BooleanField(
                              label= ugettext_lazy(u"Send me a copy of the email"),                              
                              #help_text=ugettext_lazy(u"also send me a copy of the email"),                               
                              required=False)

class PartContactForm(HeaderContactForm):
    topic = forms.ChoiceField(
                              label= ugettext_lazy(u"Topic"),
                              help_text=ugettext_lazy(u"Please select a topic"), 
                                           choices = TOPIC_CHOICES)

class ContactForm(PartContactForm,BodyContactForm):
    pass

def contact(request):
    return contact_topic(request,None)

def contact_topic(request,topic_str):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = render_to_string('site/site_contact_email.html',
                                       {
                                         'body' : form.cleaned_data['body'],
                                         'name' : form.cleaned_data['name'],
                                         'email' : form.cleaned_data['email'],
                                         'topic' : form.cleaned_data['topic'],
                                         'referer' : request.META.get('HTTP_REFERER', None),
                                          })
            subject = form.cleaned_data['title']
            email = form.cleaned_data['email']
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            dest = settings.CONTACT_DEST
            EmailMessage(subject, message, email, [dest]).send()
            if form.cleaned_data['copy']:
                my_subject = _(u"Copy of message :") + u" " + subject
                EmailMessage(subject, message, email, [email]).send()
            request.session['message'] = _(u"Email sent. We will get back to you as quickly as possible.")                
            redirect_url = reverse('index')            
            return HttpResponseRedirect(redirect_url)
    else:        
        form = ContactForm()
        # use get parameter to specify topic (if any)
        if topic_str and topic_str in TOPIC_DICT:
            form = ContactForm(initial = {'topic' : topic_str})
    return render_to_response('site/contact.html', {'form': form}, context_instance=RequestContext(request))

def validLoginFormPost(request):
    from cm.views.accounts import LoginForm
    username = request.POST['username']
    password = request.POST['password']            
    user = authenticate(username=username, password=password)
    login(request, user)
    redirect_to = reverse('texts-user', args=[request.user.id])
    request.session['message'] = _(u"You've been logged in.")
    return HttpResponseRedirect(redirect_to)
