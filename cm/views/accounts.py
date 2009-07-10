from cm.models import Profile,ObjectUserRole,Text
from cm.utils.connections import register_mailman
from cm.utils.mail import EmailMessage
from cm.views import BaseBlockForm, BlockForm
from cm.views.site import HeaderContactForm,BodyContactForm
from django import forms
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.forms.util import ErrorList
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import urlencode
import base64
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.decorators.cache import cache_page
import re

@login_required
def logout_view(request):
    logout(request)
    # logout openid
    request.session['openids'] = []
    request.session['message'] = _(u"You've been logged out.")
    return HttpResponseRedirect("/")

class LoginForm(BlockForm):
    username = forms.CharField(label=ugettext_lazy(u"Username"),max_length=100)
    password = forms.CharField(label=ugettext_lazy(u"Password"),max_length=100, widget=forms.PasswordInput)
    
    def clean(self):
        if 'username' in self.cleaned_data and 'password' in self.cleaned_data:            
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise forms.ValidationError(_(u'User is not active yet. If you registered just now, please check your inbox and look for the activation email.'))
                return self.cleaned_data
            else:
                raise forms.ValidationError(_(u'Invalid username or password.'))
        else:
            return self.cleaned_data
    
def login_view(request):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']            
            user = authenticate(username=username, password=password)
            login(request, user)
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = reverse('texts-user', args=[request.user.id])
            request.session['message'] = _(u"You've been logged in.")
            return HttpResponseRedirect(redirect_to)
    else:
        form = LoginForm()
    return render_to_response('accounts/login.html', {'form': form} , context_instance=RequestContext(request))

LANGUAGES = [(code, ugettext_lazy(val)) for code, val in settings.LANGUAGES]

class BasicRegisterFormWithoutPw(BlockForm):
    """
    Structural registration form
    (without email existence checks [to be used by invitation confirmation view])
    """

    email = forms.EmailField(help_text=ugettext_lazy(u"your current email address (it will never be displayed)"), 
                             max_length=100)                                    
    username = forms.RegexField(
                                label=ugettext_lazy(u"Username"),
                                regex="^[a-zA-Z][a-zA-Z0-9_.]*$", 
                                min_length=4, 
                                max_length=32, 
                                error_message=ugettext_lazy(u"Use 4 to 32 characters and start with a letter. You may use letters, numbers, underscores, and one dot (.) but no accents."),
                                )
    firstname = forms.CharField(label=ugettext_lazy(u"First name"),required=False, max_length=100)
    lastname = forms.CharField(label=ugettext_lazy(u"Last name"),required=False, max_length=100)
    preferred_language = forms.ChoiceField(label=ugettext_lazy(u"Preferred language"),
                                           help_text=ugettext_lazy(u"this will be the language used by the site to communicate with you"), 
                                           choices = LANGUAGES)

    tos = forms.BooleanField(required=True,
                             widget=forms.CheckboxInput(), 
                             label=ugettext_lazy(u'I have read and agree to the Terms of Use'), 
                             )

    newsletter = forms.BooleanField(required=False,
                                    widget=forms.CheckboxInput(), 
                                    label=ugettext_lazy(u'Click here to subscribe to the (monthly) co-ment newsletter'))

    def clean_tos(self):
        """
        Forces true
        """
        if 'tos' in self.cleaned_data:
            tos = self.cleaned_data['tos']
            if not tos:
                raise forms.ValidationError(_(u'You must agree to the terms to register'))
            else:
                return tos
            
    def clean_username(self):
        """
        Validates that the supplied username is unique for the site.
        """
        if 'username' in self.cleaned_data:
            username = self.cleaned_data['username']
            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(_(u'This username is already in use. Please supply a different username.'))
           


 
