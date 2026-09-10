from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from community.models import CommunityPost
from reports.models import TreeReport


class PublicProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpassword123',
        )

        self.public_report = TreeReport.objects.create(
            owner=self.user,
            title='Public oak tree',
            description='A public tree report.',
            location_name='Brighton',
            latitude=50.822500,
            longitude=-0.137200,
            visibility=TreeReport.Visibility.PUBLIC,
        )

        self.private_report = TreeReport.objects.create(
            owner=self.user,
            title='Private tree report',
            description='This should stay private.',
            location_name='Brighton',
            latitude=50.822500,
            longitude=-0.137200,
            visibility=TreeReport.Visibility.PRIVATE,
        )

        self.published_post = CommunityPost.objects.create(
            author=self.user,
            title='Published community post',
            content='Useful public advice.',
            is_published=True,
        )

        self.hidden_post = CommunityPost.objects.create(
            author=self.user,
            title='Hidden community post',
            content='This should not be public.',
            is_published=False,
        )

    def test_public_profile_page_loads(self):
        response = self.client.get(
            reverse(
                'accounts:public_profile',
                kwargs={'username': self.user.username},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alice')

    def test_public_profile_only_shows_public_reports(self):
        response = self.client.get(
            reverse(
                'accounts:public_profile',
                kwargs={'username': self.user.username},
            )
        )

        self.assertContains(response, 'Public oak tree')
        self.assertNotContains(response, 'Private tree report')

    def test_public_profile_only_shows_published_posts(self):
        response = self.client.get(
            reverse(
                'accounts:public_profile',
                kwargs={'username': self.user.username},
            )
        )

        self.assertContains(
            response,
            'Published community post',
        )
        self.assertNotContains(
            response,
            'Hidden community post',
        )