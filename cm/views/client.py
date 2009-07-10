from cStringIO import StringIO
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.utils import simplejson
from django.conf import settings as dj_settings
from cm.models import *
from cm.security import local_text_permission_required 
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext 
from django.db import connection
from tagging.validators import is_tag_list    
from django.core.exceptions import ValidationError
from tagging.models import Tag
from  tagging.utils import LOGARITHMIC, calculate_cloud, parse_tag_input
from django.utils.translation import ugettext as _
from cm.lib.BeautifulSoup import BeautifulSoup
from cm.utils.spannifier import Spannifier
from cm.templatetags.cm_utils import local_date
from email.header import Header
from cm.utils.amender import Amender
from django.core.urlresolvers import reverse


class Occ :

    nbWord = 0
    
    startWord = 0

    endWord = 0

    def compute_color(self):
# this is the js code that is used client side to paint occurences, we'll do the same here
#    var max = 12 ;
#    var pp = (p > max) ? max : p ;
#    var n = 255 - Math.floor((145 / max) * pp) ;
#    var s = n.toString(16) ;
#    while (s.length < 2)
#        s = "0" + s ; 
#    return "#ff" + s + "9a"  ;
        max = 12
        if self.nbWord > max : 
            pp = max 
        else : 
            pp = self.nbWord
        s = hex(255 - ((145 / max) * pp)) ;
        return "#ff" + s[2:] + "9a"  ;
 
    def __init__(self,nbWord, startWord, endWord):
        self.nbWord = nbWord
        self.startWord = startWord
        self.endWord = endWord
        
    def __repr__(self):
        return self.toDict().__repr__()
    
    def __eq__(self, other):
        return self.nbWord == other.nbWord and self.endWord == other.endWord and self.startWord == other.startWord

    def __ne__(self, other):
        return not self.__eq__(other)

# http://docs.python.org/lib/module-time.html
def datetime_to_ms_str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") #str(1000*mktime(dt.timetuple()))

class ComplexEncoder(simplejson.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Comment) :
            if not hasattr(obj, 'discussion_count') :
                obj.discussion_count = 0
            ret = { 'id' : obj.id, 'tags' : ','.join(parse_tag_input(obj.tags)), 'state_id' : obj.state_id, 'discussion_count' : obj.discussion_count, 'created' : datetime_to_ms_str(obj.created), 'start_word' : obj.start_word, 'end_word' : obj.end_word, 'username' : obj.username, 'content':obj.content, 'title':obj.title}
            return ret
        
        if isinstance(obj, DiscussionItem) :
            ret = { 'id' : obj.id, 'tags' : ','.join(parse_tag_input(obj.tags)), 'state_id' : obj.state_id, 'created' : datetime_to_ms_str(obj.created), 'comment_id' : obj.comment.id, 'username' : obj.username, 'content':obj.content, 'title':obj.title}            
            return ret
        
        if isinstance(obj, Occ) :
            ret = {'nbWord' : obj.nbWord, 'startWord' : obj.startWord, 'endWord' : obj.endWord}
            return ret
        
        if isinstance(obj, Tag) :
            ret = { 'id' : obj.id, 'name' : obj.name, 'font_size' : obj.font_size}            
            return ret
        
        return simplejson.JSONEncoder.default(self, obj)
    
def client_exchange(request):
    if request.POST:
        functionName = request.POST['fun']# function called from client
        version_id = int(request.POST['versionId'])
#        from time import sleep
#        sleep(2)

        if functionName == 'getOccs' or functionName == 'getAttachsOnWord' or functionName == 'getAttachs' :
            if functionName == 'getOccs' :
                fromWord = int(request.POST['fromWord'])
                toWord = int(request.POST['toWord'])
                occs = None
                ret_comments = None
                ret = get_occs_protected(request, fromWord, toWord, version_id = version_id)
                if ret.__class__ != HttpResponseRedirect :
                    (occs, ret_comments) = ret
                return dumpItOrUnauthorized({"fromWord" : fromWord, "toWord" : toWord, "occs":occs, "attachs" : ret_comments}, ret)
                
            elif functionName == 'getAttachsOnWord' or functionName == 'getAttachs' :
                fromWord = -1
                toWord = -1
                if functionName == 'getAttachsOnWord' : 
                    fromWord = int(request.POST['word'])   
                    toWord = int(request.POST['word'])   
                comments = get_comments_protected(request, fromWord, toWord, "-created", version_id = version_id)
                return dumpItOrUnauthorized({"attachs" : comments}, comments)

        elif functionName == 'getTagCloud' :
            tags = get_tagcloud(request, version_id = version_id)
            return dumpItOrUnauthorized({"tags" : tags}, tags)
                
        elif functionName == 'addAttach' :
            title = request.POST['title']
            content = request.POST['content']
            tags = request.POST['tags']

            start_word = int(request.POST['start_word'])
            end_word = int(request.POST['end_word'])

            username = request.POST['username']
            email = request.POST['email']
            creatorId = None
            if not request.user.is_anonymous() :
                username = None
                email = None
                creatorId = request.user.id

            error = validate_tags(request, tags, version_id = version_id)

            if not error :
                comment = add_attach(request, creatorId, start_word, end_word, username, email, title, content, version_id = version_id)
                if comment :
                    comment.tags=tags
                    comment.save()
            return dumpItOrUnauthorized(comment, comment)
        
        elif functionName == 'getDiscussionItems' :
            attachId = int(request.POST['attachId'])
            discussionItems = get_discussion_items(request, [attachId], version_id = version_id)
            dis = discussionItems.get(attachId, [])
            return dumpItOrUnauthorized({"discussionItems" : dis}, dis)
        
        elif functionName == 'validateTags':
            tags = request.POST['tags']

            error = validate_tags(request, tags, version_id = version_id)
            return dumpItOrUnauthorized(error, error)
            
        elif functionName == 'addDiscussionItem' :
            username = request.POST['username']
            email = request.POST['email']
            creatorId = None
            if not request.user.is_anonymous() :
                username = None
                email = None
                creatorId = request.user.id

            title = request.POST['title']
            content = request.POST['content']
            attachId = int(request.POST['comment_id'])
            tags = request.POST['tags']
            
            error = validate_tags(request, tags, version_id = version_id)
            if not error : # TODO check that  .__class__ != HttpResponseRedirect here
                discussionItem = add_discussion_item(request, attachId, creatorId, username, email, title, content, version_id = version_id)
                if discussionItem :
                    discussionItem.tags=tags
                    discussionItem.save()
                return dumpItOrUnauthorized(discussionItem, discussionItem)
        
        elif functionName == 'updateDiscussionItemState' :
            discussionitemId = int(request.POST['discussionitem_id'])
            stateId = int(request.POST['state_id'])
            discussionitem = update_discussionitem_state(request, discussionitemId, stateId, version_id = version_id)
            return dumpItOrUnauthorized({"discussionitem" : discussionitem}, discussionitem)

        elif functionName == 'updateAttachState' :
            attachId = int(request.POST['comment_id'])
            stateId = int(request.POST['state_id'])
            attach = update_attach_state(request, attachId, stateId, version_id = version_id)
            return dumpItOrUnauthorized({"attach" : attach}, attach)

        elif functionName == 'editAttach' :
            attachId = int(request.POST['comment_id'])
            isReply = request.POST['is_reply'] == '1'
            title = request.POST['title']
            content = request.POST['content']
            tags = request.POST['tags']
            start_word = int(request.POST['start_word'])
            end_word = int(request.POST['end_word'])
            
