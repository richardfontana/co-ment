import os
import django.dispatch
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from utils.contentHandler import processContent
from tagging.fields import TagField
from tagging.models import TaggedItem
from cm import patchs
from cm.utils.commentPositioning import compute_new_comment_positions
import datetime, random, re, sha
import sys
import xml.dom.minidom

class State(models.Model):
    name = models.TextField()

    def __unicode__(self):
        return self.name
    
class Workflow(models.Model):
    initial_state = models.ForeignKey(State, related_name="workflow_initial")
    states = models.ManyToManyField("State")
    name = models.TextField()
    
    def states_as_jsdict(self):
        states = []
        for state in self.states.all() :
            states.append(":".join([str(state.id), '"%s"' % _(state.name)]))
        return "{%s}" % ",".join(states)

    def __unicode__(self):
        return self.name
    
class ObjectState(models.Model):
    state = models.ForeignKey(State)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey()

    class Meta:
        unique_together = (('state', 'object_id', 'content_type'))
                
class StateRolePermissions(models.Model):
    state = models.ForeignKey(State)
    role = models.ForeignKey("Role")    
    permissions = models.ManyToManyField(Permission, related_name="object_states")

    class Meta:
        unique_together = (('state', 'role'),)        

class ObjectUserRole(models.Model):
    role = models.ForeignKey("Role")    
    user = models.ForeignKey(User, null=True, blank=True)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = (('role', 'user', 'object_id', 'content_type'))        

    def __unicode__(self):
        if self.user:
            return u"%s: %s %s %i %s" % (self.__class__.__name__, self.user.username, self.content_type, self.object_id, self.role.name)
        else:
            return u"%s: *ALL* %s %i %s" % (self.__class__.__name__, self.content_type, self.object_id, self.role.name)
    
    def __repr__(self):
        return self.__unicode__()

class Role(models.Model):
    """
    'Static' application roles 
    """
    name = models.CharField(ugettext_lazy('name'), max_length=50, unique=True)
    order = models.IntegerField(unique=True)
    permissions = models.ManyToManyField(Permission, related_name="roles")
    
    def __unicode__(self):
        return u"%s" % (self.name)
    
    def __hash__(self):
        return self.id

SERVICE_LEVEL_DATA = []

SERVICE_LEVEL_DEFINITIONS = dict(SERVICE_LEVEL_DATA)

