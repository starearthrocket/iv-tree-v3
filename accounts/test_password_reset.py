import re
from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    MAILERS={
        'default': {
            'BACKEND': (
                'django.core.mail.backends.locmem.EmailBackend'
            ),
        },
    },
)
class PasswordResetViewTest(TestCase):
    """Tests for the password-reset pages and email flow."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='resetuser',
            email='reset@example.com',
            password='OldPassword123!',
        )

    def test_password_reset_page_loads(self):
        response = self.client.get(
            reverse('accounts:password_reset'),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_password_reset_done_page_loads(self):
        response = self.client.get(
            reverse('accounts:password_reset_done'),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_password_reset_flow(self):
        """A user can reset their password from the emailed link."""

        response = self.client.post(
            reverse('accounts:password_reset'),
            {
                'email': self.user.email,
            },
        )

        self.assertRedirects(
            response,
            reverse('accounts:password_reset_done'),
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email = mail.outbox[0]

        self.assertEqual(
            email.subject,
            'Reset your I-V Tree password',
        )
        self.assertIn(
            'You requested a password reset',
            email.body,
        )

        match = re.search(
            r'https?://testserver'
            r'(?P<path>/accounts/password-reset/[^\s]+)',
            email.body,
        )

        self.assertIsNotNone(match)

        reset_path = urlparse(
            match.group('path'),
        ).path

        response = self.client.get(
            reset_path,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        confirm_path = response.url

        response = self.client.get(
            confirm_path,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        response = self.client.post(
            confirm_path,
            {
                'new_password1': 'NewPassword456!',
                'new_password2': 'NewPassword456!',
            },
        )

        self.assertRedirects(
            response,
            reverse('accounts:password_reset_complete'),
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                'NewPassword456!',
            ),
        )