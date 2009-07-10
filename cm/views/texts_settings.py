from cm.models import Profile,Text, State, Workflow, TextVersion, Role,ObjectUserRole, user_can_share_text, user_can_add_participant
from cm.security import local_text_permission_required 
from cm.utils.mail import EmailMessage
from cm.views import BaseBlockForm, BlockForm
from django import forms
from django.conf import settings as dj_settings
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext 
from django.template.context import get_standard_processors
from django.template.defaultfilters import urlencode
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.utils.translation import ungettext
from django.views.decorators.cache import cache_page
from django.views.generic.create_update import create_object,update_object
from django.views.generic.list_detail import object_detail,object_list
from itertools import groupby
import difflib,re
from django.db.models import Q
from cm.views import ROLES_INFO
from django.utils.translation import string_concat
import string

email_re = forms.fields.email_re

EMAIL_SEPARATOR = u"\n"
EMAIL_SEPARATORS = [u'\n',u' ',u',',u';']

EMAIL_EXAMPLE1 = ugettext_lazy(u'user1@example.com')
EMAIL_EXAMPLE2 = ugettext_lazy(u'user2@example.com')

def extract_tokens(stream,separator = EMAIL_SEPARATOR):
    res_tab = None
    if isinstance(separator,list):
        init_sep = separator[0]
        for the_sep in separator:
            stream = stream.replace(the_sep,init_sep)
        res_tab = stream.split(init_sep)
    else:
        res_tab = stream.split(separator)
    return set([o for o in map(unicode.strip,res_tab) if o])        
    
class MultipleEmailsField(forms.fields.CharField):
    
    def __init__(self, separator=EMAIL_SEPARATORS, max_length=None, min_length=None, *args, **kwargs):
        self.separator = separator
        self.max_length, self.min_length = max_length, min_length
        super(forms.fields.CharField, self).__init__(*args, **kwargs)
 
    def clean(self, value):
        pbs = []
        emails = extract_tokens(value,self.separator)
        for email in emails:
            if not email_re.search(email):
                pbs.append(email)
        if pbs:
            raise forms.util.ValidationError(_(u"the following items are not proper email addresses: %(emails)s") % {'emails':', '.join(pbs)})
        return value
        
DEFAULT_NEW_USER_ROLEID = 2
ROLE_CHECK_PREFIX = "role_"
ROLE_CHECK_RE = re.compile('^' + ROLE_CHECK_PREFIX + '(?P<key>\d+)') 
USER_ROLE_PREFIX = "role_choice_"
REMOVE_REMAIL_PREFIX = "select_"
REMOVE_REMAIL_RE = re.compile('^' + REMOVE_REMAIL_PREFIX + '(?P<key>\d+)') 
def get_people_involved_with_me(user, not_text_id):
        """ 
        returns users participating with me on texts
        exluding temp users
        """
        text_content_type = ContentType.objects.get_for_model(Text)
        # get texts'ids I'm involved in
        text_ids = set([r.object_id for r in ObjectUserRole.objects.filter(user__exact = user,
                                                          content_type = text_content_type,                                                          
                                                          ).exclude(object_id = not_text_id).distinct()])
        # people involved with the text
        exclude_user_ids = set([r.user_id for r in ObjectUserRole.objects.filter(
                                                          text = not_text_id,
                                                          user__isnull = False,                                                                                                                                                     
                                                          ).distinct()]).union(set([user.id]))

        users = User.objects.filter(objectuserrole__text__in = text_ids,
                                    profile__is_temp = False,
                                    is_active = True,
                                    ).exclude(id__in = exclude_user_ids).distinct()

        return users