# special case of rights check inside the function : 
# authors of comments have the right to remove their own comments although not having global 'can_manage_comment_local_text' permission on text
            right_passed = False
            if isReply :
                di = DiscussionItem.objects.get(id=attachId)
                if di :
                    right_passed = di.canAuthorEdit(request.user)
            else :
                comment = Comment.objects.get(id=attachId)
                if comment :
                    right_passed = comment.canAuthorEdit(request.user)
            if right_passed :
                attach = non_protected_edit_attach(request, attachId, isReply, title, content, start_word, end_word,version_id = version_id)
            else :            
                attach = edit_attach(request, attachId, isReply, title, content, start_word, end_word,version_id = version_id)
            
            if attach and attach.__class__ != HttpResponseRedirect :
                attach.tags=tags
                attach.save()
                
            type = "attach"
            if isReply :
                type = "discussionitem"
            return dumpItOrUnauthorized({type : attach}, attach)

        elif functionName == 'deleteAttach' :
            attachId = int(request.POST['comment_id'])
# special case of rights check inside the function : 
# authors of comments have the right to remove their own comments although not having global 'can_manage_comment_local_text' permission on text
            right_passed = False
            comment = Comment.objects.get(id=attachId)
            if comment :
                right_passed = comment.canAuthorEdit(request.user)
            if right_passed :
                retCode = non_protected_del_attach(request, attachId, version_id = version_id)
            else :            
                retCode = del_attach(request, attachId, version_id = version_id)
            return dumpItOrUnauthorized({"attachId" : attachId}, retCode)

        elif functionName == 'deleteDiscussionItem' :
            discussionItemId = int(request.POST['discussionitem_id'])
# special case of rights check inside the function :
            right_passed = False
            di = DiscussionItem.objects.get(id=discussionItemId)
            if di :
                right_passed = di.canAuthorEdit(request.user)
            if right_passed :
                retCode = non_protected_del_discussionitem(request, discussionItemId, version_id = version_id)
            else :            
                retCode = del_discussionitem(request, discussionItemId, version_id = version_id)
            return dumpItOrUnauthorized({"discussionItemId" : discussionItemId}, retCode)
    
        elif functionName == 'applyAmendments' :
            retCode, location, success_message = apply_amendments(request, version_id = version_id)
            return dumpItOrUnauthorized({"location":location, "success_message":success_message}, retCode)
        
        elif functionName == 'mailSubscribe' :
            do_subscribe = request.POST['mailsub'] == '1'
            retCode, new_sub, success_message = mail_subscribe(request, do_subscribe, version_id = version_id)
            return dumpItOrUnauthorized({"new_sub":new_sub, "success_message":success_message}, retCode)

    return HttpResponse(simplejson.dumps({}))

def dumpItOrUnauthorized(obj, rr):
    if rr.__class__ == HttpResponseRedirect :
        ret = HttpResponse(simplejson.dumps({}))
        ret.status_code = 403
        return ret
    else :
        return HttpResponse(simplejson.dumps(obj, cls=ComplexEncoder))

#keep the version_id parameter for rights checking in decorator
@local_text_permission_required('can_add_comment_local_text')
def add_discussion_item(request, attachId, creatorId, username, email, title, content, version_id):
    allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', request.user, version_id)
    
    comment = Comment.objects.get(id=attachId)
    discussionItem, object_state = DiscussionItem.objects.create_discussionitem(comment, creatorId, title, content, username, email)
    
    if object_state.state in allowed_states :
        if creatorId != None :
            creator = User.objects.get(id=creatorId)
            discussionItem.username = creator.username
        setattr(discussionItem, 'state_id', object_state.state_id)
        return discussionItem 
    else :
        return None