SERVICE_LEVEL_CHOICES = [(key, value[0]) for key, value in SERVICE_LEVEL_DATA]

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        """
        Validates an activation key and activates the corresponding
        ``User`` if valid.
        If the key is valid , returns the ``User`` as second arg
        First is boolean indicating if user has just been activated
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False, False
            user = profile.user
            activated = False
            if not user.is_active:
                user.is_active = True
                user.save()
                activated = True
            return (activated, user)
        return False, False

    def invite_user(self, email):
        """
        Invite a new user 
            - if does not exist : create it with every field empty except email
            - return user if it exists 
        """
        try:
            user = User.objects.get(email=email)
            created = False
        except User.DoesNotExist:
            # workaround because user.username must be unique
            tempu = random.randint(1, sys.maxint)
            user = User.objects.create_user(str(tempu), email, '')
            user.is_active = False
            user.save()    
            profile = self.create_profile(user)
            profile.is_temp = True
            if SERVICE_LEVEL_DATA:
                profile.service_level = SERVICE_LEVEL_DATA[0][0]
            profile.save()
            created = True
        return (created, user)
        
    def create_inactive_user(self, username, email, password, preferred_language, send_email=True, next_activate=None):
        """
        Creates a new, inactive ``User``, generates a
        ``RegistrationProfile`` and emails its activation key to the
        ``User``. Returns the new ``User``.
        """
        try:
            user = User.objects.get(email=email)
            # we know that user is temp
            created = False
            user.username = username
            user.set_password(password)
            user.save()
            profile = user.get_profile()
            profile.is_temp = False
        except User.DoesNotExist:
            created = True            
            user = User.objects.create_user(username, email, password)
            user.is_active = False
            user.save()

            profile = self.create_profile(user)

        profile.preferred_language = preferred_language
        if SERVICE_LEVEL_DATA:
            profile.service_level = SERVICE_LEVEL_DATA[0][0]
        profile.save()

        if send_email:
            from django.core.mail import send_mail
            from django.core.urlresolvers import reverse
            site_url = settings.SITE_URL
            site_name = settings.SITE_NAME

            subject = render_to_string('accounts/activation_email_subject.html',
                                       { 'site_url': site_url })
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())

            from django.core.urlresolvers import reverse
            if next_activate:
                activation_url = reverse('activate-next', args=[profile.activation_key, next_activate])
            else:
                activation_url = reverse('activate', args=[profile.activation_key])
                 
            message = render_to_string('accounts/activation_email.html',
                                       { 
                                         'activation_url' : activation_url,
                                         'site_url': site_url,
                                         'site_name': site_name,
                                          })

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        return user

    def create_profile(self, user):
        """
        Creates a ``Profile`` for a given
        ``User``. Returns the ``Profile``.
        The activation key for the ``Profile`` will be a
        SHA1 hash, generated from a combination of the ``User``'s
        username and a random salt.
        """
        salt = sha.new(str(random.random())).hexdigest()[:5]
        activation_key = sha.new(salt + user.username).hexdigest()
        return self.create(user=user, activation_key=activation_key)

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)

    activation_key = models.CharField(ugettext_lazy(u'activation key'), max_length=40)
    allow_contact = models.BooleanField(default=True)    
    service_level = models.CharField(max_length=20, choices=SERVICE_LEVEL_CHOICES)
    preferred_language = models.CharField(max_length=2, default="en")
    
    objects = RegistrationManager()

    is_temp = models.BooleanField(default=False)
    is_email_error = models.BooleanField(default=False)
    
    def get_max_number_text(self):
        if SERVICE_LEVEL_CHOICES :
            return SERVICE_LEVEL_DEFINITIONS[self.service_level][1]
        return sys.maxint

    def get_max_shared_number_text(self):
        if SERVICE_LEVEL_CHOICES :
            return SERVICE_LEVEL_DEFINITIONS[self.service_level][2]
        return sys.maxint

    def get_max_collaborators_text(self):
        if SERVICE_LEVEL_CHOICES :
            return SERVICE_LEVEL_DEFINITIONS[self.service_level][3]
        return sys.maxint

    def is_service_level_free(self):
        return self.service_level == "FREE"

    def upgrade_service_level_to_pro(self):
        self.service_level = "PRO"
        self.save()
    
    def downgrade_service_level_to_free(self):
        self.service_level = "FREE"
        self.save()
    
    def display_name(self):
        if self.is_email_error:
            return self.user.email + u' (' + _(u'invitation failed (email error) !') + u')'                    
        elif self.is_temp:
            return self.user.email + u' (' + _(u'invitation pending') + u')'        
        else:
            return self.user.username

    def can_be_contacted(self):
        return self.allow_contact and not self.is_temp 
    
    def __unicode__(self):
        return self.user.username + " (" + self.user.email + ")"

    def can_create_text(self):
        return user_can_create_text(self.user)

    def _created(self):
        return self.user.date_joined
    
    created = property(_created)
    
        
def duplicate_obj_or_list(to_dupli, new_dict={}):
    if isinstance(to_dupli, (list, set)):
        res = set()
        for oo in to_dupli:
            new_oo = duplicat_obj(oo, classes_to_duplicate, new_dict)
            res.add(new_oo)
        return res
    else:
        return duplicat_obj(to_dupli, classes_to_duplicate, new_dict)
        
def duplicate_obj(obj, new_dict={}):
    #fields = dict([ (field.name, _duplicate_obj_or_list(getattr(obj,field.name),classes_to_duplicate))  for field in obj._meta.fields])
    
    fields = dict([(key, value) for key, value in obj.__dict__.copy().items() if not key.startswith('_') and key != 'secret_key'])
    fields.update(new_dict)
    fields['id'] = None
    #print 'creating object',obj.__class__,fields
    new_obj = obj.__class__.objects.create(**fields)
    if hasattr(new_obj, 'created'):
        new_obj.created = obj.created
    if hasattr(new_obj, 'modified'):
        new_obj.modified = obj.modified
    new_obj.save()
    return new_obj 

class TextVersionManager(models.Manager):
    def duplicate(self, version, creator=None, keep_comments=True, keep_dates=True, fields={}):
        new_rev = duplicate_obj(version, fields)
        if creator:
            new_rev.creator = creator
        # comments
        if keep_comments:
            new_comments = set([Comment.objects.duplicate(cm) for cm in version.comment_set.all()])
            new_rev.comment_set = new_comments
        # images
        new_images = set([Image.objects.duplicate(i) for i in version.image_set.all()])
        new_rev.image_set = new_images
        # tags
        new_rev.tags = version.tags
        if not keep_dates:
            new_rev.created = datetime.datetime.now()                
            new_rev.modified = datetime.datetime.now()
        new_rev.save()
        return new_rev 
        
class TextVersion(models.Model):
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    #deleted = models.BooleanField(default=False)

    note = models.CharField(max_length=100, blank=True)
    
    title = models.TextField()
    content = models.TextField()
    spanned_content = models.TextField(null=True)
    css = models.TextField()

    creator = models.ForeignKey(User)

    # should be a text only 
    content_text = models.TextField(blank=True)
    
    comment_workflow = models.ForeignKey(Workflow, default=settings.DEFAULT_WORKFLOW_ID)

    text = models.ForeignKey("Text")

    tags = TagField()

    def save(self, force_insert=False, force_update=False):
        # compute spanned_content
        last_tv = None
        try:
            last_tv = TextVersion.objects.get(id=self.id)
        except ObjectDoesNotExist:
            pass
           
        if last_tv == None or self.content != last_tv.content :
            self.spanned_content = processContent(self.content)
 
        # set text modification time
        if last_tv == None or self.content != last_tv.content or self.title != last_tv.title:
            self.text.modified = datetime.datetime.now() 
            self.text.save()
        
        # save text version
        super(TextVersion, self).save(force_insert, force_update)

    def delete(self):
        # set text modification time
        self.text.modified = datetime.datetime.now() 
        self.text.save()

        # delete text version
        super(TextVersion, self).delete()
        
    def change_workflow(self, workflow):
         
        # change workflow if required 
        if workflow.id != self.comment_workflow_id :            
            old_workflow = self.comment_workflow
            self.comment_workflow = workflow
            self.save()
    
            # reinit comment state
            workflow = Workflow.objects.get(id=self.comment_workflow_id)
            ids = [state.id for state in workflow.states.all()]
            
            initial_state = State.objects.get(id=workflow.initial_state_id)
    
            comments = Comment.objects.filter(text_version=self)
            for comment in comments :
                old_state = comment.states.get().state
                if comment.states.get(content_type=ContentType.objects.get_for_model(Comment)).state.id not in ids :
                    comment.update_state(initial_state, silent=True)
                    # fire
                    post_comment_state_changed.send(sender=comment.__class__, instance=comment, old_state=old_state, state=initial_state, old_workflow=old_workflow)
    
            discussion_items = DiscussionItem.objects.filter(comment__text_version=self)
            for discussion_item in discussion_items :
                old_state = comment.states.get().state
                if discussion_item.states.get(content_type=ContentType.objects.get_for_model(DiscussionItem)).state.id not in ids :
                    discussion_item.update_state(initial_state, silent=True)
                    # fire
                    post_discussionitem_state_changed.send(sender=discussion_item.__class__, instance=discussion_item, old_state=old_state, state=initial_state, old_workflow=old_workflow)
                
    # ** links **
    # attach_set;
    # image_set
    
    def edit(self, new_title, new_note, new_tags, new_content, keep_comments):
        "Edit text version with new values, use clever algo to keep comments"
        old_content = self.content
        if not keep_comments :
            self.comment_set.all().delete()
        elif new_content != old_content:
            new_comments = self.comment_set.all() ;
            tomodify_comments, toremove_comments = compute_new_comment_positions(old_content, new_content, new_comments)
            [comment.save() for comment in tomodify_comments]
            [comment.delete() for comment in toremove_comments]
        self.title = new_title
        self.note = new_note
        self.tags = new_tags
        self.content = new_content
        self.save()

    #protected Set<Invitation> invitations;
    
    def get_spanned_content(self):
        if not self.spanned_content :
            raise Exception("A TextVersion had self.spanned_content == None, self.id is : %d" % self.id)
        return self.spanned_content
    

    def get_amendments(self):
        amendment_comments = Comment.objects.filter(text_version=self,
                            states__content_type=ContentType.objects.get_for_model(Comment),
                            states__state__name="amendment")
        amendment_dis = DiscussionItem.objects.filter(comment__text_version=self,
                            states__content_type=ContentType.objects.get_for_model(DiscussionItem),
                            states__state__name="amendment")
        return amendment_comments, amendment_dis

    # returns posts whatever state there in (never to be used for user interface purposes)
    def get_commentsandreplies(self):
        comments = self.comment_set.filter(states__content_type=ContentType.objects.get_for_model(Comment))
        dis = DiscussionItem.objects.filter(comment__id__in=[cc.id for cc in comments],
                                            states__content_type=ContentType.objects.get_for_model(DiscussionItem))
        return comments, dis

    # returns total number of posts whatever state there in (never to be used for user interface purposes)
    def get_commentsandreplies_count(self):
        comments, dis = self.get_commentsandreplies() ;
        return comments.count(), dis.count()
    get_commentsandreplies_count.short_description = '# comments'

    # returns  number of comments and replies visible for user 
    def get_visible_commentsandreplies(self, user):
        allowed_states_ids = [st.id for st in comment_states_with_perm_for_text('can_view_comment_local_text', user, self.id)]
        comments = self.comment_set.filter(states__content_type=ContentType.objects.get_for_model(Comment),
                            states__state__id__in=allowed_states_ids)
        dis = DiscussionItem.objects.filter(comment__id__in=[cc.id for cc in comments],
                                            states__content_type=ContentType.objects.get_for_model(DiscussionItem),
                                            states__state__id__in=allowed_states_ids)
        return comments, dis
    
    # returns  number of comments and replies visible for user 
    def get_visible_commentsandreplies_count(self, user):
        comments, dis = self.get_visible_commentsandreplies(user)
        return comments.count(), dis.count()

    # returns  number of comments and replies visible for anonymous user 
    def get_public_commentsandreplies(self):
        anonymous = AnonymousUser()  
        return self.get_visible_commentsandreplies(anonymous)
    
    # returns  number of comments and replies visible for anonymous user 
    def get_public_commentsandreplies_count(self):
        anonymous = AnonymousUser()  
        comments, dis = self.get_visible_commentsandreplies(anonymous)
        return (comments.count(), dis.count())

    def __unicode__(self):
        return self.title

    
    objects = TextVersionManager()
    
def get_perm_by_name_or_perm(perm):
    """
    if perm is Permission --> perm
    if perm is String --> the permission with perm as name
    """
    if isinstance(perm, Permission):
        return perm
    elif isinstance(perm, str):
        ctype = ContentType.objects.get_for_model(Text)
        permission = Permission.objects.filter(content_type=ctype, codename=perm)[0]
        return permission
    raise Exception("cannot get perm from object %s" % (str(perm)))

    
SEARCH_STRING_PARAM = 'q' 
TAGID_PARAM = 'tag_id' 
TAGPAGE_PARAM = 'tag_page_nb' 

START_SEL_KEY = '@@34@DSJLKUYHDS486U98UU0@'
END_SEL_KEY = '@@SDGJO89HGFGFYUU98UU0@'  
# see http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/docs/tsearch2-ref.html
HIGHLIGHT_OPTIONS = '\'StartSel=%s, StopSel=%s, MaxWords=55, MinWords=40, ShortWord=3, HighlightAll=FALSE\'' % (START_SEL_KEY, END_SEL_KEY)

QUERY_PARSING_CHARS = ['!', '(', ')', '&', '|']

def cleanup_query(query):
    "Cleanup query from query specific characters"
    # TODO : find a better way to do that ...
    for char in QUERY_PARSING_CHARS:
        query = query.replace(char, '')
    return query

class TextManager(models.Manager):
    def duplicate(self, text, creator):
        """
        Duplicate a text
        """
        new_text = duplicate_obj(text)
        new_text.creator = creator
        # versions
        new_versions = set([TextVersion.objects.duplicate(version, creator, True, True, {'text_id' : new_text.id}) for version in text.textversion_set.all()])
        new_text.TextVersion_set = new_versions
        # row roles : no duplication : just add me as owner
        self.create_ownership(new_text, creator)
        # re-create secret key
        new_text.update_new_secret_key()
        new_text.created = datetime.datetime.now()
        
        new_text.save()
        return new_text
    
    def create_text(self, user, title, content, tags=""):
        #default_workflow = Workflow.objects.get(id=4)
        
        # create the default version also        
        text = Text.objects.create(creator=user)
        text_version = TextVersion.objects.create(creator=user, text=text, title=title, content=content, tags=tags)
        
        # set ownership / create row local role
        self.create_ownership(text, user)
        return text
        
    def create_ownership(self, text, user):
        CREATOR_ROLE = Role.objects.filter(name="Owner")[0]
        ownership = ObjectUserRole.objects.create(role=CREATOR_ROLE, user=user, object=text)
        return ownership

    def full_text_search(self, search_string, queryset=None):
        query = cleanup_query(search_string)
        if not queryset:
            queryset = self.all()
            
        if settings.DATABASE_ENGINE in ['postgresql_psycopg2', 'postgresql']:
            # postgresql
            query = '&'.join([term.strip() for term in query.split() if term.strip()])
            # search in texts
            q_expr = "to_tsquery(%s)"

            search_texts = Text.objects.all().extra(select={
                                    'rank' : 'ts_rank(to_tsvector(content||title),%s)' % q_expr,
                                    'excerpt' : "ts_headline(cm_textversion.content,%s,%s)" % (q_expr, HIGHLIGHT_OPTIONS),
                                    },
                            tables=['cm_textversion'],
                            params=[query],
                            select_params=[query, query],
                            where=[
                                   'cm_textversion.text_id = cm_text.id',
                                   # only select the last revision ... might be a performance killer
                                   'not exists (select 1 from cm_textversion tv2 where tv2.text_id = cm_textversion.text_id and tv2.id > cm_textversion.id)',
                                   'content || title @@ %s ' % q_expr, ],
                            ).filter(id__in=[t.id for t in queryset]).order_by('rank')
        else:
            raise Exception('Unsupported database for full text queries')        
# following code is a simple attempt to support full text search with mysql...
# it should not be difficult but it's not our priority
# please contribute if you're interested

#        elif settings.DATABASE_ENGINE == 'mysql':       
#            query = ' '.join([term.strip() for term in query.split() if term.strip()])
#            # search in texts
#            search_texts = queryset.extra(select={
#                                    'rank' : "MATCH (content,title) AGAINST (%s)",
#                                    'excerpt' : "", # TODO : find a way to get a headline in mysql
#                                    },
#                            tables=['cm_textversion'],
#                            params=[query],
#                            select_params=[query],
#                            where=[
#                                   'cm_textversion.text_id = cm_text.id',
#                                   # only select the last revision ... might be a performance killer
#                                   'not exists (select 1 from cm_textversion tv2 where tv2.text_id = cm_textversion.text_id and tv2.id > cm_textversion.id)',
#                                   "MATCH (content,title) AGAINST (%s)",
#                                  ],
#                            ).filter(id__in = [t.id for t in queryset]).order_by('-rank')
                                       
        return search_texts
           
    def get_by_perm(self, user, perm, creator_user=None, exclude_all_have_perm=False):
        """
        Get the texts with 'perm' permissions for 'user' 
        created by 'creator_user' (if not None)
        exclude_all_have_perm means exclude texts when only everyone has permission 
        TODO : refactor like 
        http://groups.google.com/group/django-users/browse_thread/thread/a928d1db22c0e43f/8c5e36f515dd5c55?lnk=gst&q=generic+relation+filter#8c5e36f515dd5c55
        """
        perm = get_perm_by_name_or_perm(perm)
        if user and not user.is_anonymous():
            new_user_restriction = Q(row_roles__user__exact=user)
            if not exclude_all_have_perm:
                new_user_restriction = new_user_restriction | Q(row_roles__user__isnull=True)
        else:
            new_user_restriction = Q(row_roles__user__isnull=True)
        ctype = ContentType.objects.get_for_model(Text)
        texts = Text.objects.filter(Q(row_roles__role__permissions__exact=perm),
                                    Q(row_roles__content_type=ctype),
                                    new_user_restriction).distinct().order_by('-id')
                                    
        if creator_user:
            texts = texts.filter(creator=creator_user)
        texts = texts.distinct()
        return texts
        

def generate_secret_key(size=40):
    return ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ' 
                                + 'abcdefghijklmnopqrstuvwxyz'
                                + '0123456789'
                                ) for x in xrange(size)])
    #return sha.new(str(random.random())).hexdigest()

class Text(models.Model):
    active = models.BooleanField(default=True)
    modified = models.DateTimeField(null=True) #auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(User)    

    row_roles = generic.GenericRelation(ObjectUserRole)
    
    secret_key = models.CharField(default=generate_secret_key, max_length=40, unique=True)
    
    def has_perm(self, user, permission):
        return user_has_perm_on_text(user, permission, self.id)

        # inserted in initial_data now
        #permissions = (
        #    ("can_view_local_text", u"Can view local text"),
        #    ("can_comment_local_text", u"Can comment local text"),
        #    ("can_edit_local_text", u"Can edit local text"),
        #    ("can_delete_local_text", u"Can delete local text"),
        #)
        
    
    #def __init__(self,owner):
    #    models.Model.__init__(self)
    #    # create a text version
    #    self.owner = owner
    #    first_version = TextVersion(text = self)
    #    self.TextVersion_set.add(first_version)

    def version_number(self):
        return TextVersion.objects.filter(text__exact=self).count()

    def get_latest_version(self):
        return self.get_versions()[0]
    
    def get_versions(self):
        return TextVersion.objects.filter(text__exact=self).order_by('-created')

    def get_versions_number(self):
        return self.get_versions().count()
        
    def get_objectuserrole_number(self):
        return number_of_perm_on_text(self.id)
            
    def update_new_secret_key(self):
        self.secret_key = generate_secret_key()
        self.save()
        
    def __unicode__(self):
        return "%d '%s' (rev. %d)" % (self.id, self.get_latest_version().title, self.version_number())

    get_versions_number.short_description = "#versions"
    get_objectuserrole_number.short_description = "#perms"
    
    class Meta:
        pass

    objects = TextManager()

from django.core.files.base import ContentFile

class ImageManager(models.Manager):
    def create_image(self, text_version, filename, data):
        image = self.create(text_version=text_version)
        ff = ContentFile(data)
        image.data.save(filename, ff)
        return image

    def duplicate(self, image):
        filename = image.data.path.rsplit(os.path.sep, 1)[1]
        data = open(image.data.path).read()
        new_image = self.create_image(image.text_version, filename, data)
        return new_image
    
class Image(models.Model):
    data = models.ImageField(upload_to="images/%Y/%m/%d/", max_length=1000)
    text_version = models.ForeignKey(TextVersion)

    def get_url(self):
        return reverse('text-image', args=[self.id])
    
    objects = ImageManager()
    
post_comment_created = django.dispatch.Signal(providing_args=["instance", "state"])
post_comment_state_changed = django.dispatch.Signal(providing_args=["instance", "old_state", "old_workflow", "state"])

class CommentManager(models.Manager):
    def duplicate(self, comment):
        
        new_comment, new_object_state = self.create_comment(comment.creator_id, comment.start_word, comment.end_word, comment.username, comment.email, comment.title, comment.content, comment.text_version_id, comment.created)
        object_state = ObjectState.objects.get(
                                           Q(object_id__exact=comment.id),
                                           Q(content_type=ContentType.objects.get_for_model(Comment))
                                           )
        new_object_state.state_id = object_state.state_id
        new_object_state.save()
        
        # discution items
        new_di = set([DiscussionItem.objects.duplicate(di) for di in comment.discussionitem_set.all()])
        new_comment.discussionitem_set = new_di

        # tags
        new_comment.tags = comment.tags ;

        new_comment.save()
        return new_comment

    def create_comment(self, creatorId, start_word, end_word, username, email, title, content, version_id, created=None):
        if created:
            comment = Comment.objects.create(text_version_id=version_id, creator_id=creatorId, title=title, content=content, start_word=start_word, end_word=end_word, username=username, email=email, created=created)
        else:
            comment = Comment.objects.create(text_version_id=version_id, creator_id=creatorId, title=title, content=content, start_word=start_word, end_word=end_word, username=username, email=email)
        #if created:
        #    comment.created = created
        #    comment.save()
        textVersion = TextVersion.objects.get(id=version_id)
        object_state = ObjectState.objects.create(state=textVersion.comment_workflow.initial_state, object=comment)
        
        # fire post comment created
        post_comment_created.send(sender=self.__class__, instance=comment, state=object_state.state)
        
        return comment, object_state 
        
    def exists_past_comment_with_same_date(self, comment):
        res = self.filter(id__lt=comment.id, text_version__text=comment.text_version.text, created=comment.created)
        return len(res) > 0 
        

class Comment(models.Model):
    active = models.BooleanField(default=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=datetime.datetime.now)
    #deleted = models.BooleanField(default=False)

    start_word = models.IntegerField();
    end_word = models.IntegerField();

    #this will always be not null and non empty when created from a user that wasn't logged
    username = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=200, null=True)

    creator = models.ForeignKey(User, null=True)    

    text_version = models.ForeignKey(TextVersion)
    
    content = models.TextField()
    title = models.TextField()

    tags = TagField()
    
    # one only
    states = generic.GenericRelation(ObjectState)
    
    def update_state(self, new_state, silent=False) :
        object_state = ObjectState.objects.filter(
                                           Q(object_id__exact=self.id),
                                           Q(content_type=ContentType.objects.get_for_model(Comment))
                                           )[0]
        old_state = object_state.state                                           
        object_state.state = new_state
        object_state.save()
        
        # fire post_comment_state_changed
        if not silent:
            post_comment_state_changed.send(sender=self.__class__, instance=self, old_state=old_state, state=new_state, old_workflow=None)

        return object_state 
    
    # this function checks that a user (with no special right) can edit the comment
    # for that : user must be logged in, author of the comment, comment should be in the initial state of workflow and should not have any reply  
    # any change here should be also implemented in the js client  
    def canAuthorEdit(self, user) :
        if user.is_authenticated() and self.creator == user : # user logged in, and author of comment
            state = self.states.get().state
            if state == self.text_version.comment_workflow.initial_state :
                allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', user, self.text_version.id)
                discussionItems = DiscussionItem.objects.filter(Q(comment = self),
                                                   Q(states__state__id__in=[t.id for t in allowed_states]))
                if len(discussionItems) == 0 : 
                    return True
        return False 
    
#    def delete(self) :
#        # for some reason the removal of comments do remove the replies (doc says its regular django behavior) 
#        # for some reason the removal of a di does remove the tags because its coded in diobjectmanager delete()
#        # BUT removing the comment does not trigger the removal of tags on reply !!!! 
#        # consult RBA
##        DiscussionItem.objects.filter(
##                                  Q(comment_id__exact = self.id)
##                                  ).delete()
#        TaggedItem.objects.filter(
#                                  Q(object_id__exact = self.id),
#                                  Q(content_type = ContentType.objects.get_for_model(Comment))
#                                  ).delete()
#        models.Model.delete(self)
    
    def __unicode__(self):
        return "%s (text %d)" % (self.title, self.text_version.text.id)

    objects = CommentManager()
    
post_discussionitem_state_changed = django.dispatch.Signal(providing_args=["instance", "old_state", "old_workflow", "state"])
post_discussionitem_created = django.dispatch.Signal(providing_args=["instance", "state"])
    
class DiscussionItemManager(models.Manager):
    def duplicate(self, di):
        new_discussionitem, new_object_state = self.create_discussionitem(di.comment, di.creator_id, di.title, di.content, di.username, di.email, di.created)
        object_state = ObjectState.objects.get(
                                           Q(object_id__exact=di.id),
                                           Q(content_type=ContentType.objects.get_for_model(DiscussionItem))
                                           )
        new_object_state.state_id = object_state.state_id
        new_object_state.save()
        
        # tags
        new_discussionitem.tags = di.tags ;
        
        new_discussionitem.save()
        return new_discussionitem
    
    def create_discussionitem(self, comment, creatorId, title, content, username, email, created=None):
        if created:
            discussionItem = DiscussionItem.objects.create(comment=comment, creator_id=creatorId, title=title, content=content, username=username, email=email, created=created)
        else:
            discussionItem = DiscussionItem.objects.create(comment=comment, creator_id=creatorId, title=title, content=content, username=username, email=email)
        #if created:
        #    discussionItem.created = created
        #    discussionItem.save()
        assert not created or discussionItem.created == created, 'Create discussionitem created problem'

        object_state = ObjectState.objects.create(state=comment.text_version.comment_workflow.initial_state, object=discussionItem)
        
        # fire post comment created
        post_discussionitem_created.send(sender=self.__class__, instance=discussionItem, state=object_state.state)
        
        return discussionItem, object_state
 
    def exists_past_discussionitem_with_same_date(self, discussionitem):
        res = self.filter(id__lt=discussionitem.id, comment__text_version__text=discussionitem.comment.text_version.text, created=discussionitem.created)
        return len(res) > 0 


class DiscussionItem(models.Model):
    active = models.BooleanField(default=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=datetime.datetime.now)

    #this will always be not null and non empty when created from a user that wasn't logged
    username = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=200, null=True)

    creator = models.ForeignKey(User, null=True)    

    comment = models.ForeignKey(Comment)
   
    content = models.TextField(default="")
    title = models.TextField(default="")
    
    tags = TagField()
    
    # one only
    states = generic.GenericRelation(ObjectState)
    
    # this function checks that a user (with no special right) can edit the DiscussionItem di
    # for that : user must be logged in, author of di, di should be in the initial state of workflow and should not have any other reply  
    # any change here should be also implemented in the js client  
    def canAuthorEdit(self, user) :
        if user.is_authenticated() and self.creator == user : # user logged in, and author of comment
            state = self.states.get().state
            if state == self.comment.text_version.comment_workflow.initial_state :
                allowed_states = comment_states_with_perm_for_text('can_view_comment_local_text', user, self.comment.text_version.id)
                discussionItems = DiscussionItem.objects.filter(Q(comment = self.comment),
                                                    Q(states__state__id__in=[t.id for t in allowed_states])
                                                   ).order_by('created')
                if len(discussionItems) > 0 and discussionItems[len(discussionItems)-1].id == self.id : 
                    return True
        return False 

    def update_state(self, new_state, silent=False) :
        object_state = ObjectState.objects.filter(
                                           Q(object_id__exact=self.id),
                                           Q(content_type=ContentType.objects.get_for_model(DiscussionItem))
                                           )[0]
        old_state = object_state.state
        object_state.state = new_state
        object_state.save()
        
        # fire post_comment_state_changed
        if not silent:
            post_discussionitem_state_changed.send(sender=self.__class__, instance=self, old_state=old_state, state=new_state, old_workflow=None)
        
        return object_state
     
#    def delete(self) :
#        TaggedItem.objects.filter(
#                                  Q(object_id__exact = self.id),
#                                  Q(content_type = ContentType.objects.get_for_model(DiscussionItem))
#                                  ).delete()
#        
#        models.Model.delete(self)
    
    objects = DiscussionItemManager()

    def __unicode__(self):
        return "%s (comment %d, text %d)" % (self.title, self.comment.id, self.comment.text_version.text.id)

class Email(models.Model):
    """
    Simple (no multipart support) email storage
    """
    created = models.DateTimeField(auto_now_add=True)

    subject = models.TextField()
    body = models.TextField()
    from_email = models.CharField(max_length=100)
    to = models.TextField()
    bcc = models.TextField()
    
    def get_recipents_number(self):
        from cm.utils.mail import LIST_SEP
        res = 0
        if self.to:
            res = len(self.to.split(LIST_SEP))
        if self.bcc:
            res += len(self.bcc.split(LIST_SEP))
        return res
      
    get_recipents_number.short_description = "#recipients"
    
    def __unicode__(self):
        return ' '.join([self.from_email, self.to, self.subject])

class EmailAlertManager(models.Manager):
    def create_alert(self, user, text):
        alert, _ = self.get_or_create(user=user, text=text)
        if not alert.subscribed:
            alert.subscribed = True
            alert.save()            
        return alert
    
    def delete_alert(self, user, text):
        try:
            alert = self.get(user=user, text=text)
            alert.subscribed = False
            alert.save()
            return 0
        except EmailAlert.DoesNotExist:
            return 1                    
    
    def get_alerts(self, text):
        return self.filter(text=text, subscribed=True)
    
    def get_user_alerts(self, user, text):
        return self.filter(text=text, user=user, subscribed=True)
    
    def delete_alert_by_key(self, key):
        """
        Delete alert and returns text
        """
        try:
            alert = self.get(secret_key=key)
            text = alert.text
            alert.subscribed = False
            alert.save()
            return text
        except EmailAlert.DoesNotExist:
            return None
    
class EmailAlert(models.Model):
    """
    Users' alerts on texts
    """
    created = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, null=False)
    
    text = models.ForeignKey(Text, null=False)

    # subscribed indicates whether this subscription is active or not
    # so we preserve the secret_key among subscriptions for same text
    subscribed = models.BooleanField(default=True)
    
    secret_key = models.CharField(default=generate_secret_key, max_length=40, unique=True, db_index=True)
    
    def __unicode__(self):
        return "%i (email alert %d %d)" % (self.id, self.user.id, self.text.id)

    def get_unsubscribe_url(self):
        unsubscribe_url = reverse('emailalert-remove', args=[self.secret_key])
        return unsubscribe_url
        
    objects = EmailAlertManager()    
    
#########################################
# perms

def user_can_create_text(user):
    if not user.is_anonymous():
        nb_text_max = user.get_profile().get_max_number_text()
        nb_texts = Text.objects.filter(creator=user).count()
        return nb_texts < nb_text_max 
    else:
        return False

def user_has_perm_on_text(user, permission, text_id):
    if user and user.is_staff :
        return True 
    permission = get_perm_by_name_or_perm(permission)
    if user and not user.is_anonymous():
        user_restriction = Q(user__exact=user) | Q(user__isnull=True)
    else:
        user_restriction = Q(user__isnull=True)
    
    return ObjectUserRole.objects.filter(
                                       Q(role__permissions__exact=permission),
                                       Q(object_id__exact=text_id),
                                       Q(content_type=ContentType.objects.get_for_model(Text)),
                                       user_restriction,
                                       ).distinct().count() > 0

# states_with_perm_for_workflow('can_view_comment_local_text', user, workflow, text_id):
def comment_states_with_perm_for_text(permission, user, version_id):
    """
    for user and text return states offering requested permission
    """
    textVersion = TextVersion.objects.get(id=version_id)
    workflow = textVersion.comment_workflow 
    return comment_states_with_perm_for_workflow(permission, user, workflow, textVersion.text.id)

def comment_states_with_perm_for_workflow(permission, user, workflow, text_id):
    """
    for user and text return states offering requested permission
    """
    perm = get_perm_by_name_or_perm(permission)
    
    if user and not user.is_anonymous():
        user_restriction = Q(staterolepermissions__role__objectuserrole__user__exact=user) | Q(staterolepermissions__role__objectuserrole__user__isnull=True)
    else:
        user_restriction = Q(staterolepermissions__role__objectuserrole__user__isnull=True)

    states = State.objects.filter(
                               Q(workflow__exact=workflow),
                               Q(staterolepermissions__permissions__exact=perm),
                               Q(staterolepermissions__role__objectuserrole__object_id__exact=text_id),
                               Q(staterolepermissions__role__objectuserrole__content_type=ContentType.objects.get_for_model(Text)),
                               user_restriction,
                               ).distinct()
    return states 

#def row_level_for_perm_by_user(permission, text_id):
#    """
#    returns row level objects providing given permission for user
#    """
#    permission = get_perm_by_name_or_perm(permission)
#    rl = ObjectUserRole.objects.filter(
#                                       Q(role__permissions__exact = permission),
#                                       Q(object_id__exact = text_id),
#                                       Q(content_type = ContentType.objects.get_for_model(Text)),
#                                       Q(user__isnull = False),
#                                       ).distinct()
#    return rl
    
