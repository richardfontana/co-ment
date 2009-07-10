from cm.models import Profile,Text, TextVersion, Role,ObjectUserRole, Image,user_can_create_text, EmailAlert
from cm.security import local_text_permission_required 
from cm.utils.diff import text_diff
from cm.utils.mail import EmailMessage
from cm.views import BaseBlockForm, BlockForm
from cm.utils.commentPositioning import compute_new_comment_positions
from cm.views.client import so_get_occs
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
from django.utils.safestring import mark_safe
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.translation import ugettext_lazy
from django.views.decorators.cache import cache_page
from django.views.generic.create_update import create_object,update_object
from django.views.generic.list_detail import object_detail,object_list
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from itertools import groupby
from tagging.forms import TagField
import difflib,re
import datetime

    
def user(request,user_id):
    """
    texts from user user_id
    """
    user = get_object_or_404(User,pk = user_id)
    if user == request.user:
        creator = None
        exclude_all_have_perm = True        
    else:
        creator = user
        exclude_all_have_perm = False
    texts = Text.objects.get_by_perm(request.user, 'can_view_local_text', creator_user = creator, exclude_all_have_perm = exclude_all_have_perm).order_by('-id')
    if request.user.is_authenticated():
        text_max_number = request.user.get_profile().get_max_number_text()
    else:
        text_max_number = 0
        
        
    paginator = Paginator(texts, 10) # Show 25 contacts per page

#    texts2 = texts._clone()
#    paginator = Paginator(texts2,paginate_by)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pageobj = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pageobj = paginator.page(paginator.num_pages)
        
    texts_page_subset = pageobj.object_list
    for text in texts_page_subset :
        last_version = text.get_latest_version()
        nbcomments,nbreplies=last_version.get_visible_commentsandreplies_count(request.user)
        setattr(text,'nbcomments',nbcomments)
        setattr(text,'nbreplies',nbreplies)
    # TODO : 404 if not my workspace and not texts
    return render_to_response('texts/list.html', {
                           'texts' : texts_page_subset,
                           'watched_user'  : user,
                           'user_can_create_text'    : user_can_create_text(request.user),
                           'text_max_number' : text_max_number,                           
                           'paginator' : paginator,                           
                           'page' : pageobj,                           
                           },
                          context_instance=RequestContext(request))

from cm.utils.ooconvert import fmts

@local_text_permission_required('can_view_local_text')
def viewandcommentversion(request, text_id, embed = False, version_id=None):
    #get_object_or_404(TextVersion,pk = version_id)
    return _viewandcommentversion(request, text_id, embed, version_id)

@local_text_permission_required('can_view_local_text')
def so_viewandcommentversion(request, text_id, embed = False, version_id=None):
    return _viewandcommentversion(request, text_id, embed, version_id, so_b=True)

# so_ : static only    
def _viewandcommentversion(request, text_id, embed = False, version_id=None, so_b=False):
    text = get_object_or_404(Text,pk = text_id)
    alerts = []
    if not request.user.is_anonymous() :
        alerts = EmailAlert.objects.get_user_alerts(request.user, text) ;
    
    versions = text.get_versions()
    if version_id==None : # get latest
        version = versions[0]
    else :
        version = versions.get(id=version_id)

    export_formats = fmts.get_export_formats_tuple() 
    site_url = dj_settings.SITE_URL
    return render_to_response('texts/viewandcomment.html', 
                              {'version':version,
                               'versions':versions,
                               'embeded':embed, 
                               'mailsub':len(alerts)>0, 
                               'site_url': site_url,
                               'comment_workflow':version.comment_workflow,
                               'export_formats':export_formats,
                               'so_b':so_b,
                               }, 
                              context_instance=RequestContext(request)
                              )

class AddTextForm(BlockForm):

    title = forms.CharField(
                            label = ugettext_lazy(u"Title"),                        
                            max_length=100,
                            widget=forms.widgets.TextInput(attrs={'size' : 50}),
                            )
    content = forms.CharField(
                              label = ugettext_lazy(u"Content"),
                              widget=forms.Textarea(),
                              )

    tags = TagField(label=ugettext_lazy(u'Tags'),                                   
                           help_text= ugettext_lazy(u"separators are space and comma characters"),
                           widget=forms.widgets.TextInput(attrs={'size' : 50}),
                           max_length=250,required=False) # max_length ??

