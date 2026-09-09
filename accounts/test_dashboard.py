from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from community.models import CommunityPost
from reports.models import ProgressUpdate, TreeReport


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dashboarduser',
            password='testpassword123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        self.report = TreeReport.objects.create(
            owner=self.user,
            title='My dashboard tree',
            description='A tree owned by the dashboard user.',
            location_name='Brighton',
            latitude=50.822500,
            longitude=-0.137200,
        )

        TreeReport.objects.create(
            owner=self.other_user,
            title='Someone else tree',
            description='This should not appear.',
            location_name='Hove',
            latitude=50.827900,
            longitude=-0.168700,
        )

        self.update = ProgressUpdate.objects.create(
            tree_report=self.report,
            author=self.user,
            description='My progress update.',
        )

        self.post = CommunityPost.objects.create(
            author=self.user,
            title='My community post',
            content='Dashboard community content.',
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(
            reverse('accounts:dashboard')
        )

        self.assertEqual(response.status_code, 302)

    def test_dashboard_only_shows_users_content(self):
        self.client.login(
            username='dashboarduser',
            password='testpassword123'
        )

        response = self.client.get(
            reverse('accounts:dashboard')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My dashboard tree')
        self.assertContains(response, 'My progress update')
        self.assertContains(response, 'My community post')
        self.assertNotContains(response, 'Someone else tree')