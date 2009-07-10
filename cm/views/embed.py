# -*- coding: utf-8 -*-
from cm.models import Profile,Text, TextVersion, Role,ObjectUserRole, Image,user_can_create_text, user_has_perm_on_text
from cm.utils.diff import text_diff
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.utils import feedgenerator
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from cm.security import local_text_permission_required
from django.template import RequestContext 
from cm.views.texts import _viewandcommentversion
from django.core.urlresolvers import reverse
from cm.models import user_has_perm_on_text
from cm.utils.ooconvert import combine_css_body

@local_text_permission_required('can_view_local_text',must_be_logged_in=False)
def page(request,text_id):
    site_url = settings.SITE_URL
    text = get_object_or_404(Text,pk = text_id)
    return render_to_response('embed/embed_page.html', 
                              {'text' : text,
                               'site_url' : site_url,
                               }, 
                              context_instance=RequestContext(request)
                              )

def embed(request,text_id,type):
    if user_has_perm_on_text(None, 'can_view_local_text', text_id):
        if type=="public_view" :
            return _viewandcommentversion(request,text_id,embed = True)
        else :#if type=="public_view_textonly" :
            text = get_object_or_404(Text,pk = text_id)
            version = text.get_latest_version()
            
            additional_commentsinfo_css = """
            .acinfo {
                padding:5px 10px 5px 10px;
                color:#222;
                font:normal 11px tahoma, arial, helvetica, sans-serif;
            }
            """
            nbcomments,nbreplies = version.get_visible_commentsandreplies_count(request.user)
            comment_count_msg = _(u'this text has %(nbcomments)d comment(s) and %(nbreplies)d reply(ies)') % {'nbcomments': nbcomments,'nbreplies': nbreplies,}            
            if user_has_perm_on_text(None, 'can_add_comment_local_text', text_id) :
                click_here_msg = _(u"click here to view or add comments") 
            else :
                click_here_msg = _(u"click here to view comments") 
            viewandcomment_url = settings.SITE_URL + reverse('text-viewandcomment',args=[text_id])
            additional_commentsinfo = u"""<div class="acinfo">co-ment®:&nbsp;%s,&nbsp;<a href="%s" target="blank" >%s</a>
            </div>""" % (comment_count_msg, viewandcomment_url, click_here_msg)
            
            body = "%s%s" % (version.content, additional_commentsinfo)
            css = "%s%s" % (additional_commentsinfo_css, version.css)
            
            content = combine_css_body(body,css)
            return HttpResponse(content)        
    else:
        redirect_url = reverse('embeded_unauthorized')
        return HttpResponseRedirect(redirect_url)