@local_text_permission_required('can_add_comment_local_text')
def add_attach(request, creatorId, start_word, end_word, username, email, title, content, version_id):
    allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', request.user, version_id)

    comment, object_state = Comment.objects.create_comment(creatorId, start_word, end_word, username, email, title, content, version_id)
    
    if object_state.state in allowed_states :
        if creatorId != None :
            creator = User.objects.get(id=creatorId)
            comment.username = creator.username
        setattr(comment, 'state_id', object_state.state_id)
        return comment
    else :
        return None
    
    
def wrap_to_clientattach(request, comment, version_id):
    allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', request.user, version_id)
    discussion_item_content_type_id = ContentType.objects.get_for_model(DiscussionItem).id
    allowedStateDiscussionItemCond = """AND "d_objectstate"."state_id" in (%s) AND "d_objectstate"."content_type_id" = %s """ % (",".join([str(t.id) for t in allowed_states]), discussion_item_content_type_id)
    cursor = connection.cursor()
    rows = []
    sql = """SELECT "cm_comment"."id",
                        "cm_comment_creator"."username",
                        (SELECT COUNT(*) FROM "cm_discussionitem" as "d" 
                            INNER JOIN "cm_objectstate" AS "d_objectstate" ON "d"."id" = "d_objectstate"."object_id" 
                        WHERE "d"."comment_id" = "cm_comment"."id" """ + allowedStateDiscussionItemCond + """),                                
                        "cm_comment_objectstate"."state_id"
            FROM "cm_comment" 
                INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
                LEFT OUTER JOIN "auth_user" AS "cm_comment_creator" ON "cm_comment"."creator_id" = "cm_comment_creator"."id" 
            WHERE "cm_comment"."id" = %s""" % comment.id
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows :
        r = rows[0]
        if comment.creator_id != None :
            comment.username = r[1]
        setattr(comment, 'discussion_count', r[2])
        setattr(comment, 'state_id', r[3])
    return comment

@local_text_permission_required('can_manage_comment_local_text')
def edit_attach(request, attach_id, isreply, title, content, start_word, end_word, version_id):
    return non_protected_edit_attach(request, attach_id, isreply, title, content, start_word, end_word, version_id)

def non_protected_edit_attach(request, attach_id, isreply, title, content, start_word, end_word, version_id):
    if isreply :
        t = DiscussionItem.objects.get(id = attach_id)
    else :
        t = Comment.objects.get(id = attach_id)
        if not start_word == -1 : # that means attach scope has been modified 
            prev_start_word = t.start_word
            prev_end_word = t.end_word
            t.start_word = start_word 
            t.end_word = end_word
    t.title = title 
    t.content = content
    t.save()
    if isreply :
        setattr(t, 'state_id', t.states.get().state_id)
    else :
        t = wrap_to_clientattach(request, t, version_id)
        
    return t

@local_text_permission_required('can_manage_comment_local_text')
def update_discussionitem_state(request, discussionitem_id, state_id, version_id):
    new_state = State.objects.get(id=state_id)
    discussionitem = DiscussionItem.objects.get(id = discussionitem_id)
    object_state = discussionitem.update_state(new_state)
    setattr(discussionitem, 'state_id', object_state.state_id)
    return discussionitem

@local_text_permission_required('can_manage_comment_local_text')
def update_attach_state(request, attach_id, state_id, version_id):
    new_state = State.objects.get(id=state_id)
    comment = Comment.objects.get(id = attach_id)
    object_state = comment.update_state(new_state)
    attach = wrap_to_clientattach(request, comment, version_id)
    return attach

@local_text_permission_required('can_edit_local_text')
def apply_amendments(request, version_id):
     location = "#"
     
     text_version = TextVersion.objects.get(id=version_id)
     spanned_content = text_version.get_spanned_content()
     
     # looking for comments with amendment state :
     amendment_comments, amendment_dis = text_version.get_amendments() 
     amendments = [(comment.start_word, comment.end_word, comment.content) for comment in amendment_comments] 
     amendments.extend([(di.comment.start_word, di.comment.end_word, di.content) for di in amendment_dis])

     if amendments :
         # apply amendments to compute new spanned content
         amender = Amender()
         modified_spanned_content = amender.amend(spanned_content, amendments)
    
         # unspan new content
         spannifier = Spannifier()
         new_content = unicode(spannifier.unspannify_new(modified_spanned_content))
         new_version = TextVersion.objects.duplicate(text_version, request.user, keep_comments=True, keep_dates = False)
         
         # remove amendments from new version :
         amendment_comments, amendment_dis = new_version.get_amendments() 
         amendment_dis.delete()
         amendment_comments.delete()
         
         # call edit to input new content and manage coment positioning
         new_version.edit(new_title = new_version.title, 
                     new_note = _(u'amended version'),
                     new_tags = new_version.tags, 
                     new_content = new_content,
                     keep_comments=True
                     )
         location = reverse('text-viewandcomment',args=[text_version.text_id])
     if amendments :
         success_message = _(u"amendments were applied with success")
     else :
         success_message = _(u"there are no amendments on this text")
     return True, location, success_message
     
@local_text_permission_required('can_view_local_text')
def mail_subscribe(request, do_subscribe, version_id):
    text_version = TextVersion.objects.get(id=version_id)
    alerts = EmailAlert.objects.get_user_alerts(request.user, text_version.text) ;
    subscribed = (len(alerts) > 0)
    mess = ""
    if do_subscribe:
        ret = True ;
        if subscribed :
            mess = _(u"You already subscribed to the text")
        else : 
            EmailAlert.objects.create_alert(request.user, text_version.text)
            mess = _(u"You subscribed to the text")
    else :
        ret = False ;
        if subscribed :
            EmailAlert.objects.delete_alert(request.user, text_version.text)
            mess = _(u"You have been unsubscribed from the text")
        else : 
            mess = _(u"You have already been unsubscribed from the text")

    return True, ret, mess
     
