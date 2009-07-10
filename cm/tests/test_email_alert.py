import unittest
from time import sleep
from cm.models import *
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.core import management

class EmailAlertTestCase(unittest.TestCase):
    #fixtures = ['test.json']
    
    def setUp(self):
        management.call_command('loaddata', 'test.json', verbosity=0)
        self.user1, _ = User.objects.get_or_create(username="username1")
        self.user2, _ = User.objects.get_or_create(username="username2")
        self.user3, _ = User.objects.get_or_create(username="username3")
        self.user100, _ = User.objects.get_or_create(username="username100")
        self.text1 = Text.objects.create_text(user=self.user1, title="title1", content="content1")
        self.text_version1 = self.text1.get_latest_version()
        self.client = Client()

    def test_alert_creation(self):
        # assert not trash : delete and not alert
        self.assertEquals(EmailAlert.objects.delete_alert(self.user1, self.text1), 1)
        
        # assert ok : create & delete
        EmailAlert.objects.create_alert(self.user1, self.text1)
        self.assertEquals(EmailAlert.objects.delete_alert(self.user1, self.text1), 0)

        # create 2 alerts
        EmailAlert.objects.create_alert(self.user1, self.text1)
        EmailAlert.objects.create_alert(self.user2, self.text1)

        self.assertEquals(len(EmailAlert.objects.get_alerts(self.text1)), 2)
        users = [a.user for a in EmailAlert.objects.get_alerts(self.text1)]
        self.assertTrue(self.user1 in users)
        self.assertTrue(self.user2 in users)

    def test_alert_email_duplicate(self):
        """
        Test that duplicating a text does not trigger unnecessary emails (because
        comments & discussion items are recreated)
        """
        mail.outbox = []
        EmailAlert.objects.create_alert(self.user1, self.text1)
        # give ownership to user100 to have 2 user subscribed
        Text.objects.create_ownership(self.text1, self.user100)
        EmailAlert.objects.create_alert(self.user100, self.text1)
        
        c1, os1 = Comment.objects.create_comment(creatorId=self.user1.id , start_word=1, end_word=1, username='', email='', title='title', content='cc', version_id=self.text_version1.id)
        self.assertEquals(len(mail.outbox), 2)
        
        d1, os2 = DiscussionItem.objects.create_discussionitem(comment=c1, creatorId=self.user1.id, title='title', content='cc', username="", email="")
        self.assertEquals(len(mail.outbox), 4)
        
        self.assertEquals(EmailAlert.objects.delete_alert(self.user1, self.text1), 0)
        d1, os2 = DiscussionItem.objects.create_discussionitem(comment=c1, creatorId=self.user1.id, title='title', content='cc', username="", email="")
        self.assertEquals(len(mail.outbox), 5)
        
        # test that only the new version email is sent, not
        # duplication of past comments & discussionitems
        TextVersion.objects.duplicate(self.text_version1)
        self.assertEquals(len(mail.outbox), 6)
   
        self.assertEquals(len(EmailAlert.objects.get_alerts(self.text1)), 1)

    def test_remove_alert_by_url(self):
        mail.outbox = []
        self.assertEquals(len(EmailAlert.objects.get_alerts(self.text1)), 0)    
        alert = EmailAlert.objects.create_alert(self.user1, self.text1)
        EmailAlert.objects.create_alert(self.user2, self.text1)
        self.assertEquals(len(EmailAlert.objects.get_alerts(self.text1)), 2)

        url = alert.get_unsubscribe_url()
        response = self.client.get(url)
        self.assertEquals(len(EmailAlert.objects.get_alerts(self.text1)), 1)
        
    def test_access_rights(self):
        """
        user2 cannot read text: alert not effective 
        """
        mail.outbox = []        
        self.assertEquals(len(mail.outbox), 0)
        EmailAlert.objects.create_alert(self.user2, self.text1)
        self.assertEquals(len(EmailAlert.objects.get_alerts(self.text1)), 1)

        c1, os1 = Comment.objects.create_comment(creatorId=self.user1.id , start_word=1, end_word=1, username='', email='', title='title', content='cc', version_id=self.text_version1.id)

        # no mail sent
        self.assertEquals(len(mail.outbox), 0)

    def test_not_active_no_alert(self):
        """
        user3 is set unactive: alert not effective
        """
        mail.outbox = []
        self.assertEquals(len(mail.outbox), 0)
        EmailAlert.objects.create_alert(self.user1, self.text1)
        self.user1.is_active = False
        self.user1.save()
        self.assertEquals(len(EmailAlert.objects.get_alerts(self.text1)), 1)

        c1, os1 = Comment.objects.create_comment(creatorId=self.user1.id , start_word=1, end_word=1, username='', email='', title='title', content='cc', version_id=self.text_version1.id)

        # no mail sent
        self.assertEquals(len(mail.outbox), 0)
        
    def test_double_subscribe(self):
        alert1 = EmailAlert.objects.create_alert(self.user1, self.text1)
        EmailAlert.objects.delete_alert(self.user1, self.text1)

        alert2 = EmailAlert.objects.create_alert(self.user1, self.text1)
        
        # same key
        self.assertEquals(alert1.get_unsubscribe_url(), alert2.get_unsubscribe_url())
       
    def test_workflow_state_change(self):
        """
        Make sure change in workflow resulting in making a comment visible
        gets published by email alert system
        1. change on comment
        2. change workflow text settings
        """        
        alert1 = EmailAlert.objects.create_alert(self.user2, self.text1)
        self.user2.is_active = True
        self.user2.save()        
        # put text into 'a priori workflow'
        workflow = Workflow.objects.get(id=1)
        self.text_version1.comment_workflow = workflow
        self.text_version1.save()

        # user2 is commentator
        role = Role.objects.filter(name="Commenter")[0]
        comenter = ObjectUserRole.objects.create(role=role, user=self.user2, object=self.text1)

        #### 1
        c1, os1 = Comment.objects.create_comment(creatorId=self.user1.id , start_word=1, end_word=1, username='', email='', title='title', content='cc', version_id=self.text_version1.id)
        
        # no mail sent yet (comment is private)
        self.assertEquals(len(mail.outbox), 0)

        new_state = State.objects.get(id=3) # 2: published
        object_state = c1.update_state(new_state)

        # mail sent (fired by workflow state change)
        self.assertEquals(len(mail.outbox), 1)

        #### 2
        mail.outbox = []
        # create pending comment
        c2, os2 = Comment.objects.create_comment(creatorId=self.user1.id , start_word=1, end_word=1, username='', email='', title='title', content='cc', version_id=self.text_version1.id)

        # no mail sent yet (comment is private)
        self.assertEquals(len(mail.outbox), 0)

        a_posteriori_workflow = Workflow.objects.get(id=2)
        self.text_version1.change_workflow(a_posteriori_workflow)

        # mail sent (fired by workflow state change)
        self.assertEquals(len(mail.outbox), 1, "reinit_comment_state did not trigger email alert")
