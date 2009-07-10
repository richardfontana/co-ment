import unittest
from cm.models import *
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.user1,_ = User.objects.get_or_create(username = "username1")
        self.text1 = Text.objects.create_text(user = self.user1, title = "title", content="content")
        self.text_version1 = self.text1.get_latest_version()

    def testCommentAndDiscutionStructure(self):
        self.comment1 = Comment.objects.create(start_word=1,end_word=3,text_version=self.text_version1)
        
    def testversionStructure(self):   
        THE_TITLE = "my title"
        self.assertTrue(len(self.text1.textversion_set.all())==1)
        # change title
        self.text_version1.title = THE_TITLE
        self.text_version1.save()
        ## create new version with copy     
        # self.text_version2 = self.text1.create_new_version()        
        # self.assertTrue(len(self.text1.TextVersion_set.all())==2)
        # self.assertEqual(self.text1.get_latest_version().title,THE_TITLE)
        ## create new version without copy
        # self.text_version2 = self.text1.create_new_version(copy=False)
        # self.assertEqual(self.text1.get_latest_version().title,"")

class TestPermsTestCase(unittest.TestCase):    
    def setUp(self):
        self.user1,_ = User.objects.get_or_create(username = "username2")
        self.user2,_ = User.objects.get_or_create(username = "username22")
        self.user3,_ = User.objects.get_or_create(username = "username23")
        self.text1 = Text.objects.create_text(user = self.user1, title = "title", content="content")
        self.text_version1 = self.text1.get_latest_version()

    def testCheckPerm(self):
        # create role and add permission to it
        self.role1 = Role.objects.create(order=60)
        self.role1.name = "role1"
        self.role1.save()
        ctype = ContentType.objects.get_for_model(Text)        
        self.perm1 = Permission.objects.create(content_type=ctype,codename="xxx_can_comment")
        self.perm2 = Permission.objects.create(content_type=ctype,codename="xxx_can_view")
        self.role1.permissions.add(self.perm1)
        
        # create row local role
        self.row_level_role1 = ObjectUserRole.objects.create(role=self.role1, 
                                                           user = self.user1,
                                                           object = self.text1,
                                                           )
        self.assertTrue(self.text1.has_perm(self.user1,self.perm1))
        self.assertFalse(self.text1.has_perm(self.user2,self.perm1))
        self.assertFalse(self.text1.has_perm(self.user3,self.perm1))
        self.assertFalse(self.text1.has_perm(self.user1,self.perm2))
        self.assertFalse(self.text1.has_perm(self.user2,self.perm2))
        
    def testCheckOwnership(self):
        """
        Verif creation gets all owner's permissions
        """
        owner_role = Role.objects.filter(name = "Owner")[0]
        row_level_role = ObjectUserRole.objects.filter(role = owner_role)[0]
        for perm in row_level_role.role.permissions.all():
            self.assertTrue(self.text1.has_perm(self.user1,perm))

class TestDuplicateTestCase(unittest.TestCase):    
    def setUp(self):
        self.user1,_ = User.objects.get_or_create(username = "username2")
        self.user2,_ = User.objects.get_or_create(username = "username22")
        self.user3,_ = User.objects.get_or_create(username = "username23")
        self.text1 = Text.objects.create_text(user = self.user1, title = "title", content="content")
        self.text_version1 = self.text1.get_latest_version()

    def testDuplicate(self):
        # duplicate text
        nb_text_versions = TextVersion.objects.all().count()
        text2 = Text.objects.duplicate(self.text1, self.user1)
        self.assertEquals(TextVersion.objects.all().count(),nb_text_versions + 1)

        # attach some comment & discut
        c1,os1 = Comment.objects.create_comment(creatorId = self.user1.id , start_word=1,end_word=1, username='', email='', title = 'title', content = 'cc', version_id = self.text_version1.id)
        d1,os2 = DiscussionItem.objects.create_discussionitem(comment = c1, creatorId= self.user1.id, title = 'title', content = 'cc', username="", email="")
        c_counts = DiscussionItem.objects.all().count()
        
        # duplicate textversion
        textversion2 = TextVersion.objects.duplicate(self.text_version1, self.user1, True)
        
        
        # make sure duplication preserves creation dates
        # not text creation date ! self.assertEquals(text2.created,self.text1.created)
        self.assertEquals(textversion2.created,self.text_version1.created)
        self.assertEquals(textversion2.comment_set.all()[0].created,self.text_version1.comment_set.all()[0].created)
        self.assertEquals(textversion2.comment_set.all()[0].discussionitem_set.all()[0].created,
                          self.text_version1.comment_set.all()[0].discussionitem_set.all()[0].created)

        self.assertEquals(textversion2.creator,self.user1)
        self.assertEquals(TextVersion.objects.all().count(),nb_text_versions + 2)
        
        # duplicate image
        data = open("cm/tests/data/1.png").read()
        name = "1.png"
        image1 = Image.objects.create_image(textversion2, name,data)
        image2 = Image.objects.duplicate(image1)
        # real duplication
        self.assertNotEquals(image1.data.path,image2.data.path)

        # check that duplication of textversion creates new image
        counts = Image.objects.all().count()
        image1.text_version = self.text_version1
        image1.save()
        textversion3 = TextVersion.objects.duplicate(self.text_version1, self.user1, True)
        self.assertEquals(Image.objects.all().count(),counts + 1)
        
        #
        today = datetime.today() 
        c3,os3 = Comment.objects.create_comment(creatorId = self.user1.id , start_word=1,end_word=1, username='', email='', title = 'title', content = 'cc', version_id = self.text_version1.id, created = today)
        self.assertEquals(c3.created,today)