class AddEmailsForm(forms.Form):
    new_emails = MultipleEmailsField(required=False,
                                     label= ugettext_lazy(u"Enter emails of people you want to share the text with (separated by comma, space, semicolon or carriage return)"),
                                     initial=string_concat(EMAIL_EXAMPLE1,EMAIL_SEPARATOR,EMAIL_EXAMPLE2),
                                     widget = forms.widgets.Textarea(attrs={'rows':3,'cols':40})
                                     )
    
    invite = forms.BooleanField(required=False,
                                label=ugettext_lazy(u'invite users'),
                                help_text=ugettext_lazy(u'Send an email to the users with a link to the text to notify them'),
                                )


    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
        initial=None, error_class=forms.util.ErrorList, label_suffix=':', user=None, text=None, local_roles=[], role_choices=[]):

        forms.Form.__init__(self, data, files, auto_id, prefix, initial, error_class, label_suffix)

        # dynamic fields that do not need to be dynamically set up
        self.fields['role_add'] = forms.ChoiceField(required=False,
                                 initial=DEFAULT_NEW_USER_ROLEID,
                                 label=ugettext_lazy(u'Choose role to assign'),
                                 choices= role_choices,
                                 widget = forms.widgets.Select(),
                                 )

        self.text = text
        users = get_people_involved_with_me(user,text.id)
        if users:
            new_users = forms.MultipleChoiceField(required=False,
                                                  label= _(u"... and/or select users among the ones with whom you already collaborate"),
                                                  choices=[(u.id, u.get_profile().display_name()) for u in users],
                                                  widget = forms.widgets.SelectMultiple(attrs={'size':3 }),
                                                  )
            self.fields['new_users'] = new_users

    def dynfields(self):
        return [self[name] for name, _ in self.fields.items() if name in self.dynnames]

    def clean(self):
        pbs = []
        if 'new_emails' in self.cleaned_data:
            emails = extract_tokens(self.cleaned_data['new_emails'],EMAIL_SEPARATORS)

            if 'new_users' not in self.fields.keys() or ([] == self.cleaned_data['new_users']):
                if not self.cleaned_data['new_emails'] :                
                    raise forms.util.ValidationError(_(u"please enter email adresses"))
                transEMAIL_EXAMPLE1 = EMAIL_EXAMPLE1.decode()
                transEMAIL_EXAMPLE2 = EMAIL_EXAMPLE2.decode()
                if transEMAIL_EXAMPLE1 in emails :
                    pbs.append(transEMAIL_EXAMPLE1)
                if transEMAIL_EXAMPLE2 in emails :
                    pbs.append(transEMAIL_EXAMPLE2)
                if pbs:
                    raise forms.util.ValidationError(_(u"please replace the following items with email addresses: %(emails)s") % {'emails':', '.join(pbs)})
        
            for email in emails:
                if ObjectUserRole.objects.filter(object_id__exact = self.text.id,
                                               content_type = ContentType.objects.get_for_model(Text),
                                               user__email__iexact=email).count() > 0:
                    pbs.append(email)
            if pbs:
                raise forms.util.ValidationError(_(u"these email addresses are already collaborating on the text: %(emails)s") % {'emails':', '.join(pbs)})
        
                            
        return self.cleaned_data

class RemoveReMailUsersForm(forms.Form):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
        initial=None, error_class=forms.util.ErrorList, label_suffix=':', local_roles=[]):

        forms.Form.__init__(self, data, files, auto_id, prefix, initial, error_class, label_suffix)

        for local_role in local_roles :
            if local_role.user_id :
                self.fields[REMOVE_REMAIL_PREFIX + str(local_role.user_id)] = forms.BooleanField(required=False)
                
class UsersRightsForm(forms.Form):
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
        initial=None, error_class=forms.util.ErrorList, label_suffix=':', user=None, text=None, 
        local_roles=[], role_anonymous_choices = [], role_choices=[], removeremailform = None):
        
        self.removeremailform = removeremailform 
        
        forms.Form.__init__(self, data, files, auto_id, prefix, initial, error_class, label_suffix)

        self.users_names = {}
        self.users_initial_roles = {}
        self.initial_role_id_others = 0
        for local_role in local_roles :
            if local_role.user_id :
                if local_role.user_id != user.id:
                    self.fields[ROLE_CHECK_PREFIX + str(local_role.user_id)] = forms.ChoiceField(required=False, 
                                                                             initial = local_role.role_id,
                                                                             choices= role_choices,
                                                                             widget = forms.widgets.Select(),
                                                                             )
                    self.users_names[str(local_role.user_id)] = local_role.user.get_profile().display_name()
                    self.users_initial_roles[str(local_role.user_id)] = local_role.role_id
            else :
                    self.initial_role_id_others = local_role.role_id
        
        self.fields['role_others'] = forms.ChoiceField(required=False,
                                 initial=self.initial_role_id_others,
                                 choices= role_anonymous_choices,
                                 widget = forms.widgets.Select(),
                                 )
    def dynfields(self):
        ret = []
        for name in self.fields.keys() :
            m = ROLE_CHECK_RE.match(name)
            if m:
                user_id = m.group('key')
                ret.append((user_id, 
                            self.users_names[user_id], 
                            self[name], 
                            self.users_initial_roles[user_id], 
                            self.removeremailform[REMOVE_REMAIL_PREFIX + user_id]))
        return ret