@local_text_permission_required('can_manage_comment_local_text')
def del_attach(request, attachId, version_id):
    return non_protected_del_attach(request, attachId, version_id)

def non_protected_del_attach(request, attachId, version_id):
    try :
         Comment.objects.get(id=attachId).delete()
    except :               
        if dj_settings.DEBUG:
            raise
        else:
            pass
    return True

@local_text_permission_required('can_manage_comment_local_text')
def del_discussionitem(request, discussionItemId, version_id):
    return non_protected_del_discussionitem(request, discussionItemId, version_id)

def non_protected_del_discussionitem(request, discussionItemId, version_id):
    DiscussionItem.objects.get(id=discussionItemId).delete()
    return True

MAX_NB_TAGS_IN_COMMENT_CLOUD = 30
@local_text_permission_required('can_view_comment_local_text')
def get_tagcloud(request, version_id) :
    allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', request.user, version_id)
    cursor = connection.cursor()
    c_rows = []
    d_rows = []

    arg = [version_id]
    
    comment_content_type_id = ContentType.objects.get_for_model(Comment).id   
    discussion_item_content_type_id = ContentType.objects.get_for_model(DiscussionItem).id
    
    allowedStateCommentCond = """AND "cm_comment_objectstate"."state_id" in (%s) AND "cm_comment_objectstate"."content_type_id" = %s """ % (",".join([str(t.id) for t in allowed_states]), comment_content_type_id)
    # warning not same thing as the 'allowedStateDiscussionItemCond' in get_comments  
    allowedStateDiscussionItemCond = """AND "cm_di_objectstate"."state_id" in (%s) AND "cm_di_objectstate"."content_type_id" = %s """ % (",".join([str(t.id) for t in allowed_states]), discussion_item_content_type_id)
    sql = """SELECT "cm_comment"."id"
            FROM "cm_comment" 
                INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
            WHERE "cm_comment"."text_version_id" = %s
            """ + allowedStateCommentCond
            
    cursor.execute(sql, arg)
    c_rows = cursor.fetchall()
    
    sql = """SELECT "cm_discussionitem"."id"
            FROM "cm_discussionitem" 
                INNER JOIN "cm_comment" AS "cm_comment" ON "cm_comment"."id" = "cm_discussionitem"."comment_id" 
                INNER JOIN "cm_objectstate" AS "cm_di_objectstate" ON "cm_discussionitem"."id" = "cm_di_objectstate"."object_id" 
                INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
            WHERE "cm_comment"."text_version_id" = %s
            """  + allowedStateDiscussionItemCond + allowedStateDiscussionItemCond
    cursor.execute(sql, arg)
    d_rows = cursor.fetchall()
 
    tagCloud = []
    if c_rows or d_rows :
        # this next line has been replaced by following code to mix tags for Comment and DiscussionItem
        #tagCloud = list(Tag.objects.cloud_for_model(Comment, steps=8, distribution=LOGARITHMIC, filters=dict(id__in=[r[0] for r in c_rows])))

        c_tags = []
        if c_rows :
            c_tags = list(Tag.objects.usage_for_model(Comment, counts=True, filters=dict(id__in=[r[0] for r in c_rows])))
        
        discussionitem_tags = []
        if d_rows :
            discussionitem_tags = list(Tag.objects.usage_for_model(DiscussionItem, counts=True, filters=dict(id__in=[r[0] for r in d_rows])))
        
        # appending discussionitem tags to tags :
        tags = dict([(c.name, c) for c in c_tags])
        for di_tag in discussionitem_tags : 
            if di_tag.name in tags.keys(): # update its count if tags is also a comment tag :
                tags[di_tag.name].count = tags[di_tag.name].count + di_tag.count
            else : # append it if it is a discussionitem tag only :
                tags[di_tag.name]=di_tag
        
        ordered_tags = sorted(tags.values(), key=(lambda x : x.count), reverse = True)
        ordered_tags = ordered_tags[:MAX_NB_TAGS_IN_COMMENT_CLOUD]
        alpha_ordered_tags =  sorted(ordered_tags, key=(lambda x : x.name))
        
        tagCloud = calculate_cloud(alpha_ordered_tags, steps=8, distribution=LOGARITHMIC)
        
    return tagCloud
        
@local_text_permission_required('can_view_comment_local_text')
def get_comments_protected(request, fromWord, toWord, orderBy, version_id) :
    return get_comments(request, fromWord, toWord, orderBy, version_id) 