class EditTextCommentsForm(AddTextForm):
    create_new_version = forms.BooleanField(required=False, 
                             widget=forms.CheckboxInput(), 
                             label=ugettext_lazy(u'Create new version'), 
                             help_text= ugettext_lazy(u"versions are copies of your text that let you track and manages changes over time"),                             
                             )
    keep_comments = forms.BooleanField(required=False, 
                             widget=forms.CheckboxInput(), 
                             label=ugettext_lazy(u'Keep comments'),
                             help_text= ugettext_lazy(u"only comments on unchanged text will be preserved"),                             
                             )
    
    version_note = forms.CharField(
                                   label=ugettext_lazy(u'Version note'),
                                   help_text= ugettext_lazy(u"short description of the changes made (to appear in this document's history)"),
                                   widget=forms.widgets.TextInput(attrs={'size' : 50}),
                                   max_length=100,required=False)
    
@local_text_permission_required('can_edit_local_text',must_be_logged_in=True)
def edit(request,text_id):
    text = get_object_or_404(Text,pk = text_id)
    version = text.get_latest_version()
    nb_posts = text.get_latest_version().get_commentsandreplies_count()     
    if request.method == 'POST':
        form = EditTextCommentsForm(request.POST, initial = {'create_new_version': (nb_posts > 0)})
        if form.is_valid():
            data = form.cleaned_data
            
            create_new_version = data['create_new_version']
            keep_comments = ('keep_comments' in data) and data['keep_comments']
            
            if create_new_version :
                latest_version = text.get_latest_version()
                version = TextVersion.objects.duplicate(latest_version, request.user, keep_comments, keep_dates = False)
            else :
                version = text.get_latest_version()
                
            version.edit(new_title = data['title'], 
                         new_note = data['version_note'],
                         new_tags = data['tags'], 
                         new_content = data['content'],
                         keep_comments = keep_comments
                         )

            request.session['message'] = _(u"Text updated.")
            if 'continueediting' in request.POST and request.POST['continueediting'] == u'1':
                redirect_url = reverse('text-edit',args=[text.id])
            else:                                
                redirect_url = reverse('texts-user',args=[request.user.id])            
            return HttpResponseRedirect(redirect_url)
    else:
        initial = {'title':version.title,
                   'content':version.content,
                   'tags':version.tags, 
                   'keep_comments': True,
                   'create_new_version': (nb_posts > 0)}
        form = EditTextCommentsForm(initial = initial)
    return render_to_response('texts/edit.html', 
                              {'form': form,
                               'text': text,
                               'version':version,
                               'has_comments' : nb_posts != 0,
                               }, 
                              context_instance=RequestContext(request))


def diff_versions(request,rev_1_id,rev_2_id):
    rev_1 = get_object_or_404(TextVersion,pk = rev_1_id)
    rev_2 = get_object_or_404(TextVersion,pk = rev_2_id)
    #lines_1 = rev_1.content.split('\n')
    #lines_2 = rev_2.content.split('\n')    
    html = text_diff(rev_2.content,rev_1.content)
    #table = difflib.HtmlDiff().make_file(lines_1,lines_2,rev_1.title,rev_2.title)
    html = mark_safe(html)
    return render_to_response('texts/diff_versions.html', 
                              {
                               'html': html,
                               'rev_1': rev_1,
                               'rev_2': rev_2,                               
                                }, 
                              context_instance=RequestContext(request))
    
@local_text_permission_required('can_edit_local_text',must_be_logged_in=True)
def versions(request,text_id):
    if request.method == 'POST':
        rev_1_id = request.POST['o']
        rev_2_id = request.POST['i']
        diff_version_url = reverse('text-diffversions',args=[rev_1_id,rev_2_id])
        return HttpResponseRedirect(diff_version_url)

    text = get_object_or_404(Text,pk = text_id)
    versions = text.get_versions()
    
    more_than_two = versions.count() > 1
    for version in versions :
        nbcomments,nbreplies=version.get_visible_commentsandreplies_count(request.user)
        setattr(version,'nbcomments',nbcomments)
        setattr(version,'nbreplies',nbreplies)
    # TODO : 404 if not my workspace and not texts
    return render_to_response('texts/versions.html', {
                           'versions' : versions,
                           'text'  : text,
                           'more_than_two' : more_than_two,                           
                           },
                          context_instance=RequestContext(request))

