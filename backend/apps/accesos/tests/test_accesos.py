from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import UGELDelegation, Period

User = get_user_model()


class AccesosTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.directora = User.objects.create_user(username='dir', email='dir@example.com', password='pass')
        setattr(self.directora, 'role', 'Directora'); self.directora.save()
        self.tutor = User.objects.create_user(username='tutor', email='tutor@example.com', password='pass')
        setattr(self.tutor, 'role', 'Tutor'); self.tutor.save()
        self.other = User.objects.create_user(username='other', email='other@example.com', password='pass')
        setattr(self.other, 'role', 'Padre'); self.other.save()

    def test_delegation_by_directora(self):
        self.client.force_authenticate(user=self.directora)
        url = reverse('accesos-ugel-delegate')
        resp = self.client.post(url, {'tutor_id': self.tutor.id}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(UGELDelegation.objects.filter(tutor=self.tutor, delegated_by=self.directora, active=True).exists())

    def test_tutor_access_ugel_without_delegation(self):
        self.client.force_authenticate(user=self.tutor)
        url = reverse('accesos-ugel-manage')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_tutor_access_ugel_with_delegation(self):
        UGELDelegation.objects.create(tutor=self.tutor, delegated_by=self.directora, active=True)
        self.client.force_authenticate(user=self.tutor)
        url = reverse('accesos-ugel-manage')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_close_period_and_edit_after_close_returns_409(self):
        p = Period.objects.create(name='Mes1', closed=False)
        self.client.force_authenticate(user=self.directora)
        url_close = reverse('accesos-close-period', kwargs={'period_id': p.id})
        resp1 = self.client.post(url_close)
        self.assertEqual(resp1.status_code, 200)
        resp2 = self.client.post(url_close)
        self.assertEqual(resp2.status_code, 409)

    def test_password_reset_mock_flow(self):
        url_req = reverse('accesos-password-reset-request')
        resp = self.client.post(url_req, {'email': self.tutor.email}, format='json')
        self.assertEqual(resp.status_code, 201)
        token = resp.data.get('token')
        url_confirm = reverse('accesos-password-reset-confirm')
        resp2 = self.client.post(url_confirm, {'token': token, 'password': 'newstrongpass'}, format='json')
        self.assertEqual(resp2.status_code, 200)