# test datas : 
# user 2 (username : 'user') is Owner of text 1 (last version : 'Title ...') 
# text 1 is set to 'a priori moderation' and has two comments on its only version.one is in state 1 ... the other in state 2 
# user 3 (username : 'user2') has role Editor and Observer on text 1 (last version : 'Title of text1 version 2...') 
# user 2 (username : 'user') is Editor of text 2 (last version : 'Title of text2') 
# user 2 (username : 'user') is Observer of text 3 (last version : 'last revision') 
def get_comments(request, fromWord, toWord, orderBy, version_id) :
    textsearchfor = request.POST['textsearchfor']
    textsearchin = request.POST['textfilterselect']
    datefilterselect = request.POST['datefilterselect']
    statefilterselect = request.POST['statefilterselect']
    dateFrom = request.POST['fromdatefield']
    dateTo = request.POST['todatefield']
    tagid = request.POST['tagId']
    if tagid == "-1" :
        tagid = None
    

    # $$$ start : to be discuss 
    if not statefilterselect :
        return []
    # end : to be discuss 

    allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', request.user, version_id)
    cursor = connection.cursor()
    rows = []

    arg = [version_id]

    toWordCond = ""
    if toWord != -1 :
        toWordCond = """AND "cm_comment"."start_word" <= %s """
        arg.append(toWord)

    fromWordCond = ""
    if fromWord != -1 :
        fromWordCond = """AND "cm_comment"."end_word" >= %s """ 
        arg.append(fromWord)  
    
    comment_content_type_id = ContentType.objects.get_for_model(Comment).id   
    discussion_item_content_type_id = ContentType.objects.get_for_model(DiscussionItem).id
    
    dateFromCommentCond = ""
    dateToCommentCond = ""
    dateToDiscussionItemCond = ""
    dateFromDiscussionItemCond = ""
    stateCommentCond = ""
    stateDiscussionItemCond = ""
    
    if not tagid : 
        if dateFrom != "" and (datefilterselect == "createdafter" or datefilterselect == "createdbetween"):
            dateFromCommentCond = """AND "cm_comment"."created" >= %s """
            dateFromDiscussionItemCond = """AND "cm_discussionitem"."created" >= %s """
            arg.append(dateFrom)
    
        if dateTo != "" and (datefilterselect == "createdbefore" or datefilterselect == "createdbetween") :
            dateToCommentCond = """AND "cm_comment"."created" <= %s """
            dateToDiscussionItemCond = """AND "cm_discussionitem"."created" <= %s """
            arg.append(dateTo)
    
        if statefilterselect :
            stateCommentCond = """AND "cm_comment_objectstate"."state_id" in (%s) AND "cm_comment_objectstate"."content_type_id" = %s """ % (statefilterselect, comment_content_type_id)  
            stateDiscussionItemCond = """AND "cm_di_objectstate"."state_id" in (%s) AND "cm_di_objectstate"."content_type_id" = %s """ % (statefilterselect, discussion_item_content_type_id)
    
    allowedStateCommentCond = """AND "cm_comment_objectstate"."state_id" in (%s) AND "cm_comment_objectstate"."content_type_id" = %s """ % (",".join([str(t.id) for t in allowed_states]), comment_content_type_id) 
    allowedStateDiscussionItemCond = """AND "d_objectstate"."state_id" in (%s) AND "d_objectstate"."content_type_id" = %s """ % (",".join([str(t.id) for t in allowed_states]), discussion_item_content_type_id)

    commentConds = allowedStateCommentCond + stateCommentCond + toWordCond + fromWordCond + dateFromCommentCond + dateToCommentCond
    discussionItemConds = allowedStateCommentCond + stateDiscussionItemCond + toWordCond + fromWordCond + dateFromDiscussionItemCond + dateToDiscussionItemCond
    
    if tagid :
        tag = Tag.objects.get(id=tagid)
    
        taggedComments = TaggedItem.objects.get_by_model(Comment, tag)
        ids = [str(c.id) for c in taggedComments]
        
        taggedDiscs = TaggedItem.objects.get_by_model(DiscussionItem, tag)
        ids = ids + [str(t.comment_id) for t in taggedDiscs]

        sql = """SELECT "cm_comment"."id",
                            "cm_comment_creator"."username",
                            (SELECT COUNT(*) FROM "cm_discussionitem" as "d" 
                                INNER JOIN "cm_objectstate" AS "d_objectstate" ON "d"."id" = "d_objectstate"."object_id" 
                            WHERE "d"."comment_id" = "cm_comment"."id" """ + allowedStateDiscussionItemCond + """),                                
                            "cm_comment_objectstate"."state_id"
                    FROM "cm_comment" 
                        INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
                        LEFT OUTER JOIN "auth_user" AS "cm_comment_creator" ON "cm_comment"."creator_id" = "cm_comment_creator"."id" 
                    WHERE "cm_comment"."text_version_id" = %s and "cm_comment"."id" in (%s) %s""" %  (version_id, ",".join(ids),allowedStateCommentCond)
                    
        cursor.execute(sql)
        rows = cursor.fetchall()

    elif textsearchfor == "" :
        sql = """SELECT "cm_comment"."id",
                            "cm_comment_creator"."username",
                            (SELECT COUNT(*) FROM "cm_discussionitem" as "d" 
                                INNER JOIN "cm_objectstate" AS "d_objectstate" ON "d"."id" = "d_objectstate"."object_id" 
                            WHERE "d"."comment_id" = "cm_comment"."id" """ + allowedStateDiscussionItemCond + """),                                
                            "cm_comment_objectstate"."state_id"
                FROM "cm_comment" 
                    INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
                    LEFT OUTER JOIN "auth_user" AS "cm_comment_creator" ON "cm_comment"."creator_id" = "cm_comment_creator"."id" 
                WHERE "cm_comment"."text_version_id" = %s
                """ + commentConds
        cursor.execute(sql, arg)
        rows = cursor.fetchall()
        sql = """SELECT DISTINCT "cm_comment"."id",
                            "cm_comment_creator"."username",
                            (SELECT COUNT(*) FROM "cm_discussionitem" as "d" 
                                INNER JOIN "cm_objectstate" AS "d_objectstate" ON "d"."id" = "d_objectstate"."object_id" 
                            WHERE "d"."comment_id" = "cm_comment"."id" """ + allowedStateDiscussionItemCond + """),                                
                            "cm_comment_objectstate"."state_id"
                FROM "cm_discussionitem" 
                    INNER JOIN "cm_comment" AS "cm_comment" ON "cm_comment"."id" = "cm_discussionitem"."comment_id" 
                    INNER JOIN "cm_objectstate" AS "cm_di_objectstate" ON "cm_discussionitem"."id" = "cm_di_objectstate"."object_id" 
                    INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
                    LEFT OUTER JOIN "auth_user" AS "cm_comment_creator" ON "cm_comment"."creator_id" = "cm_comment_creator"."id" 
                WHERE "cm_comment"."text_version_id" = %s
                """  + discussionItemConds
        cursor.execute(sql, arg)
        rows = rows + cursor.fetchall()
                    
    else :
        arg = arg + ['%%%s%%' % textsearchfor, '%%%s%%' % textsearchfor]
        if textsearchin == "user" :
            sql = """SELECT "cm_comment"."id",
                                "cm_comment_creator"."username",
                                (SELECT COUNT(*) FROM "cm_discussionitem" as "d" 
                                    INNER JOIN "cm_objectstate" AS "d_objectstate" ON "d"."id" = "d_objectstate"."object_id" 
                                WHERE "d"."comment_id" = "cm_comment"."id" """ + allowedStateDiscussionItemCond + """),                                
                                "cm_comment_objectstate"."state_id"
                    FROM "cm_comment" 
                        INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
                        LEFT OUTER JOIN "auth_user" AS "cm_comment_creator" ON "cm_comment"."creator_id" = "cm_comment_creator"."id" 
                    WHERE "cm_comment"."text_version_id" = %s
                    """ + commentConds +""" 
                    AND (("cm_comment"."creator_id" is not null and "cm_comment_creator"."username" ILIKE %s) OR "cm_comment"."username" ILIKE %s)""" 

            cursor.execute(sql, arg)
            rows = cursor.fetchall()
    
            sql = """SELECT DISTINCT "cm_comment"."id",
                                "cm_comment_creator"."username",
                                (SELECT COUNT(*) FROM "cm_discussionitem" as "d" 
                                    INNER JOIN "cm_objectstate" AS "d_objectstate" ON "d"."id" = "d_objectstate"."object_id" 
                                WHERE "d"."comment_id" = "cm_comment"."id" """ + allowedStateDiscussionItemCond + """),                                
                                "cm_comment_objectstate"."state_id"
                    FROM "cm_discussionitem" 
                        INNER JOIN "cm_comment" AS "cm_comment" ON "cm_comment"."id" = "cm_discussionitem"."comment_id" 
                        INNER JOIN "cm_objectstate" AS "cm_di_objectstate" ON "cm_discussionitem"."id" = "cm_di_objectstate"."object_id" 
                        INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
                        LEFT OUTER JOIN "auth_user" AS "cm_discussionitem_creator" ON "cm_discussionitem"."creator_id" = "cm_discussionitem_creator"."id" 
                        LEFT OUTER JOIN "auth_user" AS "cm_comment_creator" ON "cm_comment"."creator_id" = "cm_comment_creator"."id" 
                    WHERE "cm_comment"."text_version_id" = %s
                    """  + discussionItemConds + """ 
                    AND (("cm_discussionitem"."creator_id" is not null and "cm_discussionitem_creator"."username" ILIKE %s) OR "cm_discussionitem"."username" ILIKE %s)"""
            cursor.execute(sql, arg)
            rows = rows + cursor.fetchall()
            
        elif textsearchin == "text_and_title" :
            sql = """SELECT "cm_comment"."id",
                                "cm_comment_creator"."username",
                                (SELECT COUNT(*) FROM "cm_discussionitem" as "d" 
                                    INNER JOIN "cm_objectstate" AS "d_objectstate" ON "d"."id" = "d_objectstate"."object_id" 
                                WHERE "d"."comment_id" = "cm_comment"."id" """ + allowedStateDiscussionItemCond + """),                                
                                "cm_comment_objectstate"."state_id"
                    FROM "cm_comment" 
                        INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
                        LEFT OUTER JOIN "auth_user" AS "cm_comment_creator" ON "cm_comment"."creator_id" = "cm_comment_creator"."id" 
                    WHERE "cm_comment"."text_version_id" = %s
                    """  + commentConds + """
                    AND (("cm_comment"."content" ILIKE %s) OR ("cm_comment"."title" ILIKE %s))"""
            cursor.execute(sql, arg)
            rows = cursor.fetchall()
            
            sql = """SELECT DISTINCT "cm_comment"."id",
                                "cm_comment_creator"."username",
                                (SELECT COUNT(*) FROM "cm_discussionitem" as "d" 
                                    INNER JOIN "cm_objectstate" AS "d_objectstate" ON "d"."id" = "d_objectstate"."object_id" 
                                WHERE "d"."comment_id" = "cm_comment"."id" """ + allowedStateDiscussionItemCond + """),                                
                                "cm_comment_objectstate"."state_id"
                    FROM "cm_discussionitem" 
                        INNER JOIN "cm_comment" AS "cm_comment" ON "cm_comment"."id" = "cm_discussionitem"."comment_id" 
                        INNER JOIN "cm_objectstate" AS "cm_di_objectstate" ON "cm_discussionitem"."id" = "cm_di_objectstate"."object_id" 
                        INNER JOIN "cm_objectstate" AS "cm_comment_objectstate" ON "cm_comment"."id" = "cm_comment_objectstate"."object_id" 
                        LEFT OUTER JOIN "auth_user" AS "cm_comment_creator" ON "cm_comment"."creator_id" = "cm_comment_creator"."id" 
                    WHERE "cm_comment"."text_version_id" = %s
                    """  + discussionItemConds + """
                    AND (("cm_discussionitem"."content" ILIKE %s) OR ("cm_discussionitem"."title" ILIKE %s))"""
            cursor.execute(sql, arg)
            rows = rows + cursor.fetchall()

    addInfos = dict([(r[0],r) for r in rows])

    # ordering :
    comments = list( Comment.objects.filter(id__in=addInfos.keys()).order_by(orderBy))
    
    for comment in comments :
        r = addInfos[comment.id]
        if comment.creator_id != None :
            comment.username = r[1]
        setattr(comment, 'discussion_count', r[2])
        setattr(comment, 'state_id', r[3])
     
    return comments