@local_text_permission_required('can_view_local_text',must_be_logged_in=True)
@user_passes_test(lambda u: user_can_create_text(u),login_url = '/unauthorized')
def duplicate(request,text_id):
    text = get_object_or_404(Text,pk = text_id)
    new_text = Text.objects.duplicate(text, creator = request.user)
    version = new_text.get_latest_version()
    title = _(u"Copy of ") + version.title
    version.title = title
    version.save()
    request.session['message'] = _(u"Text duplicated.")
    workspace_url = reverse('texts-user',args=[request.user.id])            
    return HttpResponseRedirect(workspace_url)

@local_text_permission_required('can_delete_local_text',must_be_logged_in=True)
def delete(request,text_id):
    text = get_object_or_404(Text,pk = text_id)
    text.delete()
    request.session['message'] = _(u"Text deleted.")
    workspace_url = reverse('texts-user',args=[request.user.id])            
    return HttpResponseRedirect(workspace_url)            


class InviteForm(BlockForm):
    subject = forms.CharField(required=True,
                              label= ugettext_lazy(u"Subject"),
                              help_text= ugettext_lazy(u"enter the subject of the email"),
                              )
    
    body = forms.CharField(required=True,
                           label= ugettext_lazy(u"Email content"),
                           help_text= ugettext_lazy(u"enter the content of the email."),
                           widget = forms.widgets.Textarea(attrs={'rows':10,'cols':50})
                           )

    add_link = forms.BooleanField(required=False, 
                                  widget=forms.CheckboxInput(), 
                                  label=ugettext_lazy(u'Add a link to the text at the end of the email'), 
                                  )

INVITE_SEP = "."

@local_text_permission_required('can_change_settings_local_text',must_be_logged_in=True)
def invite(request,text_id,invite_str):
    text = get_object_or_404(Text,pk = text_id)
    users_ids = map(int,invite_str.split(INVITE_SEP))
    users = User.objects.filter(id__in = users_ids).distinct()
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():            
            subject_content = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            
            # send emails
            site_url = dj_settings.SITE_URL
            site_name = dj_settings.SITE_NAME
            subject = render_to_string('texts/settings_contact_subject.html',
                                       { 'subject': subject_content,
                                         })
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
                    
            sender_user = request.user 
            for rec_user in users:            
                # include link to text :
                # if account if temp : activation link
                # if not temp : direct access to the text
                link = ''
                if rec_user.get_profile().is_temp:
                    # old invitation 
                    # take the first role
                    #                    row_level_role = ObjectUserRole.objects.filter(user = rec_user, 
                    #                                                                   object_id = text.id,
                    #                                                                   content_type = ContentType.objects.get_for_model(Text),
                    #                                                                   )[0]
                    #                    link = reverse('activate-rl',args=[rec_user.get_profile().activation_key,row_level_role.id,sender_user.id])                    
                    # new invitation 
                    link = reverse('activate-t',args=[rec_user.get_profile().activation_key,text.id,sender_user.id])                    
                elif form.cleaned_data['add_link']:
                    link = reverse('text-viewandcomment',args=[text.id])
                
                message = render_to_string('texts/settings_contact_email.html',
                                           {
                                             'link_url' : link,
                                             'body' : body,
                                             'site_url': site_url,
                                             'site_name': site_name,
                                              })
        
                email = EmailMessage(subject, message, request.user.email, [rec_user.email])
                email.send()
        
            number_users = len(users)
            request.session['message'] = ungettext(u"%(number)s email sent.", u"%(number)s emails sent.", number_users) % {'number' : number_users}
        
            settings_url = reverse('text-settings',args=[text.id])   
            return HttpResponseRedirect(settings_url)
    else:
        form = InviteForm(initial={'add_link' : True})
    return render_to_response('texts/text_invite.html', {'form' : form, 'text': text, 'users' : users }, context_instance=RequestContext(request))