def number_of_perm_on_text(text_id):
    return ObjectUserRole.objects.filter(
                                       Q(object_id__exact=text_id),
                                       Q(content_type=ContentType.objects.get_for_model(Text)),
                                       ).count()
        
def user_ids_has_perm_on_text(permission, text_id):
    """
    returns user ids with such permission on this text
    """
    permission = get_perm_by_name_or_perm(permission)
    users_having_perm = User.objects.filter(Q(objectuserrole__object_id=text_id),
                                            Q(objectuserrole__content_type=ContentType.objects.get_for_model(Text)),
                                            Q(objectuserrole__user__isnull=False),
                                            Q(objectuserrole__role__permissions__exact=permission),
                                            ).distinct()
    return users_having_perm

    
def number_has_perm_on_text(permission, text_id):
    """
    returns number of (real) users with such permission on this text
    """
    return user_ids_has_perm_on_text(permission, text_id).count()

def user_can_share_new_text(user):
    """
    Does this user have the right to share a new text ?
    """
    return user_can_share_text(user, None)

def user_can_share_text(user, text):
    """
    Does this user have the right to share this text:
    if text is already shared : yes
    if not : see limitation
    """
    if not user.is_anonymous():
        # if text is already shared : True
        if text:
            is_text_shared = ObjectUserRole.objects.filter(
                                               Q(object_id__exact=text.id),
                                               Q(content_type=ContentType.objects.get_for_model(Text)),
                                               ).exclude(
                                                 Q(user__exact=user.id) | Q(user__isnull=True),
                                               ).distinct().count() > 0
            if is_text_shared:
                return True
        
        # if not, see restrictions if get_max_shared_number_text
        nb_max_shared_text = user.get_profile().get_max_shared_number_text()

        nb_shared_texts = Text.objects.filter(creator=user).exclude(Q(row_roles__user=user) | Q(row_roles__user__isnull=True)).distinct().count()
        return nb_shared_texts < nb_max_shared_text 
    else:
        return False

