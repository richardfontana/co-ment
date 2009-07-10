from cm.models import Profile, Text, Comment, TextVersion, Role,ObjectUserRole, Image,user_can_create_text, user_has_perm_on_text
from cm.utils.diff import text_diff
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.utils import feedgenerator
from django.utils.translation import ugettext as _
from cm.security import local_text_permission_required
from django.template import RequestContext 

@local_text_permission_required('can_view_local_text',must_be_logged_in=False)
def page(request,text_id):
    text = get_object_or_404(Text,pk = text_id)
    return render_to_response('feeds/feed_page.html', 
                              {'text' : text}, 
                              context_instance=RequestContext(request)
                              )

@local_text_permission_required('can_change_settings_local_text',must_be_logged_in=True)
def reset(request,text_id):
    text = get_object_or_404(Text,pk = text_id)
    text.update_new_secret_key()
    request.session['message'] = _(u"The private feed URL has been reset.")    
    redirect_url = reverse('text-feeds',args=[text.id])            
    return HttpResponseRedirect(redirect_url)
    

# TODO : feed for user's text
# def user_text_feed(request, user_id, private_key):
#     user = get_object_or_404(User,pk = user_id)    
#     texts = Text.objects.get_by_perm(user, 'can_view_local_text', creator_user = user).order_by('-id')
    
def text_feed(request,text_id):
    if not user_has_perm_on_text(None, 'can_view_local_text', text_id):
        raise Http404 #HttpResponse(status=401)
    else:
        return _text_feed(request,text_id)
    
import time
import re
# taken from django's feedgenerator.py and changed to support multiple posts in minute
def get_tag_uri(url, date):
    "Creates a TagURI. See http://diveintomark.org/archives/2004/05/28/howto-atom-id"
    tag = re.sub('^http://', '', url)
    if date is not None:
        tag = re.sub('/', ',%s:/' % time.mktime(date.timetuple()), tag, 1)
    tag = re.sub('#', '/', tag)
    return u'tag:' + tag

def private_text_feed(request,text_id, private_key):
    text = get_object_or_404(Text,pk = text_id)
    # private key protection
    if text.secret_key and private_key == text.secret_key:
        return _text_feed(request,text_id, False)
    else:
        return HttpResponse(status=401)
    
def _text_feed(request,text_id, public_comments_only = True):    
    text = get_object_or_404(Text,pk = text_id)
    
    latest_version = text.get_latest_version()
    
    site_url = settings.SITE_URL
    text_url = site_url + reverse('text-viewandcomment',args=[text.id])
    creator_lang = text.creator.get_profile().preferred_language
    feed = feedgenerator.Atom1Feed(
        title=latest_version.title,
        link=text_url,
        description=_(u"Comments and edits for text '%(name)s'") %{'name':latest_version.title},
        language=creator_lang
    )    
    versions = text.get_versions()

    # compute new versions and comments
    for index in xrange(len(versions)):
        v_1 = versions[index] 

        if (public_comments_only) :  
            comments, dis = v_1.get_public_commentsandreplies()
        else :
            comments, dis = v_1.get_commentsandreplies()
        v_1_comments = list(comments.filter(created__gt = v_1.created))
        v_1_comments.extend(list(dis.filter(created__gt = v_1.created)))
        
        v_1_comments = sorted(v_1_comments, reverse = True, key = lambda x:x.created)

        # add comments _created_ on this version
        for comment in v_1_comments : #v_1.comment_set.filter(created__gt = v_1.created):
            if type(comment) == Comment:                
                feed_title = _(u"Comment added '%(title)s'") %{'title' : comment.title}
            else:
                feed_title = _(u"Reply to '%(comment_title)s' added: '%(title)s'") %{'comment_title' : comment.comment.title, 'title' : comment.title}
            feed_body = render_to_string('notifications/new_comment.html',
                                       { 'title': feed_title,
                                         'content': comment.content,
                                         })
            feed.add_item(title=feed_title,
                   link=text_url,
                   description=feed_body,
                   pubdate=comment.created,
                   unique_id = get_tag_uri(text_url, comment.created)
                   )

        if index!=len(versions)-1:
            v_2 = versions[index+1]            
            # Display html diff only is small (<=500) 
            html_diff = text_diff(v_2.content,v_1.content)
            if len(html_diff) > 500:
                html_diff = None
             
            if v_1.note:
                feed_title = _(u"New version created '%(version_note)s'" % {'version_note' : v_1.note})
            else:
                feed_title = _(u"New version created")
            
            feed_body = render_to_string('notifications/new_version.html',
                                       { 'SITE_URL' : settings.SITE_URL,
                                         'title': feed_title,
                                         'note' : html_diff,
                                         'version_url' : reverse('text-viewandcommentversion',args=[text.id, v_1.id]),                                          
                                         })
            feed.add_item(title=feed_title,
                   link=text_url,
                   description=feed_body,
                   pubdate= v_1.created,
                   unique_id = get_tag_uri(text_url, v_1.created)
                   )

    first_version = list(versions)[-1]
    feed_title = _(u"First version created")
    feed_body = render_to_string('notifications/new_version.html',
                               { 'SITE_URL' : settings.SITE_URL,
                                 'title': feed_title,
                                 'note' : first_version.note,
                                 'version_url' : reverse('text-viewandcommentversion',args=[text.id, first_version.id]),                                 
                                 })
    feed.add_item(title=feed_title,
           link=text_url,
           description=feed_body,
           pubdate= first_version.created,
           unique_id = get_tag_uri(text_url, first_version.created)
           )
    
    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, 'utf-8')
    return response

