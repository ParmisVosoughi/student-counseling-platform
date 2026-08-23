import os
os.environ.setdefault('USE_SQLITE','True')
from django.test import TestCase
from rest_framework.test import APIClient
from .models import User,SupervisorProfile,AdvisorProfile

class AuthAndUserTests(TestCase):
    def setUp(self):
        self.admin=User.objects.create_user('admin','admin@test.local','StrongPass123!',role='ADMIN')
        self.sup=User.objects.create_user('sup','sup@test.local','StrongPass123!',role='SUPERVISOR'); SupervisorProfile.objects.create(user=self.sup)
        self.client=APIClient()
    def test_login_returns_access_and_refresh_cookie(self):
        r=self.client.post('/api/auth/login/',{'username':'admin','password':'StrongPass123!'},format='json')
        self.assertEqual(r.status_code,200); self.assertIn('access',r.data); self.assertIn('refresh_token',r.cookies)
    def test_admin_can_create_supervisor(self):
        self.client.force_authenticate(self.admin)
        r=self.client.post('/api/users/',{'username':'sup2','email':'sup2@test.local','first_name':'New','last_name':'Supervisor','role':'SUPERVISOR','password':'StrongPass123!'},format='json')
        self.assertEqual(r.status_code,201); self.assertTrue(User.objects.filter(username='sup2',role='SUPERVISOR').exists())
    def test_supervisor_cannot_create_admin(self):
        self.client.force_authenticate(self.sup)
        r=self.client.post('/api/users/',{'username':'hack','email':'hack@test.local','role':'ADMIN','password':'StrongPass123!'},format='json')
        self.assertIn(r.status_code,[400,403])
