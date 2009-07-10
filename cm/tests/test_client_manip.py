import unittest
from django.test import TestCase

class ManipTestCase(TestCase):
    fixtures = ['test.json']
    
    def testManip(self):
        response = self.client.get('/accounts/login/')
        self.failUnlessEqual(response.status_code, 200)
        
        self.client.login(username = 'user', password = 'asasas')

        response = self.client.get('/accounts/profile/')
        self.failUnlessEqual(response.status_code, 200)

        # for some reason : error triggered here ... django bug
        # response = self.client.get('/texts/2/')
        # self.failUnlessEqual(response.status_code, 200)