@local_text_permission_required('can_view_comment_local_text')
def get_discussion_items(request, attachIds, version_id) :
    allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', request.user, version_id)
    allowed = [t.id for t in allowed_states]

    ret = {}
    discussionItems = DiscussionItem.objects.select_related(depth=1).filter(comment__id__in = attachIds).order_by('created')
    for di in discussionItems :
        state_id = di.states.get().state_id
        if state_id in allowed :
            setattr(di, 'state_id', state_id)

            if di.creator != None :
                # should not be expensive (cf. select_related)
                di.username = di.creator.username
                
            tab = ret.setdefault(di.comment_id, [])    
            tab.append(di)
    return ret 

# COULD really become a major source of bugs !!!!!!!!! use with care 
def so_get_occs(version_id):
    # 1 prepare a call to get_comments
    request = HttpRequest()
    request.POST['textsearchfor'] = ''
    request.POST['textfilterselect'] = ''
    request.POST['datefilterselect'] = ''
    request.POST['fromdatefield'] = '2007-01-01 00:00:00'
    request.POST['todatefield'] = '2100-01-01 00:00:00'
    request.POST['tagId'] = '-1'
    
    request.POST['statefilterselect'] = ",".join([str(st.id) for st in State.objects.all()])
    
    version = TextVersion.objects.get(id=version_id) 
    our = ObjectUserRole.objects.filter(Q(role__name = 'Owner'),Q(object_id__exact = version.text_id),Q(content_type = ContentType.objects.get_for_model(Text)))
    request.user = our[0].user
    
    # 2 call get_occs
    fromWord = -1
    toWord = -1
    ret = get_occs(request, fromWord, toWord, version_id)
    #if ret.__class__ != HttpResponseRedirect :
    #    (occs, ret_comments) = ret
    (occs, ret_comments) = ret
    
    # add so_ specifics :
    discs = get_discussion_items(request, [comment.id for comment in ret_comments], version_id = version.id)
    
    tags = get_tagcloud(request, version_id = version.id)
    
    return simplejson.dumps({"fromWord" : fromWord, "toWord" : toWord, "attachs" : ret_comments, "discussionItems" : discs,"tags" : tags}, cls=ComplexEncoder)

