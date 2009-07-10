from unittest import TestCase as TestCase2 
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.core import management
from cm.models import Text

class AccountTest(TestCase2):
    # it should be done extending TestCase
    # and uncommenting the following line ...
    #fixtures = ['test.json']
    # but this does not work so we manually load the test fixture
    
    def setUp(self):
        self.client = Client()

    def test_login(self):
        management.call_command('loaddata','test.json', verbosity=0)
        response = self.client.get('/')        
        nb_users = len(User.objects.all())
        self.assertNotEqual(nb_users,0)
        
        response = self.client.get('/accounts/profile/')
        self.failUnlessEqual(response.status_code, 302) # should redirect
        
        self.client.login(username='user', password='asasas')
        response = self.client.get('/accounts/profile/')
        self.failUnlessEqual(response.status_code, 200)
        #self.failUnlessEqual(response.status_code, 200)
        #response = self.client.post('/accounts/login/', {'username': 'john', 'password': 'smith'})
        #self.failUnlessEqual(response.status_code, 200)