class BasicRegisterForm(BasicRegisterFormWithoutPw):
    password = forms.CharField(label=ugettext_lazy(u"Password"),
                               max_length=100,
                               required=False,                                
                               help_text=ugettext_lazy(u"pick up a password"), 
                               widget=forms.PasswordInput)

    password2 = forms.CharField(label=ugettext_lazy(u"Password (repeat)"), 
                                help_text=ugettext_lazy(u"please repeat your password for confirmation"), 
                                max_length=100, 
                                required=False,
                                widget=forms.PasswordInput)
    
    if settings.OPENID:
        openid_url = forms.URLField(label=ugettext_lazy(u"OpenID"),
                                   help_text=ugettext_lazy(u"Fill this instead of the passwords above if you whish to use OpenID authentification"), 
                                   required=False,
                                   widget=forms.TextInput(attrs={'class':'openid', 'size':'40'})
                                   )
 
    forms.CharField(label=ugettext_lazy(u"Password (repeat)"), 
                                help_text=ugettext_lazy(u"please repeat your password for confirmation"), 
                                max_length=100, 
                                widget=forms.PasswordInput)
    
    def clean_openid_url(self):
        """
        Validates that the supplied openid url is unique for the site.
        """
        if 'openid_url' in self.cleaned_data:
            openid_url = self.cleaned_data['openid_url']
            if openid_url:
                try:
                    from django_openidauth.models import UserOpenID                    
                    user_openid = UserOpenID.objects.get(openid__startswith=openid_url)
                except UserOpenID.DoesNotExist:
                    return openid_url
                raise forms.ValidationError(_(u'This OpenID is already in use. Please supply a different one.'))
            else:
                return openid_url
        
    def clean(self):
        cleaned_data = self.cleaned_data
        # make sure usage or password OR OpenID
        if cleaned_data['password'] and 'openid_url' in cleaned_data and cleaned_data['openid_url']:
            msg = ugettext_lazy(u"Password and OpenID are filled, you should choose between the two authentification modes")
            self._errors["password"] = ErrorList([msg])
            del cleaned_data["password"]
            self._errors["openid_url"] = ErrorList([msg])
            del cleaned_data["openid_url"]
            
        elif cleaned_data['password'] or cleaned_data['password2']:            
            password = cleaned_data['password']
            password2 = cleaned_data['password2']
            if password != password2:
                msg = ugettext_lazy(_(u'Passwords do not match, please check.'))
                self._errors["password"] = ErrorList([msg])
                del cleaned_data["password"]
        else:
            if 'openid_url' not in cleaned_data or not cleaned_data['openid_url']:
                msg = ugettext_lazy(u"Please fill in the passwords")
                self._errors["password"] = ErrorList([msg])
                del cleaned_data["password"]                
                if settings.OPENID:
                    msg = ugettext_lazy(u"Please fill in the OpenID url (or the passwords above)")
                    if 'openid_url' not in self._errors: 
                        self._errors["openid_url"] = ErrorList([msg])
                    try:
                        del cleaned_data["openid_url"]
                    except:
                        pass
        return cleaned_data


    
#    def clean_password2(self):
#        if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:            
#            password = self.cleaned_data['password']
#            password2 = self.cleaned_data['password2']
#            if password != password2:
#                raise forms.ValidationError(_(u'Passwords do not match, please check.'))
#            else:
#                return password2
            
class RegisterFormWithoutPw(BasicRegisterFormWithoutPw):
    def clean_email(self):
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email']          
            try:
                user = User.objects.get(email__exact=email)
                if user.get_profile().is_temp:
                    return email
            except User.DoesNotExist:
                return email
            raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
    
    def clean_username(self):
        """
        Validates that the supplied username is unique for the site.
        """
        if 'username' in self.cleaned_data:
            username = self.cleaned_data['username']
            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(_(u'This username is already in use. Please supply a different username.'))
    
class RegisterForm(BasicRegisterForm):
    """
    Full registration form with full checks (username & email already exist)
    """

    def clean_email(self):
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email']          
            try:
                user = User.objects.get(email__exact=email)
                if user.get_profile().is_temp:
                    return email
            except User.DoesNotExist:
                return email
            raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
    
    def clean_username(self):
        """
        Validates that the supplied username is unique for the site.
        """
        if 'username' in self.cleaned_data:
            username = self.cleaned_data['username']
            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(_(u'This username is already in use. Please supply a different username.'))

from cm.views import get_tou_txt
from cm.views.site import is_unattached_openid


