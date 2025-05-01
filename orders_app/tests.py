# orders_app/tests.py

import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.db.models import Q

# Passe Importpfade ggf. an
from .models import Order
from offers_app.models import Offer, OfferDetail, Category
# Stelle sicher, dass das CustomUser Model importiert wird
# from user_auth_app.models import CustomUser # Oder: CustomUser = get_user_model()

CustomUser = get_user_model()

class OrderAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # --- Benutzer erstellen ---
        cls.business_user1 = CustomUser.objects.create_user(
            username='order_provider1', password='password123', email='bprovider1@example.com',
            type='business', first_name='Business1', last_name='Provider1'
        )
        cls.business_user2 = CustomUser.objects.create_user(
            username='order_provider2', password='password123', email='bprovider2@example.com',
            type='business', first_name='Business2', last_name='Provider2'
        )
        cls.customer_user1 = CustomUser.objects.create_user(
            username='order_customer1', password='password123', email='customer1@example.com',
            type='customer', first_name='Customer', last_name='One'
        )
        cls.customer_user2 = CustomUser.objects.create_user(
            username='order_customer2', password='password123', email='customer2@example.com',
            type='customer', first_name='Customer', last_name='Two'
        )
        # Admin/Staff User für DELETE Test
        cls.admin_user = CustomUser.objects.create_superuser(
            username='order_admin', password='password123', email='admin@example.com',
            type='business' # Typ ist ggf. egal für is_staff, aber setzen wir ihn
        )
        # Business User ohne Orders für Count-Test
        cls.business_user3_no_orders = CustomUser.objects.create_user(
             username='no_orders_yet', password='password123', email='noorders@example.com',
             type='business'
        )

        # --- Angebote & Details erstellen ---
        cls.category = Category.objects.create(name='Order Test Category')
        cls.offer1 = Offer.objects.create(user=cls.business_user1, category=cls.category, title="Offer 1 by B1")
        cls.detail1 = OfferDetail.objects.create(offer=cls.offer1, title="Detail 1.1", price=50.00, delivery_time_in_days=3, revisions=1)
        cls.detail2 = OfferDetail.objects.create(offer=cls.offer1, title="Detail 1.2", price=100.00, delivery_time_in_days=5, revisions=2)
        cls.offer2 = Offer.objects.create(user=cls.business_user2, category=cls.category, title="Offer 2 by B2")
        cls.detail3 = OfferDetail.objects.create(offer=cls.offer2, title="Detail 2.1", price=75.00, delivery_time_in_days=4, revisions=1)

        # --- Bestellungen erstellen ---
        cls.order1 = Order.objects.create(customer=cls.customer_user1, offer_detail=cls.detail1, status=Order.STATUS_PENDING) # P: B1, C: C1
        cls.order2 = Order.objects.create(customer=cls.customer_user2, offer_detail=cls.detail2, status=Order.STATUS_IN_PROGRESS) # P: B1, C: C2
        cls.order3 = Order.objects.create(customer=cls.customer_user1, offer_detail=cls.detail3, status=Order.STATUS_COMPLETED) # P: B2, C: C1
        cls.order4 = Order.objects.create(customer=cls.customer_user2, offer_detail=cls.detail1, status=Order.STATUS_COMPLETED) # P: B1, C: C2

        # --- URLs ---
        cls.list_create_url = reverse('orders_api:order-list-create')
        cls.order1_detail_url = reverse('orders_api:order-detail', kwargs={'id': cls.order1.id})
        cls.order_non_existent_url = reverse('orders_api:order-detail', kwargs={'id': 9999})
        cls.business1_list_url = reverse('orders_api:business-order-list', kwargs={'business_user_id': cls.business_user1.id})
        cls.business2_list_url = reverse('orders_api:business-order-list', kwargs={'business_user_id': cls.business_user2.id})
        cls.business_non_existent_list_url = reverse('orders_api:business-order-list', kwargs={'business_user_id': 9999})
        cls.business1_completed_count_url = reverse('orders_api:completed-order-count', kwargs={'business_user_id': cls.business_user1.id})
        cls.business2_completed_count_url = reverse('orders_api:completed-order-count', kwargs={'business_user_id': cls.business_user2.id})
        cls.business3_completed_count_url = reverse('orders_api:completed-order-count', kwargs={'business_user_id': cls.business_user3_no_orders.id})
        cls.business1_inprogress_count_url = reverse('orders_api:inprogress-orders-count', kwargs={'business_user_id': cls.business_user1.id})
        cls.business2_inprogress_count_url = reverse('orders_api:inprogress-orders-count', kwargs={'business_user_id': cls.business_user2.id})
        cls.business3_inprogress_count_url = reverse('orders_api:inprogress-orders-count', kwargs={'business_user_id': cls.business_user3_no_orders.id})
        cls.business_non_existent_completed_count_url = reverse('orders_api:completed-order-count', kwargs={'business_user_id': 9999})
        cls.business_non_existent_inprogress_count_url = reverse('orders_api:inprogress-orders-count', kwargs={'business_user_id': 9999})
    # === GET /api/orders/ Tests ===

    def test_list_orders_unauthenticated_fail(self):
        response = self.client.get(self.list_create_url)
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_list_orders_customer_success(self):
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Customer 1 ist Kunde bei Order 1 (P: B1) und Order 3 (P: B2)
        self.assertEqual(len(response.data), 2)
        order_ids = {item['id'] for item in response.data}
        self.assertIn(self.order1.id, order_ids)
        self.assertIn(self.order3.id, order_ids)
        # Prüfe Struktur eines Eintrags (flach)
        order_data = response.data[0]
        expected_keys = {
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        }
        self.assertEqual(set(order_data.keys()), expected_keys)
        self.assertIsInstance(order_data['customer_user'], int)
        self.assertIsInstance(order_data['business_user'], int)

    def test_list_orders_provider_success(self):
        self.client.force_authenticate(user=self.business_user1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Business User 1 ist Anbieter für Order 1, 2, 4
        self.assertEqual(len(response.data), 3)
        order_ids = {item['id'] for item in response.data}
        self.assertIn(self.order1.id, order_ids)
        self.assertIn(self.order2.id, order_ids)
        self.assertIn(self.order4.id, order_ids)

    # === POST /api/orders/ Tests ===

    def test_create_order_customer_success(self):
        self.client.force_authenticate(user=self.customer_user2)
        order_count_before = Order.objects.count()
        post_data = {"offer_detail_id": self.detail3.id} # Detail von Offer 2 (Provider B2)
        response = self.client.post(self.list_create_url, post_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), order_count_before + 1)
        # Prüfe Response (sollte OrderSerializer sein - flach)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], Order.STATUS_PENDING)
        self.assertEqual(response.data['customer_user'], self.customer_user2.id)
        self.assertEqual(response.data['business_user'], self.business_user2.id) # Provider ID prüfen
        self.assertEqual(response.data['title'], self.detail3.title)
        # Prüfe DB
        new_order = Order.objects.latest('id')
        self.assertEqual(new_order.customer, self.customer_user2)
        self.assertEqual(new_order.offer_detail, self.detail3)
        self.assertEqual(new_order.status, Order.STATUS_PENDING)

    def test_create_order_business_user_fail(self):
        self.client.force_authenticate(user=self.business_user1)
        post_data = {"offer_detail_id": self.detail1.id}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_unauthenticated_fail(self):
        post_data = {"offer_detail_id": self.detail1.id}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_order_invalid_detail_id_fail(self):
        self.client.force_authenticate(user=self.customer_user1)
        post_data = {"offer_detail_id": 9999}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_detail_id_fail(self):
        self.client.force_authenticate(user=self.customer_user1)
        post_data = {}
        response = self.client.post(self.list_create_url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # === GET /api/orders/{id}/ Tests ===

    def test_retrieve_order_customer_success(self):
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.order1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order1.id)
        self.assertEqual(response.data['customer_user'], self.customer_user1.id)
        self.assertEqual(response.data['business_user'], self.business_user1.id)

    def test_retrieve_order_provider_success(self):
        self.client.force_authenticate(user=self.business_user1)
        response = self.client.get(self.order1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order1.id)

    def test_retrieve_order_other_user_fail(self):
        self.client.force_authenticate(user=self.customer_user2) # C2 ist nicht an Order 1 beteiligt
        response = self.client.get(self.order1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Wegen IsOrderParticipant

    def test_retrieve_order_unauthenticated_fail(self):
        response = self.client.get(self.order1_detail_url)
        self.assertTrue(response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_retrieve_order_not_found(self):
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.get(self.order_non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # === PATCH /api/orders/{id}/ Tests ===

    def test_patch_order_status_provider_success(self):
        """ Test: Anbieter kann Status ändern """
        self.client.force_authenticate(user=self.business_user1) # Anbieter von Order 1
        patch_data = {"status": Order.STATUS_COMPLETED}
        response = self.client.patch(self.order1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order1.id)
        self.assertEqual(response.data['status'], Order.STATUS_COMPLETED)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, Order.STATUS_COMPLETED)

    def test_patch_order_status_customer_fail(self):
        """ Test: Kunde kann Status NICHT ändern (403) """
        self.client.force_authenticate(user=self.customer_user1) # Kunde von Order 1
        patch_data = {"status": Order.STATUS_IN_PROGRESS}
        response = self.client.patch(self.order1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Wegen IsOrderProvider

    def test_patch_order_status_other_business_fail(self):
        """ Test: Anderer Business User kann Status NICHT ändern (403) """
        self.client.force_authenticate(user=self.business_user2) # Nicht Anbieter von Order 1
        patch_data = {"status": Order.STATUS_IN_PROGRESS}
        response = self.client.patch(self.order1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Wegen IsOrderProvider

    def test_patch_order_status_invalid_status_fail(self):
        """ Test: Ungültiger Status führt zu Fehler (400) """
        self.client.force_authenticate(user=self.business_user1)
        patch_data = {"status": "invalid_status"}
        response = self.client.patch(self.order1_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # === DELETE /api/orders/{id}/ Tests ===

    def test_delete_order_admin_success(self):
        """ Test: Admin kann Order löschen """
        self.client.force_authenticate(user=self.admin_user)
        order_count_before = Order.objects.count()
        response = self.client.delete(self.order1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), order_count_before - 1)
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(id=self.order1.id)

    def test_delete_order_customer_fail(self):
        """ Test: Kunde kann Order NICHT löschen (403) """
        self.client.force_authenticate(user=self.customer_user1)
        response = self.client.delete(self.order1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Wegen IsAdminUser

    def test_delete_order_provider_fail(self):
        """ Test: Anbieter kann Order NICHT löschen (403) """
        self.client.force_authenticate(user=self.business_user1)
        response = self.client.delete(self.order1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Wegen IsAdminUser

    def test_delete_order_not_found(self):
        """ Test: Löschen nicht existierender Order (404) """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.order_non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # === GET /api/orders/business/{id}/ Tests ===

    def test_list_business_orders_success(self):
        """ Test: Auflisten der Orders eines Business Users (AllowAny) """
        response = self.client.get(self.business1_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Business User 1 ist Anbieter für Order 1, 2, 4
        self.assertEqual(len(response.data), 3)
        order_ids = {item['id'] for item in response.data}
        self.assertIn(self.order1.id, order_ids)
        self.assertIn(self.order2.id, order_ids)
        self.assertIn(self.order4.id, order_ids)

    def test_list_business_orders_other_success(self):
        """ Test: Auflisten der Orders eines anderen Business Users """
        response = self.client.get(self.business2_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Business User 2 ist Anbieter für Order 3
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order3.id)

    def test_list_business_orders_non_existent_empty(self):
        """ Test: Auflisten für nicht existierenden Business User gibt leere Liste """
        response = self.client.get(self.business_non_existent_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # === GET /api/completed-order-count/{id}/ Tests ===

    def test_completed_count_success(self):
        """ Test: Zählen abgeschlossener Orders """
        response = self.client.get(self.business1_completed_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'completed_order_count': 1}) # Nur Order 4

    def test_completed_count_other_success(self):
        """ Test: Zählen abgeschlossener Orders für anderen User """
        response = self.client.get(self.business2_completed_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'completed_order_count': 1}) # Nur Order 3

    def test_completed_count_no_orders_zero(self):
        """ Test: Zählen für User ohne abgeschlossene Orders """
        response = self.client.get(self.business3_completed_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'completed_order_count': 0})

    def test_completed_count_non_existent_404(self):
        """ Test: Zählen für nicht existierenden User gibt 404 (wegen Prüfung in View) """
        response = self.client.get(self.business_non_existent_completed_count_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # === GET /api/order-count/{id}/ Tests (in_progress) ===

    def test_inprogress_count_success(self):
        """ Test: Zählen laufender Orders """
        response = self.client.get(self.business1_inprogress_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'order_count': 1}) # Nur Order 2

    def test_inprogress_count_other_zero(self):
        """ Test: Zählen laufender Orders für anderen User """
        response = self.client.get(self.business2_inprogress_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'order_count': 0}) # B2 hat keine laufenden

    def test_inprogress_count_no_orders_zero(self):
        """ Test: Zählen für User ohne laufende Orders """
        response = self.client.get(self.business3_inprogress_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'order_count': 0})

    def test_inprogress_count_non_existent_404(self):
        """ Test: Zählen für nicht existierenden User gibt 404 """
        response = self.client.get(self.business_non_existent_inprogress_count_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
