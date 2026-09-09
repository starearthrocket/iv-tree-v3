from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            password='testpassword123'
        )

        self.profile = Profile.objects.create(
            user=self.user,
            avatar_choice=Profile.Avatar.OAK_LEAF,
        )

    def test_profile_page_requires_login(self):
        response = self.client.get(
            reverse('accounts:profile')
        )

        self.assertEqual(response.status_code, 302)

    def test_user_can_change_avatar(self):
        self.client.login(
            username='profileuser',
            password='testpassword123'
        )

        response = self.client.post(
            reverse('accounts:profile'),
            {
                'avatar_choice': Profile.Avatar.ROBIN,
                'bio': 'Helping protect local trees.',
            },
        )

        self.profile.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.profile.avatar_choice,
            Profile.Avatar.ROBIN
        )
        self.assertEqual(
            self.profile.bio,
            'Helping protect local trees.'
        )