def register_view(request):
    next_activate = ''
    if request.method == 'POST':
        if is_unattached_openid(request):
            form = RegisterFormWithoutPw(request.POST)
        else:
            form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if is_unattached_openid(request):
                pw = ''
                send = False
            else:
                pw = data['password']
                send = True
            if 'openid_url' in data and data['openid_url']:
                # the user is registering with OpendID authentification
                request.session[DELAYED_REGISTRATION_SESSION_KEY] = data
                from django_openidconsumer.views import begin
                return begin(request, redirect_to = reverse('openid-complete'))
            else:
                # no OpenID:
                # - redirect from an OpenID login
                # - plain old register
                user = Profile.objects.create_inactive_user(data['username'], 
                                                              data['email'], 
                                                              pw, 
                                                              data['preferred_language'],
                                                              send_email = send,
                                                              next_activate = request.POST.get('next_activate',''),
                                                              )
                user.first_name = data['firstname']
                user.last_name = data['lastname']
                user.save()
                # newsletter
                if data['newsletter'] and settings.HAS_NEWSLETTER and not settings.DEBUG:
                    register_mailman(data['email'], settings.NEWSLETTER_ADR, data['username'])
                # opend id?
                if is_unattached_openid(request):
                    # activate user
                    profile = user.get_profile() 
                    profile.is_temp = False
                    profile.save()                
                    user.is_active = True
                    user.save()
                    # attach it
                    from django_openidauth.models import associate_openid
                    associate_openid(user,request.openid)
                    # login
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    request.session['message'] = _(u"OpenId Registration successful!")
                    return HttpResponseRedirect("/")            
                else:
                    request.session['message'] = _(u"Registration successful! Check your email to activate your account.")
                    return HttpResponseRedirect("/")            
    else:
        if 'django_language' in request.session:
            default_lang = request.session['django_language']
        elif request.LANGUAGE_CODE:
            default_lang = request.LANGUAGE_CODE
        else:
            default_lang = 'en'
        next_activate = request.GET.get("next_activate",'')
        if is_unattached_openid(request):
            form = RegisterFormWithoutPw(
                                initial={'preferred_language': default_lang}
                                )
        else:
            form = RegisterForm(
                                initial={'preferred_language': default_lang}
                                )
            
        
    TOU_TXT = get_tou_txt()
    return render_to_response('accounts/register.html', {'has_newsletter':settings.HAS_NEWSLETTER, 
                                                         'TOU_TXT':TOU_TXT, 
                                                         'form': form,
                                                         'next_activate': base64.b64encode(next_activate),
                                                         } , context_instance=RequestContext(request))

def activate_view_next(request,activation_key,next_activate):
    ret = activate_view(request, activation_key, None, None)
    redirect_to = base64.b64decode(next_activate)
    return HttpResponseRedirect(redirect_to)
    
def activate_view_rl(request, activation_key):
    return activate_view(request, activation_key, None, None)

def activate_view_t(request, activation_key, text_id, user_id):
    return activate_view(request, activation_key, None, user_id, text_id)

