# reviews_app/tests.py

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

# Passe ggf. den Importpfad für die Modelle an
from .models import Review
# Stelle sicher, dass das CustomUser Model importiert wird
# from user_auth_app.models import CustomUser # Oder: CustomUser = get_user_model()

CustomUser = get_user_model()

class ReviewAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # --- Benutzer erstellen ---
        cls.business_user1 = CustomUser.objects.create_user(
            username='review_provider1', password='password123', email='revprovider1@example.com',
            type='business', first_name='Biz', last_name='One'
        )
        cls.business_user2 = CustomUser.objects.create_user(
            username='review_provider2', password='password123', email='revprovider2@example.com',
            type='business', first_name='Biz', last_name='Two'
        )
        cls.customer_user1 = CustomUser.objects.create_user(
            username='review_customer1', password='password123', email='revcustomer1@example.com',
            type='customer', first_name='Cust', last_name='One'
        )
        cls.customer_user2 = CustomUser.objects.create_user(
            username='review_customer2', password='password123', email='revcustomer2@example.com',
            type='customer', first_name='Cust', last_name='Two'
        )
        cls.other_customer = CustomUser.objects.create_user(
            username='other_customer', password='password123', email='othercust@example.com',
            type='customer'
        )

        # --- Reviews erstellen ---
        # R1: C1 bewertet B1 (Rating 5)
        cls.review1 = Review.objects.create(
            reviewer=cls.customer_user1, reviewed_user=cls.business_user1,
            rating=5, comment="Super Service!"
        )
        # R2: C2 bewertet B1 (Rating 3)
        cls.review2 = Review.objects.create(
            reviewer=cls.customer_user2, reviewed_user=cls.business_user1,
            rating=3, comment="War okay."
        )
        # R3: C1 bewertet B2 (Rating 4)
        cls.review3 = Review.objects.create(
            reviewer=cls.customer_user1, reviewed_user=cls.business_user2,
            rating=4, comment="Gute Arbeit."
        )

        # --- URLs ---
        cls.list_create_url = reverse('reviews_api:review-list-create')
        cls.review1_detail_url = reverse('reviews_api:review-detail', kwargs={'id': cls.review1.id})
        cls.review_non_existent_url = reverse('reviews_api:review-detail', kwargs={'id': 9999})


    # === GET /api/reviews/ Tests ===

    def test_list_reviews_unauthenticated_fail(self):
        """ Test: Nicht-authentifizierte User können keine Reviews auflisten (401/403) """
        response = self.client.get(self.list_create_url)
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_list_reviews_authenticated_success(self):
        """ Test: Authentifizierte User können Reviews auflisten """
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3) # 3 Reviews erstellt
        # Prüfe Struktur eines Eintrags (flach, ReviewListSerializer)
        review_data = response.data[0] # Nimm den neuesten (höchste ID oder ordering)
        expected_keys = {
            'id', 'business_user', 'reviewer', 'rating', 'description',
            'created_at', 'updated_at'
        }
        self.assertEqual(set(review_data.keys()), expected_keys)
        self.assertIsInstance(review_data['business_user'], int)
        self.assertIsInstance(review_data['reviewer'], int)
        self.assertIsInstance(review_data['description'], str)

    def test_list_reviews_filter_business_user_id(self):
        """ Test: Filtern nach business_user_id """
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.list_create_url, {'business_user_id': self.business_user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # R1 und R2 bewerten B1
        self.assertTrue(all(item['business_user'] == self.business_user1.id for item in response.data))

    def test_list_reviews_filter_reviewer_id(self):
        """ Test: Filtern nach reviewer_id """
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.list_create_url, {'reviewer_id': self.customer_user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # R1 und R3 sind von C1
        self.assertTrue(all(item['reviewer'] == self.customer_user1.id for item in response.data))

    def test_list_reviews_filter_rating(self):
        """ Test: Filtern nach rating """
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.list_create_url, {'rating': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Nur R1 hat Rating 5
        self.assertEqual(response.data[0]['id'], self.review1.id)

    def test_list_reviews_ordering_rating(self):
        """ Test: Sortieren nach Rating (absteigend) """
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.list_create_url, {'ordering': '-rating'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['id'], self.review1.id) # Rating 5
        self.assertEqual(response.data[1]['id'], self.review3.id) # Rating 4
        self.assertEqual(response.data[2]['id'], self.review2.id) # Rating 3

    # === POST /api/reviews/ Tests ===

    def test_create_review_customer_success(self):
        """ Test: Customer kann erfolgreich eine Review erstellen """
        self.client.force_authenticate(user=self.customer_user2) # C2 bewertet B2
        review_count_before = Review.objects.count()
        post_data = {
            "business_user_id": self.business_user2.id,
            "rating": 2,
            "description": "War nicht so gut."
        }
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), review_count_before + 1)
        # Prüfe Response (sollte ReviewListSerializer sein - flach)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['rating'], 2)
        self.assertEqual(response.data['description'], "War nicht so gut.")
        self.assertEqual(response.data['reviewer'], self.customer_user2.id)
        self.assertEqual(response.data['business_user'], self.business_user2.id)
        # Prüfe DB
        new_review = Review.objects.latest('id')
        self.assertEqual(new_review.reviewer, self.customer_user2)
        self.assertEqual(new_review.reviewed_user, self.business_user2)
        self.assertEqual(new_review.rating, 2)
        self.assertEqual(new_review.comment, "War nicht so gut.")

    def test_create_review_duplicate_fail(self):
        """ Test: User kann denselben Business User nicht zweimal bewerten (400) """
        self.client.force_authenticate(user=self.customer_user1) # C1 hat B1 schon bewertet
        post_data = {
            "business_user_id": self.business_user1.id,
            "rating": 1,
            "description": "Zweite Bewertung Versuch."
        }
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Erwarte Detailmeldung wegen Unique Constraint
        self.assertIn("already reviewed", response.data.get('detail', '').lower())

    def test_create_review_business_user_fail(self):
        """ Test: Business User kann keine Review erstellen (403) """
        self.client.force_authenticate(user=self.business_user1)
        post_data = {"business_user_id": self.business_user2.id, "rating": 5, "description": "Self"}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Wegen IsCustomerUser

    def test_create_review_unauthenticated_fail(self):
        """ Test: Nicht-authentifizierte User können keine Review erstellen (401/403) """
        post_data = {"business_user_id": self.business_user1.id, "rating": 5, "description": "Anon"}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_review_invalid_rating_fail(self):
        """ Test: Ungültiges Rating führt zu Fehler (400) """
        self.client.force_authenticate(user=self.customer_user2)
        post_data = {"business_user_id": self.business_user2.id, "rating": 6, "description": "Zu gut"}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)

    def test_create_review_invalid_business_user_fail(self):
        """ Test: Ungültige business_user_id führt zu Fehler (400) """
        self.client.force_authenticate(user=self.customer_user2)
        post_data = {"business_user_id": 9999, "rating": 4, "description": "Wer?"}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('business_user_id', response.data)

    def test_create_review_target_customer_user_fail(self):
        """ Test: Bewertung eines Customer Users schlägt fehl (400) """
        self.client.force_authenticate(user=self.customer_user2)
        post_data = {"business_user_id": self.customer_user1.id, "rating": 3, "description": "Falsches Ziel"}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('business_user_id', response.data) # Wegen Queryset im Serializer Field

    # === GET /api/reviews/{id}/ Tests ===

    def test_retrieve_review_authenticated_success(self):
        """ Test: Authentifizierter User kann Review-Details abrufen """
        self.client.force_authenticate(user=self.other_customer) # Irgendein eingeloggter User
        response = self.client.get(self.review1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Prüfe Struktur (verschachtelt, ReviewDetailSerializer)
        expected_keys = {
            'id', 'rating', 'comment', 'reviewer', 'business_user',
            'created_at', 'updated_at'
        }
        self.assertEqual(set(response.data.keys()), expected_keys)
        self.assertIsInstance(response.data['reviewer'], dict)
        self.assertIn('username', response.data['reviewer'])
        self.assertEqual(response.data['reviewer']['id'], self.customer_user1.id)
        self.assertIsInstance(response.data['business_user'], dict)
        self.assertIn('username', response.data['business_user'])
        self.assertEqual(response.data['business_user']['id'], self.business_user1.id)
        self.assertEqual(response.data['comment'], "Super Service!") # Feld heißt 'comment' hier

    def test_retrieve_review_unauthenticated_fail(self):
        """ Test: Nicht-authentifizierter User kann keine Details abrufen (401/403) """
        response = self.client.get(self.review1_detail_url)
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_retrieve_review_not_found(self):
        """ Test: Abrufen einer nicht existierenden Review (404) """
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.review_non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # === PATCH /api/reviews/{id}/ Tests ===

    def test_patch_review_owner_success(self):
        """ Test: Besitzer kann seine Review erfolgreich patchen """
        self.client.force_authenticate(user=self.customer_user1) # Besitzer von Review 1
        patch_data = {"rating": 1, "description": "Update: Doch nicht so gut."}
        response = self.client.patch(self.review1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Prüfe Response (flach, ReviewListSerializer)
        self.assertEqual(response.data['rating'], 1)
        self.assertEqual(response.data['description'], "Update: Doch nicht so gut.")
        self.assertEqual(response.data['id'], self.review1.id)
        self.assertEqual(response.data['reviewer'], self.customer_user1.id)
        # Prüfe DB
        self.review1.refresh_from_db()
        self.assertEqual(self.review1.rating, 1)
        self.assertEqual(self.review1.comment, "Update: Doch nicht so gut.")

    def test_patch_review_partial_success(self):
        """ Test: Teil-Update (nur Rating) durch Besitzer """
        self.client.force_authenticate(user=self.customer_user1)
        original_comment = self.review1.comment
        patch_data = {"rating": 2}
        response = self.client.patch(self.review1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 2)
        self.review1.refresh_from_db()
        self.assertEqual(self.review1.rating, 2)
        self.assertEqual(self.review1.comment, original_comment) # Kommentar unverändert

    def test_patch_review_non_owner_fail(self):
        """ Test: Nicht-Besitzer kann Review nicht patchen (403) """
        self.client.force_authenticate(user=self.customer_user2) # Nicht Besitzer von R1
        patch_data = {"rating": 1}
        response = self.client.patch(self.review1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Wegen IsReviewOwner

    def test_patch_review_unauthenticated_fail(self):
        """ Test: Nicht-authentifizierter User kann nicht patchen (401/403) """
        patch_data = {"rating": 1}
        response = self.client.patch(self.review1_detail_url, patch_data, format='json')
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_patch_review_not_found(self):
        """ Test: Patch einer nicht existierenden Review (404) """
        self.client.force_authenticate(user=self.customer_user1)
        patch_data = {"rating": 1}
        response = self.client.patch(self.review_non_existent_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_review_invalid_rating(self):
        """ Test: Patch mit ungültigem Rating (400) """
        self.client.force_authenticate(user=self.customer_user1)
        patch_data = {"rating": 7}
        response = self.client.patch(self.review1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)

    # === DELETE /api/reviews/{id}/ Tests ===

    def test_delete_review_owner_success(self):
        """ Test: Besitzer kann seine Review löschen """
        self.client.force_authenticate(user=self.customer_user1)
        review_count_before = Review.objects.count()
        response = self.client.delete(self.review1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), review_count_before - 1)
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=self.review1.id)

    def test_delete_review_non_owner_fail(self):
        """ Test: Nicht-Besitzer kann Review nicht löschen (403) """
        self.client.force_authenticate(user=self.customer_user2)
        response = self.client.delete(self.review1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_unauthenticated_fail(self):
        """ Test: Nicht-authentifizierter User kann nicht löschen (401/403) """
        response = self.client.delete(self.review1_detail_url)
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_delete_review_not_found(self):
        """ Test: Löschen einer nicht existierenden Review (404) """
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.delete(self.review_non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)