def user_can_add_participant(user, text):
    """
    Can this user add a participant
    """
    if not user.is_anonymous():
        nb_users_shared = User.objects.filter(objectuserrole__object_id=text.id,
                                                objectuserrole__content_type=ContentType.objects.get_for_model(Text),
                                                objectuserrole__user__isnull=False,
                                                ).exclude(id=user.id).distinct().count()
        return nb_users_shared < user.get_profile().get_max_collaborators_text()                                            
    else:
        return False

# this is called twice TODO : figure out why (http://code.djangoproject.com/ticket/3951)
def on_taggeditem_pre_delete(sender, instance, **kwargs):
    #   passing an instance to get_for_model works fine
    TaggedItem.objects.filter(
                              Q(object_id__exact=instance.id),
                              Q(content_type=ContentType.objects.get_for_model(instance))
                              ).delete()

from django.db.models import signals

from cm.utils.cache import tag_cloud_reset
from cm.email_alerts import comment_created, textversion_created, state_changed

def connect_all():
    signals.pre_delete.connect(on_taggeditem_pre_delete, sender=TextVersion)
    signals.pre_delete.connect(on_taggeditem_pre_delete, sender=Comment)
    signals.pre_delete.connect(on_taggeditem_pre_delete, sender=DiscussionItem)

    signals.post_delete.connect(tag_cloud_reset, sender=TextVersion)
    signals.post_save.connect(tag_cloud_reset, sender=TextVersion)

    signals.post_delete.connect(tag_cloud_reset, sender=Text)
    signals.post_save.connect(tag_cloud_reset, sender=Text)

    signals.post_delete.connect(tag_cloud_reset, sender=ObjectUserRole)
    signals.post_save.connect(tag_cloud_reset, sender=ObjectUserRole)
    
    ## email alerts
    # comment creation
    post_comment_created.connect(comment_created, sender=CommentManager)
    # discussionitem creation
    post_discussionitem_created.connect(comment_created, sender=DiscussionItemManager)    
    # comment state changed  
    post_comment_state_changed.connect(state_changed, sender=Comment)
    # discussionitem state changed
    post_discussionitem_state_changed.connect(state_changed, sender=DiscussionItem)
    # text_version changed
    signals.post_save.connect(textversion_created, sender=TextVersion)    
    
connect_all()
