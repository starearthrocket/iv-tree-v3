from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegistrationViewTest(TestCase):
    def test_registration_creates_user_and_profile(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'StrongTestPassword123!',
                'password2': 'StrongTestPassword123!',
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='newuser')

        self.assertEqual(
            user.email,
            'newuser@example.com'
        )
        self.assertTrue(
            hasattr(user, 'profile')
        )

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='StrongTestPassword123!'
        )

        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'anotheruser',
                'email': 'existing@example.com',
                'password1': 'StrongTestPassword123!',
                'password2': 'StrongTestPassword123!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            User.objects.filter(
                email='existing@example.com'
            ).count(),
            1
        )