@user_passes_test(lambda u: user_can_create_text(u),login_url = '/unauthorized')
def add(request):
    if request.method == 'POST':
        form = AddTextForm(request.POST)
        if form.is_valid():
            # do it
            data = form.cleaned_data
            title = data['title']
            content = data['content']
            tags = data['tags']
            text = Text.objects.create_text(user=request.user, title=title, content=content, tags=tags)
            request.session['message'] = _(u"Text created.")
            if 'continueediting' in request.POST and request.POST['continueediting'] == u'1':
                redirect_url = reverse('text-edit',args=[text.id])
            else:                      
                redirect_url = reverse('texts-user',args=[request.user.id])            
            return HttpResponseRedirect(redirect_url)            
    else:
        form = AddTextForm()
    return render_to_response('texts/add.html', {'form': form, 'version':None }, context_instance=RequestContext(request))
    

@local_text_permission_required('can_view_local_text')
def version_content(request, version_id, so_b=False):
    version = get_object_or_404(TextVersion,pk = version_id)
    
    so_db = '' 
    if so_b : # need to add static only javascript 'client database' (so_)
        so_db = so_get_occs(version_id)
        
    return render_to_response('texts/version_content.html', 
                              {
                                 'version': version,
                                 'so_db' : so_db, 
                              }, 
                              context_instance=RequestContext(request))

@local_text_permission_required('can_edit_local_text',must_be_logged_in=True)
def revert_to_version(request, version_id):
    version = get_object_or_404(TextVersion,pk = version_id)
    new_version = TextVersion.objects.duplicate(version, version.creator, True, keep_dates = False)
    
    text_rev_url = reverse('text-versions',args=[version.text_id])            
    request.session['message'] = _(u"Reverted to version entitled %(version_title)s.") %{'version_title':version.title}
    return HttpResponseRedirect(text_rev_url)            
    

@local_text_permission_required('can_delete_local_version',must_be_logged_in=True)
def delete_version(request, version_id):
    version = get_object_or_404(TextVersion,pk = version_id)
    if version.text.get_versions_number() > 1:
        version.delete()
        request.session['message'] = _(u"version deleted")
    else:
        request.session['message'] = _(u"version not deleted")
    text_rev_url = reverse('text-versions',args=[version.text.id])            
    return HttpResponseRedirect(text_rev_url)            
    
@local_text_permission_required('can_edit_local_text',must_be_logged_in=True)
def precreate_version(request, version_id):
    previous_version = get_object_or_404(TextVersion,pk = version_id)
    comments = previous_version.comment_set.all() ;
    new_content = request.POST['content']
    create_new_version = request.POST['create_new_version']
    tomodify_comments, toremove_comments = compute_new_comment_positions(previous_version.content, new_content, comments)
    nb_removed = len(toremove_comments)    
    if create_new_version :
        message = ungettext("%(nb_removed)s comment will be removed because its underlying text has been changed. Do you want to continue ?",
                            "%(nb_removed)s comments will be removed because their underlying text has been changed. Do you want to continue ?", 
                            nb_removed) % {'nb_removed' : nb_removed}
    else :
        message = ungettext("%(nb_removed)s comment will be removed because its underlying text has been changed. Since you chose not to create a new version these comments will be definitely lost, do you want to continue ?",
                            "%(nb_removed)s comments will be removed because their underlying text has been changed. Since you chose not to create a new version these comments will be definitely lost, do you want to continue ?", 
                            nb_removed) % {'nb_removed' : nb_removed}
                
    return HttpResponse(simplejson.dumps({"warning_message" : message, 'nb_removed' : nb_removed }))
# heavy but only way to take permissions into account
@local_text_permission_required('can_view_local_text',must_be_logged_in=False)
def image(request, image_id):
    image = get_object_or_404(Image,pk = image_id)
    content = file(image.data.path).read()
    response = HttpResponse(content,'image/png')
    return response

@local_text_permission_required('can_view_local_text')
def version_css(request,version_id):
    version = get_object_or_404(TextVersion,pk = version_id)
    return HttpResponse(version.css,'text/css')