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

    def test_authenticated_user_cannot_open_register_page(self):
        user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='StrongTestPassword123!'
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse('accounts:register')
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('core:home')
        )


class LoginViewTest(TestCase):
    def test_authenticated_user_cannot_open_login_page(self):
        user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='StrongTestPassword123!'
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse('accounts:login')
        )

        self.assertEqual(response.status_code, 302)