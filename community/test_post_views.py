from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CommunityPost


class CommunityPostListTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='testpassword123',
        )

    def test_community_post_list_page_loads(self):
        response = self.client.get(
            reverse('community:post_list')
        )

        self.assertEqual(response.status_code, 200)

    def test_only_published_posts_are_visible(self):
        CommunityPost.objects.create(
            author=self.user,
            title='Visible post',
            content='This post should be public.',
            is_published=True,
        )

        CommunityPost.objects.create(
            author=self.user,
            title='Hidden post',
            content='This post should not be public.',
            is_published=False,
        )

        response = self.client.get(
            reverse('community:post_list')
        )

        self.assertContains(response, 'Visible post')
        self.assertNotContains(response, 'Hidden post')


class CommunityPostCreateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='testpassword123',
        )

    def test_create_post_requires_login(self):
        response = self.client.get(
            reverse('community:post_create')
        )

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_create_post(self):
        self.client.login(
            username='alice',
            password='testpassword123',
        )

        response = self.client.post(
            reverse('community:post_create'),
            {
                'title': 'Protecting an old oak',
                'content': 'We cleared ivy around this tree today.',
                'is_published': True,
            },
        )

        self.assertEqual(CommunityPost.objects.count(), 1)

        post = CommunityPost.objects.first()

        self.assertEqual(post.author, self.user)
        self.assertEqual(post.title, 'Protecting an old oak')
        self.assertEqual(response.status_code, 302)