from cm.views.texts import INVITE_SEP

def get_value_from_matching_keys(data,regex, keyname, mapper = lambda x:x):
    res = set()
    for key,value in data.items():
        m = re.search(regex, key)
        if m:
            obj = mapper(m.group(keyname))
            res.add(obj)
    return res
    
def settings_settings(text,data,request):
    """
    returns : (form,httpreturn)
    if httpreturn != None : this is returned
    """
    if "settings.invite" in data:
        invitees = []
        for user_id in get_value_from_matching_keys(data,r'select_(?P<id>\d+)','id'):
            invitees.append(user_id)
        if invitees :
            invite_str = INVITE_SEP.join(invitees)
            invite_url = reverse('text-invite',args=[text.id,invite_str])
            return (None,HttpResponseRedirect(invite_url))            

    if "settings.delete" in data:
        # get deleted ids
        nb_deleted = 0
        
        user_ids_to_remove = get_value_from_matching_keys(data,r'select_(?P<id>\d+)','id',int)

        for user_id in user_ids_to_remove:
            nb_deleted += 1
            [d.delete() for d in ObjectUserRole.objects.filter(
                                                             object_id__exact = text.id,
                                                             content_type = ContentType.objects.get_for_model(Text),
                                                             user__exact = user_id
                                                             )]
        if nb_deleted:
            request.session['message'] = ungettext(u"%(number)s collaboration removed !", u"%(number)s collaborations removed !",  nb_deleted) %{'number': nb_deleted}
            

                
    if "settings.roles" in data:
        # 0 : prepare data : copy post data
        new_data = data.copy()
        
        # user_id --> role_id
        new_local_roles = dict([(k[len(ROLE_CHECK_PREFIX):],v) for k,v in new_data.items() if k.startswith(ROLE_CHECK_PREFIX)])
        
        for userid, roleid in new_local_roles.items() :
            if userid == u'others' :
                local_roles = ObjectUserRole.objects.filter(object_id__exact = text.id,
                                                      content_type = ContentType.objects.get_for_model(Text),
                                                      user__isnull=True
                                                      )
                if roleid == u'0' :
                    if local_roles and local_roles[0] :
                        local_roles[0].delete()
                    local_roles = [] # we're done
                elif not (local_roles and local_roles[0]) :
                    local_roles = ObjectUserRole.objects.create(object=text,role_id=roleid)
                    local_roles = [] # we're done
                    
            else :
                local_roles = ObjectUserRole.objects.filter(object_id__exact = text.id,
                                                      content_type = ContentType.objects.get_for_model(Text),
                                                      user__exact = userid
                                                      )
            if local_roles and local_roles[0] :
                local_roles[0].role_id = roleid
                local_roles[0].save() 
        request.session['message'] = _(u"Text settings updated.")

    settings_url = reverse('text-settings',args=[text.id])            
    return (None,HttpResponseRedirect(settings_url))            
    
def extract_roles_id(data):
    res = []
    for k,v in data.items():
        m = ROLE_CHECK_RE.match(k)
        if m:
            role_id = int(m.group('key'))
            res.append(role_id)
    return res
        
def send_notify_email(rec_user, sender_user, text) : #, row_level_role):
    site_url = dj_settings.SITE_URL
    site_name = dj_settings.SITE_NAME
    subject = render_to_string('texts/settings_notify_subject.html',
                               { 'site_url': site_url,
                                 'text' : text,
                                 })
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())

    message = render_to_string('texts/settings_notify_email.html',
                               {
# old invitation                 'activate_url' : reverse('activate-rl',args=[rec_user.get_profile().activation_key,row_level_role.id,sender_user.id]),
# new invitation                 
                                 'activate_url' : reverse('activate-t',args=[rec_user.get_profile().activation_key,text.id,sender_user.id]),
                                 'site_url': site_url,
                                 'text' : text,
                                 'site_name': site_name,
                                  })
    try:
        EmailMessage(subject, message, sender_user.email, [rec_user.email]).send()            
    except:
        return False
    return True

