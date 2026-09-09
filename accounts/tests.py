from django.contrib.auth.models import User
from django.test import TestCase

from .models import Profile


class ProfileModelTest(TestCase):
    def test_profile_links_to_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        profile = Profile.objects.create(
            user=user,
            avatar_choice='avatar-oak-leaf.png'
        )

        self.assertEqual(profile.user, user)
        self.assertEqual(
            profile.avatar_choice,
            'avatar-oak-leaf.png'
        )