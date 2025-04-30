# profile_app/tests.py

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Profile

CustomUser = get_user_model()

class ProfileDetailAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_a = CustomUser.objects.create_user(
            username='testuser_a', password='password123', email='a@example.com',
            type='business', first_name='TestA_First', last_name='TestA_Last'
        )
        # Profile wird durch Signal erstellt, aber wir holen es und fügen Daten hinzu
        cls.profile_a = Profile.objects.get(user=cls.user_a)
        cls.profile_a.location = "Teststadt A"
        cls.profile_a.tel = "11111"
        cls.profile_a.description = "Beschreibung A"
        cls.profile_a.working_hours = "7-10"
        cls.profile_a.save()

        cls.user_b = CustomUser.objects.create_user(
            username='testuser_b', password='password123', email='b@example.com',
            type='customer'
        )
        cls.profile_b = Profile.objects.get(user=cls.user_b) 

        cls.other_business_user = CustomUser.objects.create_user(
            username='otherbiz', password='password123', email='other@example.com',
            type='business'
        )
        cls.profile_other_business = Profile.objects.get(user=cls.other_business_user) 

        cls.detail_url_user_a = reverse('profile_api:profile-detail', kwargs={'pk': cls.user_a.pk})
        cls.customer_list_url = reverse('profile_api:customer-profile-list')
        cls.business_list_url = reverse('profile_api:business-profile-list')

    def test_get_own_profile_success(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.detail_url_user_a)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_keys = {
            "user", "username", "first_name", "last_name", "file", "location",
            "tel", "description", "working_hours", "type", "email", "created_at"
        }
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertEqual(response.data['user'], self.user_a.id)
        self.assertEqual(response.data['location'], self.profile_a.location)
        self.assertEqual(response.data['type'], self.user_a.type)

    def test_get_other_profile_authenticated_allowed(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.detail_url_user_a)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user_a.id)

    def test_get_profile_unauthenticated_fail(self):
        response = self.client.get(self.detail_url_user_a)
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_get_profile_not_found(self):
        self.client.force_authenticate(user=self.user_a)
        non_existent_pk = CustomUser.objects.latest('id').id + 99
        url_not_found = reverse('profile_api:profile-detail', kwargs={'pk': non_existent_pk})
        response = self.client.get(url_not_found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_profile_success(self):
        self.client.force_authenticate(user=self.user_a)
        update_data = {
            "location": "Neue Stadt", "tel": "98765", "first_name": "UpdateFirst",
            "last_name": "UpdateLast", "email": "new_a@example.com",
            "description": "Neue Beschreibung", "working_hours": "9-17"
        }
        response = self.client.patch(self.detail_url_user_a, update_data, format='json')

        if response.status_code != status.HTTP_200_OK:
            print("\nDEBUG PATCH FAIL Response Data:", response.data)
            # Zusätzlicher Debug: User-Objekt vor refresh
            print("DEBUG User before refresh:", CustomUser.objects.get(pk=self.user_a.pk).__dict__)


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile_a.refresh_from_db()
        self.user_a.refresh_from_db() # Wichtig!

        # Zusätzlicher Debug: User-Objekt nach refresh
        # print("DEBUG User after refresh:", self.user_a.__dict__)

        self.assertEqual(self.profile_a.location, "Neue Stadt")
        self.assertEqual(self.profile_a.tel, "98765")
        self.assertEqual(self.profile_a.description, "Neue Beschreibung")
        self.assertEqual(self.profile_a.working_hours, "9-17")
        # --- DIESE SOLLTEN JETZT PASSEN ---
        self.assertEqual(self.user_a.first_name, "UpdateFirst")
        self.assertEqual(self.user_a.last_name, "UpdateLast")
        self.assertEqual(self.user_a.email, "new_a@example.com")
        # ---
        self.assertEqual(response.data['location'], "Neue Stadt")
        self.assertEqual(response.data['first_name'], "UpdateFirst")
        self.assertEqual(response.data['email'], "new_a@example.com")
        expected_keys = {
            "user", "username", "first_name", "last_name", "file", "location",
            "tel", "description", "working_hours", "type", "email", "created_at"
        }
        self.assertEqual(set(response.data.keys()), expected_keys)

    def test_patch_own_profile_partial_success(self):
        self.client.force_authenticate(user=self.user_a)
        original_location = self.profile_a.location
        update_data = {"tel": "555-PARTIAL"}
        response = self.client.patch(self.detail_url_user_a, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile_a.refresh_from_db()
        self.assertEqual(self.profile_a.tel, "555-PARTIAL")
        self.assertEqual(self.profile_a.location, original_location)
        self.assertEqual(response.data['tel'], "555-PARTIAL")

    def test_patch_other_profile_fail(self):
        self.client.force_authenticate(user=self.user_b)
        update_data = {"location": "Nicht erlaubt"}
        response = self.client.patch(self.detail_url_user_a, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_unauthenticated_fail(self):
        update_data = {"location": "Nicht erlaubt"}
        response = self.client.patch(self.detail_url_user_a, update_data, format='json')
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_patch_profile_not_found(self):
        self.client.force_authenticate(user=self.user_a)
        non_existent_pk = CustomUser.objects.latest('id').id + 99
        url_not_found = reverse('profile_api:profile-detail', kwargs={'pk': non_existent_pk})
        update_data = {"location": "Wohin?"}
        response = self.client.patch(url_not_found, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_own_profile_invalid_email(self):
        self.client.force_authenticate(user=self.user_a)
        update_data = {"email": "invalid-email"}
        response = self.client.patch(self.detail_url_user_a, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_get_customer_list_success(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        customer_data = response.data[0]

        # --- KORRIGIERTE ASSERTIONS für Liste ---
        self.assertIn('user', customer_data)
        self.assertIsInstance(customer_data['user'], int) # Erwarte Integer ID
        self.assertEqual(customer_data['user'], self.user_b.id)
        # Überprüfe andere erwartete Felder direkt
        self.assertIn('username', customer_data)
        self.assertEqual(customer_data['username'], self.user_b.username)
        self.assertIn('first_name', customer_data)
        self.assertIn('last_name', customer_data)
        # --- ENDE KORRIGIERTE ASSERTIONS ---

        self.assertIn('file', customer_data)
        self.assertIn('type', customer_data)
        self.assertEqual(customer_data['type'], 'customer')
        self.assertIn('uploaded_at', customer_data) # Überprüfe den umbenannten Key

    def test_get_business_list_success(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.business_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)

        business_data_a = None
        business_data_other = None
        for item in response.data:
             # --- KORRIGIERTE ASSERTIONS für Liste ---
            self.assertIn('user', item)
            self.assertIsInstance(item['user'], int) # Erwarte Integer ID
            if item['user'] == self.user_a.id:
                 business_data_a = item
            elif item['user'] == self.other_business_user.id:
                 business_data_other = item
             # Überprüfe andere erwartete Felder direkt
            self.assertIn('username', item)
            self.assertIn('first_name', item)
            self.assertIn('last_name', item)
             # --- ENDE KORRIGIERTE ASSERTIONS ---

        self.assertIsNotNone(business_data_a)
        self.assertIsNotNone(business_data_other)

        # Überprüfe spezifische Felder für user_a
        self.assertEqual(business_data_a['username'], self.user_a.username)
        self.assertIn('file', business_data_a)
        self.assertIn('location', business_data_a)
        self.assertEqual(business_data_a['location'], self.profile_a.location)
        self.assertIn('tel', business_data_a)
        self.assertEqual(business_data_a['tel'], self.profile_a.tel)
        self.assertIn('description', business_data_a)
        self.assertEqual(business_data_a['description'], self.profile_a.description)
        self.assertIn('working_hours', business_data_a)
        self.assertEqual(business_data_a['working_hours'], self.profile_a.working_hours)
        self.assertIn('type', business_data_a)
        self.assertEqual(business_data_a['type'], 'business')
        # uploaded_at sollte hier NICHT sein
        self.assertNotIn('uploaded_at', business_data_a)