def settings_add(add_form, text,data,request, local_roles, role_choices):
    number_added = 0
    # bounding the form
    add_form = AddEmailsForm(data, user=request.user, text=text, local_roles=local_roles, role_choices=role_choices)
    if add_form.is_valid():
        # simple security check if user tries to trick us with tabs
        if not user_can_share_text(request.user, text) or not user_can_add_participant(request.user, text):
            settings_url = reverse('text-settings',args=[text.id])
            request.session['message'] = _(u"Nothing added ... please check.")                        
            return (None,HttpResponseRedirect(settings_url))            
        else:
            if not add_form.data.get('role_add', []) :
                add_form._errors[forms.forms.NON_FIELD_ERRORS] = forms.util.ErrorList([_(u"please check some role/permission to delegate to those new users")])
                return (add_form,None)
            # process new emails
            emails = extract_tokens(add_form.cleaned_data['new_emails'],EMAIL_SEPARATORS)
            transEMAIL_EXAMPLE1 = EMAIL_EXAMPLE1.decode()
            transEMAIL_EXAMPLE2 = EMAIL_EXAMPLE2.decode()
            if transEMAIL_EXAMPLE1 in emails :
                emails.remove(transEMAIL_EXAMPLE1)
            if transEMAIL_EXAMPLE2 in emails :
                emails.remove(transEMAIL_EXAMPLE2)
                 
            role_id = add_form.cleaned_data['role_add']
            # dont send many email to a single user
            notified_users = set()
            for email in emails:
                created,user = Profile.objects.invite_user(email)
                if not ObjectUserRole.objects.filter(object_id__exact = text.id,
                                                   content_type = ContentType.objects.get_for_model(Text),
                                                   user=user,
                                                   role=role_id).count():
                    row_level_role = ObjectUserRole.objects.create(object=text,user=user,role_id=role_id)
                    # invite only if sayed so OR if new users
                    if add_form.cleaned_data['invite'] or created:
                        if user not in notified_users: 
                            send_res = send_notify_email(user, request.user, text)
                            # error sending email : flag user
                            if not send_res:
                                profile = user.get_profile()
                                profile.is_mail_error = True
                                profile.save()
                            notified_users.add(user)                        
                    number_added += 1                        

            # process new users
            if 'new_users' in add_form.cleaned_data:
                new_users_id = add_form.cleaned_data['new_users']
                for new_user_id in new_users_id:
                    new_user = User.objects.get(pk = new_user_id) 
                    if not ObjectUserRole.objects.filter(object_id__exact = text.id,
                                                       content_type = ContentType.objects.get_for_model(Text),
                                                       user=new_user,
                                                       role=role_id).count():
                        row_level_role = ObjectUserRole.objects.create(object=text,user=new_user,role_id=role_id)
                    if add_form.cleaned_data['invite']:
                        if new_user not in notified_users: 
                            send_res = send_notify_email(new_user, request.user, text)
                            # error sending email : flag user
                            if not send_res:
                                profile = user.get_profile()
                                profile.is_mail_error = True
                                profile.save()                                
                            notified_users.add(new_user)                   
                    number_added += 1
    
            settings_url = reverse('text-settings',args=[text.id])
            if number_added:
                request.session['message'] = ungettext(u"%(number)s new collaboration added.", u"%(number)s new collaborations added.", number_added) % {'number':number_added}
                        
            return (None,HttpResponseRedirect(settings_url))            
    else:
        return (add_form,None)

from django.utils.functional import lazy

def richworkflow_a_priori():
    return u" | ".join([_(state.name) for state in State.objects.filter(workflow__id=4).exclude(id__in = (1,2))])

richworkflow_a_priori = lazy(richworkflow_a_priori, unicode)

def simpleworkflow_a_priori():
    return u" | ".join([_(state.name) for state in State.objects.filter(workflow__id=1).exclude(id__in = (1,2))])

simpleworkflow_a_priori = lazy(simpleworkflow_a_priori, unicode)

class ModForm(forms.Form):
    
    aprioriworkflow = forms.BooleanField(required=False,
                                label=ugettext_lazy(u'Should comments be approved to be public ?'),
                                widget=forms.widgets.RadioSelect(choices = [(1,ugettext_lazy(u"Yes")),(0, ugettext_lazy(u"No"))]),
                                )
    richworkflow = forms.BooleanField(required=False,
                                label=ugettext_lazy(u'Choose comment workflow:'),
                                widget=forms.widgets.RadioSelect(choices = [(0,simpleworkflow_a_priori()),
                                           (1, richworkflow_a_priori())]),
                                )


