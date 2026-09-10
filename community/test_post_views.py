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


class CommunityPostDetailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='testpassword123',
        )

        self.post = CommunityPost.objects.create(
            author=self.user,
            title='How do I safely cut ivy?',
            content='Useful tree-care guidance.',
            is_published=True,
        )

    def test_published_post_detail_page_loads(self):
        response = self.client.get(
            reverse(
                'community:post_detail',
                kwargs={'pk': self.post.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'How do I safely cut ivy?',
        )

    def test_unpublished_post_is_hidden_from_other_users(self):
        other_user = User.objects.create_user(
            username='bob',
            password='testpassword123',
        )

        self.post.is_published = False
        self.post.save()

        self.client.login(
            username='bob',
            password='testpassword123',
        )

        response = self.client.get(
            reverse(
                'community:post_detail',
                kwargs={'pk': self.post.pk},
            )
        )

        self.assertEqual(response.status_code, 404)


class CommunityPostEditTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='testpassword123',
        )

        self.post = CommunityPost.objects.create(
            author=self.user,
            title='Original title',
            content='Original content.',
            is_published=True,
        )

    def test_owner_can_edit_post(self):
        self.client.login(
            username='alice',
            password='testpassword123',
        )

        response = self.client.post(
            reverse(
                'community:post_edit',
                kwargs={'pk': self.post.pk},
            ),
            {
                'title': 'Updated title',
                'content': 'Updated content.',
                'is_published': True,
            },
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.title,
            'Updated title',
        )
        self.assertEqual(response.status_code, 302)

    def test_other_user_cannot_edit_post(self):
        User.objects.create_user(
            username='bob',
            password='testpassword123',
        )

        self.client.login(
            username='bob',
            password='testpassword123',
        )

        response = self.client.get(
            reverse(
                'community:post_edit',
                kwargs={'pk': self.post.pk},
            )
        )

        self.assertEqual(response.status_code, 404)


class CommunityPostDeleteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='testpassword123',
        )

        self.post = CommunityPost.objects.create(
            author=self.user,
            title='Post to delete',
            content='Temporary content.',
            is_published=True,
        )

    def test_owner_can_delete_post(self):
        self.client.login(
            username='alice',
            password='testpassword123',
        )

        response = self.client.post(
            reverse(
                'community:post_delete',
                kwargs={'pk': self.post.pk},
            )
        )

        self.assertEqual(
            CommunityPost.objects.count(),
            0,
        )
        self.assertEqual(response.status_code, 302)

    def test_other_user_cannot_delete_post(self):
        User.objects.create_user(
            username='bob',
            password='testpassword123',
        )

        self.client.login(
            username='bob',
            password='testpassword123',
        )

        response = self.client.post(
            reverse(
                'community:post_delete',
                kwargs={'pk': self.post.pk},
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            CommunityPost.objects.filter(
                pk=self.post.pk
            ).exists()
        )