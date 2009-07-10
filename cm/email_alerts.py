from cm.models import EmailAlert, Comment, DiscussionItem, comment_states_with_perm_for_text, user_has_perm_on_text, comment_states_with_perm_for_workflow
from cm.utils.mail import EmailMessage
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

EMAIL_SUBJECT_PREFIX = '[co-ment] '

def get_past_and_text(comment):
    """
    Comment / DiscussionItem abstraction to get:
    exist_in_past: does another similar (i.e. from copy) object exists
    text_version / text 
    """
    if type(comment) == Comment:
        exist_in_past = Comment.objects.exists_past_comment_with_same_date(comment)
        text_version = comment.text_version
        text = text_version.text
    elif type(comment) == DiscussionItem:
        exist_in_past = DiscussionItem.objects.exists_past_discussionitem_with_same_date(comment)
        text_version = comment.comment.text_version
        text = text_version.text
    else:
        raise Exception('Unsupported type in alert')
    return text, exist_in_past, text_version

def send_comment_created_email(comment, alert, user):
    if type(comment) == Comment:
        title = _(u"A comment entitled '%(comment_title)s' has been added to the text '%(text_title)s'") % {'comment_title': comment.title, 'text_title': comment.text_version.title}
    else:
        title = _(u"A reply entitled '%(reply_title)s' to the comment '%(comment_title)s' has been added (text '%(text_title)s'): ") % {'reply_title': comment.title, 'comment_title': comment.comment.title, 'text_title': comment.comment.text_version.title}
    body = render_to_string('notifications/alert_email_body.html', {'title': title,
                                                                    'site_url': settings.SITE_URL,
                                                                    'text_url': reverse('text-viewandcomment', args=[alert.text.id]),
                                                                    'site_name': settings.SITE_NAME,
                                                                    'content': comment.content,
                                                                    'unsubscribe_url': alert.get_unsubscribe_url(),
                                                                    })
    EmailMessage(EMAIL_SUBJECT_PREFIX + title, body, settings.DEFAULT_FROM_EMAIL, [user.email]).send()

def comment_created(sender, **kwargs):
    comment = kwargs['instance']
    state = kwargs['state']
    text, exist_in_past, text_version = get_past_and_text(comment)
    if exist_in_past:
        return

    alerts = EmailAlert.objects.get_alerts(text)
    for alert in alerts:
        user = alert.user

        # permission & activate check
        allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', user, text_version.id)
        if user.is_active and state in allowed_states:        
            send_comment_created_email(comment, alert, user)
            

def textversion_created(sender, **kwargs):
    if kwargs['created']:
        text_version = kwargs['instance']
        text = text_version.text
        
        alerts = EmailAlert.objects.get_alerts(text)
        
        for alert in alerts:
            user = alert.user
    
            # permission check
            if user.is_active and user_has_perm_on_text(user, 'can_view_local_text', text.id):            
                if text_version.note:
                    title = _(u"A new version of the text entitled '%(text_version_name)s' has been created (note : '%(version_note)s')") % {'version_note' : text_version.note,
                                                                                                                                  'text_version_name' : text_version.title,
                                                                                                                                  }
                else:
                    title = _(u"A new version of the text entitled '%(text_version_name)s' has been created") % {'text_version_name' : text_version.title}
                content = _(u"Click here to access this version: %(version_url)s") % {'version_url' : settings.SITE_URL + reverse('text-viewandcommentversion', args=[text.id, text_version.id])}
                body = render_to_string('notifications/alert_email_body.html',
                                           { 'title': title,
                                             'text_url': reverse('text-viewandcomment', args=[alert.text.id]),                                            
                                             'site_url' : settings.SITE_URL,
                                             'site_name' : settings.SITE_NAME,
                                             'content': content,
                                             'unsubscribe_url': alert.get_unsubscribe_url(),
                                           })
                EmailMessage(EMAIL_SUBJECT_PREFIX + title, body, settings.DEFAULT_FROM_EMAIL, [user.email]).send()

def state_changed(sender, **kwargs):    
    comment = kwargs['instance']
    old_state = kwargs['old_state']
    old_workflow = kwargs['old_workflow']
    state = kwargs['state']
    text, exist_in_past, text_version = get_past_and_text(comment)
    if exist_in_past:
        return
    alerts = EmailAlert.objects.get_alerts(text)
    for alert in alerts:
        user = alert.user

        
        
        allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', user, text_version.id)
        if old_workflow:
            old_allowed_states = comment_states_with_perm_for_workflow('can_view_comment_local_text', user, old_workflow, text.id)
        else:
            old_allowed_states = allowed_states 
        # permission check
        # check that the state update makes the comment visible
        if user.is_active and state in allowed_states and old_state not in old_allowed_states:
            send_comment_created_email(comment, alert, user)
            
    
    #import pdb;pdb.set_trace()