@local_text_permission_required('can_change_settings_local_text',must_be_logged_in=True)
def settings(request,text_id):
    text = get_object_or_404(Text,pk = text_id)
    version = text.get_latest_version()
    nb_pots = version.get_commentsandreplies_count()     

    local_roles = list(ObjectUserRole.objects.filter(user = None, object_id__exact = text.id,
                                            content_type = ContentType.objects.get_for_model(Text),
                                           )) 
    local_roles = local_roles + list(ObjectUserRole.objects.filter(object_id__exact = text.id,
                                            content_type = ContentType.objects.get_for_model(Text),
                                           ).order_by('-user')) 

    forbidden_anonymous_permission = Permission.objects.get(codename = 'can_manage_comment_local_text')
    forbidden_anonymous_roleids = [role.id for role in Role.objects.filter(permissions__id =forbidden_anonymous_permission.id)]
    roles = Role.objects.all().order_by('order')
    role_choices = [(role.id, _(role.name)) for role in roles]
    role_anonymous_choices = [(0, _("None"))] + [(role.id, _(role.name)) for role in roles if role.id not in forbidden_anonymous_roleids]
    roles_help = [(0, string_concat(ROLES_INFO["None"][0], "<br />",ROLES_INFO["None"][1]))]
    roles_help +=  [(role.id, string_concat(ROLES_INFO[role.name][0], "<br />",ROLES_INFO[role.name][1])) for role in roles]
                                           
    add_form = AddEmailsForm(initial={'invite':True}, user=request.user, text=text, local_roles=local_roles, role_choices=role_choices)
    remove_remail_form = RemoveReMailUsersForm(initial={'invite':True}, local_roles=local_roles)
    users_rights_form = UsersRightsForm(user=request.user, 
                                        local_roles=local_roles, 
                                        role_choices=role_choices, 
                                        role_anonymous_choices = role_anonymous_choices, 
                                        removeremailform = remove_remail_form)

    comment_workflow = version.comment_workflow
    if comment_workflow.id in [3, 1] :
        apriori = '1'
    else :
        apriori = '0'
        
    if comment_workflow.id in [3, 4] :
        rich = '1'
    else :
        rich = '0'
    mod_form = ModForm(initial = {'aprioriworkflow' : apriori,'richworkflow' : rich})
    
    form_dict = {}
    if request.method == 'POST':
        form_name = request.POST['form']
        all_post_data = request.POST.copy()
        del all_post_data["form"]
        if form_name == "settings":
            settings_form,response = settings_settings(text,all_post_data,request)
        elif form_name == "add":
            add_form,response = settings_add(add_form, text,all_post_data,request,local_roles,role_choices)            
        elif form_name == "mod":
            apriori = bool(int(request.POST['aprioriworkflow']))
            rich = bool(int(request.POST['richworkflow']))
            
            workflowid = -1
            if apriori :
                if rich :
                    workflowid = 3
                else :    
                    workflowid = 1
            else :    
                if rich :
                    workflowid = 4
                else :    
                    workflowid = 2
                    
            workflow = Workflow.objects.get(id=workflowid)
            
            version.change_workflow(workflow)
                
            settings_url = reverse('text-settings',args=[text.id])            
            response = HttpResponseRedirect(settings_url)
        if response:
            return response
    return render_to_response('texts/settings.html', 
                              {'role_choices': role_choices, 
                              'add_form': add_form,
                              'remove_remail_form': remove_remail_form,
                              'users_rights_form':users_rights_form,
                              'mod_form': mod_form,
                              'default_new_user_roleid':DEFAULT_NEW_USER_ROLEID,
                              'text' : text,
                              'has_comments': nb_pots > 0,
                              'is_rich': rich == '1',
                              'user_can_share_text' : user_can_share_text(request.user, text),
                              'max_shared_text_number' : request.user.get_profile().get_max_shared_number_text(),
                              'user_can_add_participant' : user_can_add_participant(request.user, text),
                              'roles_help' : roles_help,
                              'max_collaborators_text' : request.user.get_profile().get_max_collaborators_text(),
                              } , 
                              context_instance=RequestContext(request),
                              )