@local_text_permission_required('can_view_comment_local_text')
def get_occs_protected(request, fromWord, toWord, version_id):
    return get_occs(request, fromWord, toWord, version_id)
                    
def get_occs(request, fromWord, toWord, version_id):
    comments = get_comments(request, fromWord, toWord, "start_word", version_id = version_id)
    occs = []
    occs = compute_occs(comments, fromWord, toWord)
    
    # only return comments in case client asked for all comments : (fromWord == toWord == -1)
    ret_comments = [] 
    if fromWord == toWord  and fromWord == -1 :
        ret_comments = comments
    
    return (occs, ret_comments)

def compute_occs(comments, fromWord, toWord) :
    occs = []
    if comments :
        starts = {}     # word --> [ids of comments starting on this word]
        ends = {}
        
        for comment in comments :
            starts.setdefault(comment.start_word, set([])).add(comment.id)
            ends.setdefault(comment.end_word, set([])).add(comment.id)
        
        startWords = set(starts.keys())
        endWords = set(ends.keys())
        s = min(startWords)
        e = max(endWords)
        
        ids = set([])
        start = s;
        for word in range(s, e + 2) :
                size = len(ids); # size := nber of ids before this word
                
                if word in startWords : # ids := set of ids on word
                    ids = ids.union(starts[word]);
                if word - 1 in endWords :
                    ids = ids.difference(ends[word - 1]);

                if size != len(ids) :
                    if size == 0 :
                        start = word
                    else :
                        d = start
                        f = word - 1
                        doAdd = True

                        if fromWord != -1 and d < fromWord :
                            if f < fromWord :
                                doAdd = False
                            d = fromWord
                        if toWord != -1 and f > toWord :
                            if d > toWord :
                                doAdd = False
                            f = toWord
                        if doAdd :
                            occs.append(Occ(size, d, f))    
                        start = word
    return occs

def export_colorize_comment(comments, spanned_soup):
    spans = spanned_soup.findAll('span', id=re.compile("w_*"))

    occs = compute_occs(comments, -1, -1)
    if len(occs)>0 :
        i = 0
        occ = occs[i]
        color = occ.compute_color()
        for span in spans :
            id = int(span['id'][2:])
            if id >= occ.startWord and id <= occ.endWord :
                span['style']='background-color:%s;'%color
                
            if id == occ.endWord :
                if i == len(occs) - 1 :
                    break ;
                else : 
                     i = i + 1
                     occ = occs[i]
                     color = occ.compute_color()