from cm.views.site import DELAYED_REGISTRATION_SESSION_KEY
# we used to put the row_level_role_id in the link inside the invitation mail 
# but there were bugs related to that (in perticular when a new version was created before user activation) 
# now we put the text id instead 
def activate_view(request, activation_key, row_level_role_id, user_id, text_id = None):
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    activated, user = Profile.objects.activate_user(activation_key)
    if user:
        if row_level_role_id and not text_id:# old invitations 
            rl = ObjectUserRole.objects.filter(content_type = ContentType.objects.get_for_model(Text),
                                               user__exact = user.id,)
            if len(rl) == 1 :  #in case of a click in the first mail after a sequence of invitation/removal/re-invitation use text.id to recover  
                text_id = rl[0].object_id
           
        if text_id: # new invitations
            rl = ObjectUserRole.objects.filter(object_id__exact = text_id,
                                               content_type = ContentType.objects.get_for_model(Text),
                                               user__exact = user.id,)
            if not rl  :
                return HttpResponseRedirect(reverse('unauthorized'))
            
            row_level_role_id = rl[0].id
            
        if row_level_role_id:
            inviter_user = get_object_or_404(User,pk = user_id)            
            row_level_role = get_object_or_404(ObjectUserRole,pk = row_level_role_id)
           
        if request.method == 'POST':
            form = BasicRegisterForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                openid_url = data.get('openid_url', None)
                if not openid_url:  
                    # non openid activation
                    user.username = data['username']
                    user.first_name = data['firstname']
                    user.last_name = data['lastname']
                    user.set_password(data['password'])
                    user.save()
                    profile = user.get_profile() 
                    profile.preferred_language = data['preferred_language']
                    profile.is_temp = False
                    profile.save()
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)                
                    request.session['message'] = _(u"Registration successful !")
                    if row_level_role_id:
                        # directly redirect to text
                        redirect_to = reverse('text-viewandcomment', args=[row_level_role.object.id])
                        return HttpResponseRedirect(redirect_to)                    
                    else:
                        return HttpResponseRedirect("/")
                else:
                    # open id activation
                    # 1. store registration data in session
                    # 2. redirect to openid authentification page
                    # 3. home page redirect will:
                    #    - detect the authentification
                    #    - create the user
                    #    - attach the new user to openid
                    #    - login the user
                    request.session[DELAYED_REGISTRATION_SESSION_KEY] = form.cleaned_data
                    from django_openidconsumer.views import begin
                    return begin(request, redirect_to = reverse('openid-complete'))
        else:
            form = BasicRegisterForm(initial={'email': user.email})            
            if not user.get_profile().is_temp:
                # hack : manual backend setting
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                if activated:
                    request.session['message'] = _(u"Welcome, your account has been activated.")
                if row_level_role_id:
                    # directly redirect to text
                    redirect_to = reverse('text-viewandcomment', args=[row_level_role.object.id])
                    return HttpResponseRedirect(redirect_to)                    
                else:
                    return HttpResponseRedirect("/")

        text = row_level_role.object
        # slightly modify form appearance
        form.fields['email'].help_text = _(u"this is the email which received the invitation (it will never be displayed on the site)")
        form.fields['email'].widget.attrs['readonly'] = 'readonly'
        TOU_TXT = get_tou_txt()
        return render_to_response('accounts/invitation_register.html', {'has_newsletter':settings.HAS_NEWSLETTER, 'TOU_TXT' : TOU_TXT, 'form': form, 'inviter_user' : inviter_user, 'text' : text} , context_instance=RequestContext(request))            
    else:
        request.session['message'] = _(u"Invalid activation key.")
        return HttpResponseRedirect("/")

class ProfileForm(BlockForm):
    email = forms.EmailField(
                             label=ugettext_lazy(u"Email"),
                             help_text=ugettext_lazy(u"your current email address (it will never be displayed)"), 
                             max_length=100)                                    
    username = forms.CharField(max_length=100, 
                               label=ugettext_lazy(u"Username"),
                               help_text=ugettext_lazy(u"this is your username on this site (it cannot be changed after registration)"), 
                               widget = forms.widgets.Input(attrs={'readonly':"readonly"}))
    firstname = forms.CharField(label=ugettext_lazy(u"First name"),required=False, max_length=100)
    lastname = forms.CharField(label=ugettext_lazy(u"Last name"),required=False, max_length=100)
    preferred_language = forms.ChoiceField(
                                           label=ugettext_lazy(u"Preferred language"),
                                           help_text=ugettext_lazy(u"this will be the language use by the site to communicate with you"), 
                                           choices = LANGUAGES)

    service_level = forms.CharField(max_length=100, required=False, 
                               label=ugettext_lazy(u"Service level"),
                               widget = forms.widgets.Input(attrs={'readonly':"readonly"}))

    allow_contact = forms.BooleanField(widget=forms.CheckboxInput(), 
                         label=ugettext_lazy(u"I welcome email contact from other site members"), 
                         help_text=ugettext_lazy(u"this will create a web contact form through which other users can contact you (your email won't be displayed)"), 
                         )

    # idea taken from:
    # http://www.b-list.org/weblog/2008/nov/09/dynamic-forms/
    # to be able to check against logged in user in clean email
    def __init__(self, user, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)
        self._user = user
    
    def clean_email(self):
        if 'email' in self.cleaned_data :
            email = self.cleaned_data['email']          
            username = self.data['username']          
            try:
                user = User.objects.get(email__exact=email)
            except User.DoesNotExist:
                return email
            me = User.objects.get(username__exact=username)
            if user == me and user == self._user: # user is same AND is logged in user
                return email
            raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
            
