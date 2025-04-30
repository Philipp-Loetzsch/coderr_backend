# user_auth_app/tests.py

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

CustomUser = get_user_model()

class AuthAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.existing_user = CustomUser.objects.create_user(
            username='testloginuser',
            password='testpassword123',
            email='login@example.com',
            type='customer'
        )
        cls.register_url = reverse('user_auth_app:registration') # Passe Namespace an!
        cls.login_url = reverse('user_auth_app:login')         # Passe Namespace an!

    def test_registration_success(self):
        user_count_before = CustomUser.objects.count()
        data = {
            "username": "newreguser",
            "email": "reg@example.com",
            "password": "newpassword123",
            "repeated_password": "newpassword123",
            "type": "business"
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), user_count_before + 1)
        new_user = CustomUser.objects.get(username="newreguser")
        self.assertEqual(new_user.email, "reg@example.com")
        self.assertEqual(new_user.type, "business")
        self.assertTrue(Token.objects.filter(user=new_user).exists())

        expected_keys = {"token", "username", "email", "user_id"}
        self.assertEqual(set(response.data.keys()), expected_keys)

        self.assertEqual(response.data['username'], "newreguser")
        self.assertEqual(response.data['email'], "reg@example.com")
        self.assertEqual(response.data['user_id'], new_user.id)
        self.assertTrue(len(response.data['token']) > 10)

    def test_registration_password_mismatch(self):
        data = {
            "username": "pwmatchuser",
            "email": "pwm@example.com",
            "password": "password1",
            "repeated_password": "password2",
            "type": "customer"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registration_missing_email(self):
        data = {
            "username": "noemailuser",
            "password": "password123",
            "repeated_password": "password123",
            "type": "customer"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_missing_type(self):
        data = {
            "username": "notypeuser",
            "email": "notype@example.com",
            "password": "password123",
            "repeated_password": "password123",
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)

    def test_registration_duplicate_username(self):
        data = {
            "username": self.existing_user.username,
            "email": "duplicate@example.com",
            "password": "password123",
            "repeated_password": "password123",
            "type": "customer"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_duplicate_email(self):
        data = {
            "username": "anothernewuser",
            "email": self.existing_user.email,
            "password": "password123",
            "repeated_password": "password123",
            "type": "customer"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_success(self):
        data = {'username': self.existing_user.username, 'password': 'testpassword123'}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_keys = {"token", "username", "email", "user_id"}
        self.assertEqual(set(response.data.keys()), expected_keys)

        self.assertEqual(response.data['username'], self.existing_user.username)
        self.assertEqual(response.data['email'], self.existing_user.email)
        self.assertEqual(response.data['user_id'], self.existing_user.id)
        self.assertTrue(len(response.data['token']) > 10)

    def test_login_fail_wrong_password(self):
        data = {'username': self.existing_user.username, 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_login_fail_nonexistent_user(self):
        data = {'username': 'nouser', 'password': 'password123'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_login_fail_missing_password(self):
        data = {'username': self.existing_user.username}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_fail_missing_username(self):
        data = {'password': 'testpassword123'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)