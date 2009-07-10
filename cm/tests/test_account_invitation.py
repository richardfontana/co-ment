import unittest
from cm.models import *
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.core import management

class InvitationTestCase(unittest.TestCase):
    #fixtures = ['test.json']
    
    def setUp(self):
         self.client = Client()

    def reg(self, username, do_activate):
        # register 
        self.client.post('/accounts/register/', {'email': '%s@sopinspace.com' % username,
                                                 'username': username,
                                                 'preferred_language':'fr',
                                                 'password':username,
                                                 'password2':username,
                                                 'tos':'on'})
        # do not activate
        if do_activate :
            self.activate(username)

    def activate(self, username):
        self.client.get('/activate/' + Profile.objects.get(user__username=username).activation_key + '/', {})

    def reg_log_createtxt_invite(self, username, username_toinvite, text_title):
        # register 
        self.client.post('/accounts/register/', {'email': '%s@sopinspace.com' % username,
                                                 'username': username,
                                                 'preferred_language':'fr',
                                                 'password':username,
                                                 'password2':username,
                                                 'tos':'on'})
        # activate 
        self.client.get('/activate/' + Profile.objects.get(user__username=username).activation_key + '/', {})
        # login 
        # RBA ? self.client.login(username='rberbe', password='rberbe')
        self.client.login(username=username, password=username)
        
        # create text 
        self.client.post('/text/add/', {'title': text_title,
                                        'content': 'content',
                                        'tags': 'toto',
                                        'continueediting':'0'})
        text_id = TextVersion.objects.get(title=text_title).text_id
        
        # invite rbe2 
        self.client.post('/text/%d/settings/' % text_id, {'form': 'add',
                                                          'new_emails': '%s@sopinspace.com' % username_toinvite,
                                                          'role_add': '2',
                                                          'invite':'on'})

        self.client.logout()

    def test_account_invitation(self):
        self.reg('usr2', False)
        self.reg_log_createtxt_invite('usr1', 'usr2', 'tit0')  
        
        self.reg('usr3', True)
        self.reg_log_createtxt_invite('usr4', 'usr3', 'tit1')  
        
        self.reg_log_createtxt_invite('usr5', 'usr6', 'tit2')  
        self.reg('usr6', False)
        
        self.reg_log_createtxt_invite('usr7', 'usr8', 'tit3')  
        self.reg('usr8', True)
        
        self.failUnlessEqual(User.objects.filter(email='usr2@sopinspace.com').count(), 1)
        self.failUnlessEqual(User.objects.filter(email='usr3@sopinspace.com').count(), 1)
        self.failUnlessEqual(User.objects.filter(email='usr6@sopinspace.com').count(), 1)
        self.failUnlessEqual(User.objects.filter(email='usr8@sopinspace.com').count(), 1)

    def test_share_with_inactive(self):
        """
        Test nasty bug when editing profile: put existing username and email
        """
        self.reg_log_createtxt_invite('usr11', 'usr12', 'tit10')
          
        self.failUnlessEqual(User.objects.filter(email='usr12@sopinspace.com').count(), 1)
        self.failUnlessEqual(User.objects.get(email='usr12@sopinspace.com').is_active, False)
        self.reg('usr12', True)
        self.reg('usr13', True)
        
        self.client.login(username="usr13",password="usr13")
        
        res = self.client.post('/accounts/profile/', {'email': 'usr12@sopinspace.com',
                                                      'allow_contact' : True,
                                                      'preferred_language': 'fr',
                                                      'username': "usr12"})
        
        self.failUnlessEqual(User.objects.filter(email='usr12@sopinspace.com').count(), 1)
        # register 