@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(user, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.email = data['email']
            user.first_name = data['firstname']
            user.last_name = data['lastname']
            user.get_profile().preferred_language = data['preferred_language']
            user.get_profile().allow_contact = data['allow_contact']
            user.save()
            user.get_profile().save()
            request.session['message'] = _(u"Profile updated.")
            workspace_url = reverse('texts-user', args=[request.user.id])
            return HttpResponseRedirect(workspace_url)
    else:                
        form = ProfileForm(user,
                           {'username': user.username, 
                           'email':user.email, 
                           'firstname':user.first_name, 
                           'lastname':user.last_name,
                           'allow_contact': user.get_profile().allow_contact, 
                           'preferred_language':user.get_profile().preferred_language, 
                           'service_level':user.get_profile().service_level, 
                           })
    return render_to_response('accounts/profile.html', {'form': form }, context_instance=RequestContext(request))

class PasswordResetForm(BlockForm):
    email = forms.EmailField(
                             label=ugettext_lazy(u"Your email address"),
                             max_length=100)                                    

def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = User.objects.get(email=data['email'])
                profile = user.get_profile()                
                site_url = settings.SITE_URL
                site_name = settings.SITE_NAME
    
                subject = render_to_string('accounts/password_reset_email_subject.html',
                                           { 'site_url': site_url })
                # Email subject *must not* contain newlines
                subject = ''.join(subject.splitlines())
    
                message = render_to_string('accounts/password_reset_email.html',
                                           { 
                                             'password_reset_url' : reverse('password-reset-real',args=[profile.activation_key]),
                                             'site_url': site_url,
                                             'site_name': site_name,
                                              })
    
                EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]).send()
                request.session['message'] = _(u"An email has been sent to you registration address, click on the link in this email to change your password.")
                return HttpResponseRedirect("/")    
            except User.DoesNotExist:
                request.session['message'] = _(u"This email is not registered on the site.")
                return HttpResponseRedirect("/")    
    else:
        form = PasswordResetForm()
    return render_to_response('accounts/password_reset.html', {'form': form }, context_instance=RequestContext(request))

class PasswordResetRealForm(BlockForm):
    password = forms.CharField(max_length=100, 
                               label=ugettext_lazy(u"Password"),
                               help_text=ugettext_lazy(u"pick up a password"), 
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label=ugettext_lazy(u"Password (repeat)"), 
                                help_text=ugettext_lazy(u"please repeat your password for confirmation"), 
                                max_length=100, 
                                widget=forms.PasswordInput)

    def clean_password2(self):
        if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:            
            password = self.cleaned_data['password']
            password2 = self.cleaned_data['password2']
            if password != password2:
                raise forms.ValidationError(_(u'Passwords do not match, please check.'))
            else:
                return password2

def password_reset_real_view(request,activation_key):
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    activated, user = Profile.objects.activate_user(activation_key)
    if user:           
        if request.method == 'POST':
            form = PasswordResetRealForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                user.set_password(password)
                user.save()
                request.session['message'] = _(u"Your password has been changed.")
                return HttpResponseRedirect("/")                      
        else:
            form = PasswordResetRealForm()
        return render_to_response('accounts/password_reset_real.html', {'form': form }, context_instance=RequestContext(request))
    else:
        request.session['message'] = _(u"Invalid activation key.")
        return HttpResponseRedirect("/")
    

class UserContactForm(BodyContactForm):
    pass

@login_required
def contact_user(request,user_id):
    contact_user = get_object_or_404(User,pk = user_id)
    contact_profile = contact_user.get_profile() 
    if not contact_profile.can_be_contacted():
        raise Http404
    if request.method == 'POST':
        form = UserContactForm(request.POST)
        if form.is_valid():
            message = render_to_string('accounts/user_contact_email.html',
                                       {
                                         'body' : form.cleaned_data['body'],
                                         'site_url': settings.SITE_URL,
                                         'site_name': settings.SITE_NAME,                                         
                                          })
            subject = form.cleaned_data['title']
            email = request.user.email
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            dest = contact_user.email
            EmailMessage(subject, message, email, [dest]).send()
            if form.cleaned_data['copy']:
                my_subject = _(u"Copy of message :") + u" " + subject
                EmailMessage(subject, message, email, [email]).send()
            
            request.session['message'] = _(u"Your message has been sent.")
            workspace_url = reverse('texts-user', args=[request.user.id])
            return HttpResponseRedirect(workspace_url)
    else:
        form = UserContactForm(initial = {
                                          'email':request.user.email,
                                          'name':request.user.get_profile().display_name(),
                                          })
        
    return render_to_response('accounts/contact_user.html', {'contact_user' : contact_user, 'form': form }, context_instance=RequestContext(request))
