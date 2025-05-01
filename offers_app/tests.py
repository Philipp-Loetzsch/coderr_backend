# offers_app/tests.py

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
# Passe ggf. den Importpfad für die Modelle an
from .models import Offer, OfferDetail, Category
# Stelle sicher, dass das CustomUser Model importiert wird
from user_auth_app.models import CustomUser # Oder: CustomUser = get_user_model()

# CustomUser = get_user_model() # Alternative, falls der direkte Import nicht klappt

# WICHTIG: Für ImageField-Tests ggf. 'Pillow' installieren: pip install Pillow

class OfferAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # --- Benutzer erstellen ---
        cls.business_user = CustomUser.objects.create_user(
            username='offer_provider', password='password123', email='provider@example.com',
            type='business', first_name='Business', last_name='User'
        )
        cls.other_business_user = CustomUser.objects.create_user(
            username='other_provider', password='password123', email='other@example.com',
            type='business'
        )
        cls.customer_user = CustomUser.objects.create_user(
            username='offer_customer', password='password123', email='customer@example.com',
            type='customer'
        )

        # --- Kategorie erstellen ---
        cls.category = Category.objects.create(name='Design')
        cls.category2 = Category.objects.create(name='Development')


        # --- Angebot 1 erstellen (von business_user) ---
        cls.offer1 = Offer.objects.create(
            user=cls.business_user,
            category=cls.category,
            title="Webdesign Basic",
            description="Grundlegendes Webdesign"
            # image wird nicht gesetzt
        )
        # Details für Angebot 1
        cls.detail1_1 = OfferDetail.objects.create(
            offer=cls.offer1, title="Basic Page", description="Eine Seite", price=150.00,
            delivery_time_in_days=5, revisions=1, features=["Layout"], offer_type='basic'
        )
        cls.detail1_2 = OfferDetail.objects.create(
            offer=cls.offer1, title="Standard Page", description="Bis 5 Seiten", price=500.00,
            delivery_time_in_days=10, revisions=3, features=["Layout", "Kontaktformular"], offer_type='standard'
        )

        # --- Angebot 2 erstellen (von business_user) ---
        cls.offer2 = Offer.objects.create(
            user=cls.business_user,
            category=cls.category2,
            title="API Entwicklung",
            description="Backend API"
        )
        # Detail für Angebot 2
        cls.detail2_1 = OfferDetail.objects.create(
            offer=cls.offer2, title="Simple Endpoint", description="Ein Endpoint", price=300.00,
            delivery_time_in_days=7, revisions=2, features=["Auth"], offer_type='basic'
        )

        # --- Angebot 3 erstellen (von other_business_user) ---
        cls.offer3 = Offer.objects.create(
            user=cls.other_business_user,
            category=cls.category,
            title="Logo Design",
            description="Nur Logo"
        )
        cls.detail3_1 = OfferDetail.objects.create(
            offer=cls.offer3, title="Basic Logo", description="3 Entwürfe", price=100.00,
            delivery_time_in_days=3, revisions=2, features=["Vektor"], offer_type='basic'
        )


        # --- URLs definieren ---
        cls.offer_list_create_url = reverse('offers_api:offer-list-create')
        cls.offer1_detail_url = reverse('offers_api:offer-detail', kwargs={'id': cls.offer1.id})
        cls.offer_non_existent_url = reverse('offers_api:offer-detail', kwargs={'id': 9999})
        cls.detail1_1_url = reverse('offers_api:offerdetail-detail', kwargs={'id': cls.detail1_1.id})
        cls.detail_non_existent_url = reverse('offers_api:offerdetail-detail', kwargs={'id': 9999})

    # === GET /api/offers/ Tests ===

    def test_list_offers_success(self):
        """ Testet erfolgreiches Abrufen der Angebotsliste (AllowAny) """
        response = self.client.get(self.offer_list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Prüfe Paginierungs-Keys (Annahme: StandardPagination ist aktiv)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 3) # Wir haben 3 Angebote erstellt
        self.assertEqual(len(response.data['results']), 3) # Annahme: page_size >= 3

        # Prüfe Struktur eines Eintrags
        offer_data = response.data['results'][0] # Nimm den ersten Eintrag
        self.assertIn('id', offer_data)
        self.assertIn('user', offer_data) # Sollte die User ID sein
        self.assertIn('user_details', offer_data) # Sollte das Objekt sein
        self.assertIn('first_name', offer_data['user_details'])
        self.assertIn('details', offer_data) # Sollte Liste von {id, url} sein
        self.assertIsInstance(offer_data['details'], list)
        if offer_data['details']: # Nur prüfen wenn Details vorhanden
             self.assertIn('id', offer_data['details'][0])
             self.assertIn('url', offer_data['details'][0])
             # Prüfe ob URL absolut ist (enthält http)
             self.assertTrue(offer_data['details'][0]['url'].startswith('http'))
        self.assertIn('min_price', offer_data)
        self.assertIn('min_delivery_time', offer_data)
        self.assertIn('title', offer_data)
        self.assertIn('image', offer_data)

    def test_list_offers_filtering_category_success(self):
        """ Testet Filterung nach category_id """
        response = self.client.get(self.offer_list_create_url, {'category_id': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2) # offer1 und offer3 sind in category 1
        self.assertEqual(len(response.data['results']), 2)
        for item in response.data['results']:
             # Finde das zugehörige Offer-Objekt um die Kategorie zu prüfen (etwas umständlich)
             offer_obj = Offer.objects.get(id=item['id'])
             self.assertEqual(offer_obj.category, self.category)

    def test_list_offers_filtering_min_price_success(self):
        """ Testet Filterung nach min_price (basiert auf OfferDetail) """
        response = self.client.get(self.offer_list_create_url, {'min_price': 400})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1) # Nur offer1 hat ein Detail (Standard) mit price >= 400
        self.assertEqual(response.data['results'][0]['id'], self.offer1.id)

    def test_list_offers_filtering_max_delivery_success(self):
        """ Testet Filterung nach max_delivery_time (basiert auf OfferDetail) """
        response = self.client.get(self.offer_list_create_url, {'max_delivery_time': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2) # offer1 (Basic) und offer3 (Basic) haben Details <= 5 Tage
        offer_ids = {item['id'] for item in response.data['results']}
        self.assertIn(self.offer1.id, offer_ids)
        self.assertIn(self.offer3.id, offer_ids)

    def test_list_offers_search_success(self):
        """ Testet die Suche """
        response = self.client.get(self.offer_list_create_url, {'search': 'API Entwicklung'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.offer2.id)

    def test_list_offers_ordering_created_at_success(self):
        """ Testet die Sortierung nach Erstellungsdatum (Standard oder explizit) """
        response = self.client.get(self.offer_list_create_url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        # Das zuletzt erstellte Angebot sollte zuerst kommen
        self.assertEqual(response.data['results'][0]['id'], self.offer3.id)

    # === POST /api/offers/ Tests ===

    def test_create_offer_business_user_success(self):
        """ Testet erfolgreiches Erstellen eines Angebots durch Business User """
        self.client.force_authenticate(user=self.business_user)
        offer_count_before = Offer.objects.count()
        detail_count_before = OfferDetail.objects.count()
        post_data = {
            "title": "Neues Angebot",
            "description": "Beschreibung neu",
            # "category": self.category.id, # Momentan im Serializer nicht vorgesehen!
            "details": [
                {
                    "title": "Neues Basic", "price": 50.0, "delivery_time_in_days": 2,
                    "revisions": 1, "features": ["Feature A"], "offer_type": "basic"
                },
                 {
                    "title": "Neues Premium", "price": 150.0, "delivery_time_in_days": 5,
                    "revisions": 5, "features": ["Feature A", "Feature B"], "offer_type": "premium"
                }
            ]
        }
        response = self.client.post(self.offer_list_create_url, post_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), offer_count_before + 1)
        self.assertEqual(OfferDetail.objects.count(), detail_count_before + 2)

        # Prüfe Response Data Struktur (sollte OfferResponseSerializer sein)
        self.assertIn('id', response.data)
        self.assertIn('details', response.data)
        self.assertIsInstance(response.data['details'], list)
        self.assertEqual(len(response.data['details']), 2)
        self.assertIn('title', response.data['details'][0])
        self.assertIn('price', response.data['details'][0])
        self.assertNotIn('user', response.data) # User-Objekt sollte nicht Teil der Response sein
        self.assertNotIn('created_at', response.data) # Zeitstempel auch nicht

        # Prüfe DB-Objekt
        new_offer = Offer.objects.get(id=response.data['id'])
        self.assertEqual(new_offer.user, self.business_user)
        self.assertEqual(new_offer.details.count(), 2)

    def test_create_offer_customer_user_fail(self):
        """ Testet, dass Customer User kein Angebot erstellen kann (403) """
        self.client.force_authenticate(user=self.customer_user)
        post_data = { "title": "Versuch", "details": [{"title": "fail", "price": 1, "delivery_time_in_days": 1, "revisions": 0}] }
        response = self.client.post(self.offer_list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_offer_unauthenticated_fail(self):
        """ Testet, dass nicht-authentifizierte User kein Angebot erstellen können (401/403) """
        post_data = { "title": "Versuch", "details": [{"title": "fail", "price": 1, "delivery_time_in_days": 1, "revisions": 0}] }
        response = self.client.post(self.offer_list_create_url, post_data, format='json')
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_offer_missing_details_fail(self):
        """ Testet, dass 'details' benötigt wird (400) """
        self.client.force_authenticate(user=self.business_user)
        post_data = { "title": "Ohne Details" }
        response = self.client.post(self.offer_list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)

    def test_create_offer_missing_detail_title_fail(self):
        """ Testet, dass Detail-Felder benötigt werden (400) """
        self.client.force_authenticate(user=self.business_user)
        post_data = {
            "title": "Angebot",
            "details": [{"price": 1, "delivery_time_in_days": 1, "revisions": 0}] # title fehlt
        }
        response = self.client.post(self.offer_list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data) # Fehler sollte im details-Feld liegen

    # === GET /api/offers/{id}/ Tests ===

    def test_retrieve_offer_success(self):
        """ Testet erfolgreiches Abrufen eines Angebots (AllowAny) """
        response = self.client.get(self.offer1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Prüfe Struktur (sollte OfferRetrieveSerializer sein)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], self.offer1.id)
        self.assertIn('user', response.data) # User ID
        self.assertEqual(response.data['user'], self.offer1.user.id)
        self.assertNotIn('user_details', response.data) # Kein Objekt hier erwartet
        self.assertIn('details', response.data) # URLs erwartet
        self.assertIsInstance(response.data['details'], list)
        self.assertEqual(len(response.data['details']), 2)
        self.assertTrue(response.data['details'][0]['url'].startswith('http'))
        self.assertIn('min_price', response.data)
        self.assertEqual(response.data['min_price'], 150.00) # Min Preis von Offer 1
        self.assertIn('min_delivery_time', response.data)
        self.assertEqual(response.data['min_delivery_time'], 5) # Min Lieferzeit von Offer 1

    def test_retrieve_offer_not_found(self):
        """ Testet Abrufen eines nicht existierenden Angebots (404) """
        response = self.client.get(self.offer_non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # === PATCH /api/offers/{id}/ Tests ===

    def test_patch_offer_owner_success(self):
        """ Testet erfolgreiches Patchen durch den Besitzer """
        self.client.force_authenticate(user=self.business_user)
        patch_data = {
            "title": "Webdesign Basic Updated",
            "details": [
                {
                    "id": self.detail1_1.id, # ID des zu ändernden Details
                    "price": 160.00,
                    "revisions": 2
                },
                # detail1_2 wird nicht geändert
            ]
        }
        response = self.client.patch(self.offer1_detail_url, patch_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Prüfe Response (sollte OfferResponseSerializer sein)
        self.assertEqual(response.data['title'], "Webdesign Basic Updated")
        self.assertIn('details', response.data)
        self.assertEqual(len(response.data['details']), 2)
        updated_detail_found = False
        for detail in response.data['details']:
             if detail['id'] == self.detail1_1.id:
                 self.assertEqual(detail['price'], '160.00') # Decimal wird als String serialisiert
                 self.assertEqual(detail['revisions'], 2)
                 updated_detail_found = True
        self.assertTrue(updated_detail_found)

        # Prüfe DB
        self.offer1.refresh_from_db()
        self.detail1_1.refresh_from_db()
        self.assertEqual(self.offer1.title, "Webdesign Basic Updated")
        self.assertEqual(self.detail1_1.price, 160.00)
        self.assertEqual(self.detail1_1.revisions, 2)

    def test_patch_offer_non_owner_fail(self):
        """ Testet, dass Nicht-Besitzer nicht patchen können (403) """
        self.client.force_authenticate(user=self.other_business_user)
        patch_data = {"title": "Versuch Patch"}
        response = self.client.patch(self.offer1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_offer_unauthenticated_fail(self):
        """ Testet, dass nicht-authentifizierte User nicht patchen können (401/403) """
        patch_data = {"title": "Versuch Patch"}
        response = self.client.patch(self.offer1_detail_url, patch_data, format='json')
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_patch_offer_not_found(self):
        """ Testet Patch eines nicht existierenden Angebots (404) """
        self.client.force_authenticate(user=self.business_user)
        patch_data = {"title": "Versuch Patch"}
        response = self.client.patch(self.offer_non_existent_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # === DELETE /api/offers/{id}/ Tests ===

    def test_delete_offer_owner_success(self):
        """ Testet erfolgreiches Löschen durch den Besitzer """
        self.client.force_authenticate(user=self.business_user)
        offer_count_before = Offer.objects.count()
        detail_count_before = OfferDetail.objects.count()
        response = self.client.delete(self.offer1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), offer_count_before - 1)
        # Prüfe, ob die Details auch weg sind (wegen on_delete=CASCADE)
        self.assertEqual(OfferDetail.objects.count(), detail_count_before - 2)
        with self.assertRaises(Offer.DoesNotExist):
            Offer.objects.get(id=self.offer1.id)

    def test_delete_offer_non_owner_fail(self):
        """ Testet, dass Nicht-Besitzer nicht löschen können (403) """
        self.client.force_authenticate(user=self.other_business_user)
        response = self.client.delete(self.offer1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_offer_unauthenticated_fail(self):
        """ Testet, dass nicht-authentifizierte User nicht löschen können (401/403) """
        response = self.client.delete(self.offer1_detail_url)
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_delete_offer_not_found(self):
        """ Testet Löschen eines nicht existierenden Angebots (404) """
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(self.offer_non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # === GET /api/offerdetails/{id}/ Tests ===

    def test_retrieve_offerdetail_success(self):
        """ Testet erfolgreiches Abrufen eines OfferDetail (AllowAny) """
        response = self.client.get(self.detail1_1_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Prüfe Struktur (sollte OfferDetailSpecificSerializer sein)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], self.detail1_1.id)
        self.assertIn('title', response.data)
        self.assertEqual(response.data['title'], self.detail1_1.title)
        self.assertIn('price', response.data)
        self.assertEqual(response.data['price'], f"{self.detail1_1.price:.2f}") # Preis als String prüfen
        self.assertIn('delivery_time_in_days', response.data)
        self.assertIn('revisions', response.data)
        self.assertIn('features', response.data)
        self.assertIn('offer_type', response.data)
        self.assertIn('description', response.data) # Prüfe, ob description enthalten ist

    def test_retrieve_offerdetail_not_found(self):
        """ Testet Abrufen eines nicht existierenden OfferDetail (404) """
        response = self.client.get(self.detail_non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)