# this would be simpler but takes much more time !!
#    for occ in occs :
#        color = occ.compute_color()
#        for word in range(occ.startWord, 1 + occ.endWord) :
#            span = spanned_soup.find('span', id="w_%s"%word)
#            span['style']='background-color:%s;'%color
                     
                 

def export_add_comment(request, version):
    # ADDING MARKERS
    spannifier = Spannifier() 
    soup = spannifier.get_the_soup(version.content)
    res = spannifier.spannify_new(soup)
    
    spanned_soup = BeautifulSoup(res)
    
    version_id = int(request.POST['versionId'])
    comments = get_comments(request, -1, -1, "start_word", version_id = version_id)

    comments_starts = {}
    comments_ends = {}
    for comment in comments :
        starts = comments_starts.setdefault(comment.start_word, [])
        starts.append(comment)

    comment_count = 1
    sortedstarts = comments_starts.keys()
    sortedstarts.sort() 
    for start in sortedstarts : 
        ss = ""
        for comment in comments_starts[start] :
            ss = "%s[%s>"%(ss, comment_count)
            
            ends = comments_ends.setdefault(comment.end_word, [])
            ends.append(comment_count)
            comment_count = comment_count + 1
        
        start_span = spanned_soup.find(id="w_%s"%start)
        start_span.contents[0].replaceWith(u"%s%s"%(ss, start_span.contents[0]))

    for end in comments_ends.keys() : 
        ss = ""
        comments_ends[end].sort()
        for ind in comments_ends[end] :  #.reverse():
            ss = "<%s]%s"%(ind , ss)
        end_span = spanned_soup.find(id="w_%s"%end)
        end_span.contents[0].replaceWith(u"%s%s"%(end_span.contents[0], ss))
        
    export_colorize_comment(comments, spanned_soup)
        
    # REQUESTING COMMENTS REPLIES
    discs = get_discussion_items(request, [comment.id for comment in comments], version_id = version.id)            
        
    # ADDING COMMENTS CONTENT
    output = unicode(spanned_soup)
    
    comment_count = 1
    can_manage_comment = user_has_perm_on_text(request.user, 'can_manage_comment_local_text', version.text_id)
    ss=[] 
    
    for start in sortedstarts :
        for comment in comments_starts[start] :
            ss.append("<hr />")
            ss.append(format_attach(comment, can_manage_comment, "","[%s] "%comment_count))
            di_count = 1
            for di in discs.get(comment.id,[]) :
                ss.append("<br /><br />")
                ss.append(format_attach(di, can_manage_comment, "&nbsp;&nbsp;&nbsp;&nbsp;", "[%s.%s] "%(comment_count, di_count)))
                di_count = di_count + 1
            comment_count = comment_count + 1
    output = output + ''.join(ss)
      
    return output

def format_attach(attach, with_state, sep, prefix):
    date =  _(u"by %(name)s on the %(date)s") %{'name' : attach.username,'date' : local_date(attach.created)}
    state_name = ""
    if with_state :
        state_name = "%(sep)s(%(state_name)s)<br />" % {'sep':sep, 'state_name':_(attach.states.get().state.name)}
    tags = ""
    if attach.tags :
        tags = "<br />%(sep)s%(tag_label)s%(tags)s" % {'sep':sep,
                                                       'tag_label':_(u"tags: "), 
                                                       'tags':", ".join(parse_tag_input(attach.tags))}
    ss = "%(sep)s%(prefix)s%(title)s<br />%(sep)s%(date)s<br />%(state_name)s%(sep)s%(content)s%(tags)s"  % {'sep':sep,
                                                                            'prefix':prefix,
                                                                            'title':attach.title, 
                                                                            'date':date, 
                                                                            'state_name':state_name,
                                                                            'content':attach.content,
                                                                            'tags':tags}
    return ss

@local_text_permission_required('can_view_local_text')
def version_export(request, version_id):
    version = get_object_or_404(TextVersion,pk = version_id)
    if request.method == 'POST':
        format = request.POST['format']
        
        from cm.utils.ooconvert import fmts        
        fmt = fmts.get_by_name(format)
        response = HttpResponse(mimetype=fmt['mimetype'])
        file_title = version.title + u'.%s' %fmt['extension']
        encoded_name = str(Header(file_title.encode('utf8'), charset='utf8', maxlinelen=500))
        h = u'attachment; filename=%s' %encoded_name
        response['Content-Disposition'] = h
        
        body = version.content
        if request.POST['txtOnly'] == '0' :
            body = export_add_comment(request, version)
            
        from cm.utils.ooconvert import convert_html,combine_css_body
        data = combine_css_body(body,version.css)
        
        content = convert_html(data.encode('utf-8'),fmt['name'])
        
        response.write(content) #.decode('utf-8')
        return response
    return HttpResponse()

@local_text_permission_required('can_view_local_text')
def version_print(request, version_id):
    version = get_object_or_404(TextVersion,pk = version_id)
    body = version.content
    if request.method == 'POST'and request.POST['txtOnly'] == '0' :
        body = export_add_comment(request, version)
    body += """<script type="text/javascript">window.print();</script>""";
        
    from cm.utils.ooconvert import combine_css_body
    content = combine_css_body(body,version.css)
    return HttpResponse(content)        

# import is done inside functions (avoid uno pb in tests)
# from cm.utils.ooconvert import fmts,convert_html,combine_css_body

@local_text_permission_required('can_add_comment_local_text')
def validate_tags(request, tags, version_id):
    try :
        if len(tags) > 250 :
            return _(u"Tags input must be no longer than 250 characters.")
        if tags :
            is_tag_list(tags)
        return ''
    except ValidationError, e :
        return ",".join(e.messages)