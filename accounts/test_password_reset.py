from django.test import TestCase
from django.urls import reverse


class PasswordResetViewTest(TestCase):
    def test_password_reset_page_loads(self):
        response = self.client.get(
            reverse('accounts:password_reset')
        )

        self.assertEqual(response.status_code, 200)

    def test_password_reset_done_page_loads(self):
        response = self.client.get(
            reverse('accounts:password_reset_done')
        )

        self.assertEqual(response.status_code, 200)