# base_app/tests.py

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
import decimal # Für Decimal-Vergleiche

# Importiere Modelle aus anderen Apps (Pfade ggf. anpassen)
from offers_app.models import Offer, OfferDetail, Category
from reviews_app.models import Review
# from user_auth_app.models import CustomUser # Oder: CustomUser = get_user_model()

CustomUser = get_user_model()

class BaseInfoAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # --- Benutzer erstellen ---
        cls.b_user1 = CustomUser.objects.create_user(
            username='base_b1',
            email='base_b1@example.com', # E-Mail hinzugefügt
            type='business',
            password='pw'
        )
        cls.b_user2 = CustomUser.objects.create_user(
            username='base_b2',
            email='base_b2@example.com', # E-Mail hinzugefügt
            type='business',
            password='pw'
        )
        cls.c_user1 = CustomUser.objects.create_user(
            username='base_c1',
            email='base_c1@example.com', # E-Mail hinzugefügt
            type='customer',
            password='pw'
        )
        cls.c_user2 = CustomUser.objects.create_user(
            username='base_c2',
            email='base_c2@example.com', # E-Mail hinzugefügt
            type='customer',
            password='pw'
        )

        # --- Angebote erstellen ---
        cls.offer1 = Offer.objects.create(user=cls.b_user1, title="Base Offer 1")
        cls.offer2 = Offer.objects.create(user=cls.b_user2, title="Base Offer 2")
        cls.offer3 = Offer.objects.create(user=cls.b_user1, title="Base Offer 3")

        # --- Reviews erstellen ---
        # 3 Reviews, Ratings: 5, 4, 4 -> Avg = (5+4+4)/3 = 13/3 = 4.333... -> gerundet 4.3
        cls.review1 = Review.objects.create(reviewer=cls.c_user1, reviewed_user=cls.b_user1, rating=5, comment="Top")
        cls.review2 = Review.objects.create(reviewer=cls.c_user2, reviewed_user=cls.b_user1, rating=4, comment="Gut")
        cls.review3 = Review.objects.create(reviewer=cls.c_user1, reviewed_user=cls.b_user2, rating=4, comment="Auch gut")

        # --- URL ---
        cls.base_info_url = reverse('base_app_api:base-info') # Passe Namespace an, falls nötig

    def test_get_base_info_success(self):
        """ Testet erfolgreichen Abruf der Basis-Infos mit Daten """
        response = self.client.get(self.base_info_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Erwartete Werte basierend auf setUpTestData
        expected_review_count = 3
        expected_avg_rating = 4.3 # (5+4+4)/3 = 4.333... gerundet
        expected_business_count = 2 # b_user1, b_user2 (admin zählt nicht, falls separat)
        # Zähle Business User aus DB zur Sicherheit
        actual_business_count = CustomUser.objects.filter(type='business').count()
        expected_offer_count = 3

        # Prüfe Keys
        expected_keys = {
            "review_count", "average_rating", "business_profile_count", "offer_count"
        }
        self.assertEqual(set(response.data.keys()), expected_keys)

        # Prüfe Werte
        self.assertEqual(response.data['review_count'], expected_review_count)
        # Vergleich für Fließkommazahlen/Decimal (Serializer gibt float/string zurück?)
        # Annahme: Serializer gibt float oder string zurück, der zu float konvertiert werden kann
        self.assertAlmostEqual(float(response.data['average_rating']), expected_avg_rating, places=1)
        self.assertEqual(response.data['business_profile_count'], actual_business_count) # Vergleich mit tatsächlicher DB-Zahl
        self.assertEqual(response.data['offer_count'], expected_offer_count)

    def test_get_base_info_no_reviews(self):
        """ Testet Abruf, wenn keine Reviews existieren """
        # Lösche Reviews nur für diesen Test (geht nicht in setUpTestData)
        Review.objects.all().delete()
        # Erstelle einen Offer neu, da er ggf. wegen Reviews gelöscht wurde? Nein, nur Reviews löschen.
        # Offer und User bleiben bestehen

        response = self.client.get(self.base_info_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_business_count = CustomUser.objects.filter(type='business').count() # Bleibt 2
        expected_offer_count = 3 # Bleibt 3

        self.assertEqual(response.data['review_count'], 0)
        self.assertIsNone(response.data['average_rating']) # Erwarte None, wenn Avg auf leerem Set
        self.assertEqual(response.data['business_profile_count'], expected_business_count)
        self.assertEqual(response.data['offer_count'], expected_offer_count)

    def test_get_base_info_no_data_at_all(self):
        """ Testet Abruf, wenn keine relevanten Daten existieren """
        # Lösche alles Relevante
        Review.objects.all().delete()
        Offer.objects.all().delete()
        # Vorsicht: Löschen der User löscht ggf. auch Profile etc. via CASCADE
        # Wir löschen nur die Business User, um den Count zu testen
        CustomUser.objects.filter(type='business').delete()

        response = self.client.get(self.base_info_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['review_count'], 0)
        self.assertIsNone(response.data['average_rating'])
        self.assertEqual(response.data['business_profile_count'], 0)
        self.assertEqual(response.data['offer_count'], 0)