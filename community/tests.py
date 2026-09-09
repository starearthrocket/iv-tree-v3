from django.contrib.auth.models import User
from django.test import TestCase

from .models import CommunityPost


class CommunityPostModelTest(TestCase):
    def test_community_post_creation(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        post = CommunityPost.objects.create(
            author=user,
            title='Helping an ivy-covered tree',
            content='A short community update about protecting a tree.'
        )

        self.assertEqual(post.author, user)
        self.assertTrue(post.is_published)
        self.assertEqual(
            str(post),
            'Helping an ivy-covered tree'
        )