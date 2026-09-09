from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ProgressUpdate, TreeReport


class TreeReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_tree_report_defaults(self):
        report = TreeReport.objects.create(
            owner=self.user,
            title='Ivy-covered oak',
            description='Large amount of ivy covering the trunk.',
            location_name='Test location',
            latitude=51.507400,
            longitude=-0.127800,
        )

        self.assertEqual(report.status, 'ACTIVE')
        self.assertEqual(report.visibility, 'PUBLIC')
        self.assertEqual(str(report), 'Ivy-covered oak')

    def test_progress_update_links_to_tree_report(self):
        report = TreeReport.objects.create(
            owner=self.user,
            title='Ivy-covered beech',
            description='Ivy covering much of the trunk.',
            location_name='Test woodland',
            latitude=51.500000,
            longitude=-0.120000,
        )

        update = ProgressUpdate.objects.create(
            tree_report=report,
            author=self.user,
            description='Ivy has been cut around the base of the tree.',
            status=TreeReport.Status.IN_PROGRESS,
        )

        self.assertEqual(update.tree_report, report)
        self.assertEqual(update.author, self.user)
        self.assertEqual(report.progress_updates.count(), 1)
        self.assertEqual(
            str(update),
            'Update for Ivy-covered beech'
        )


class TreeReportViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='reporter',
            password='testpassword123'
        )

        self.public_report = TreeReport.objects.create(
            owner=self.user,
            title='Public oak report',
            description='Visible public tree report.',
            location_name='Brighton',
            latitude=50.822500,
            longitude=-0.137200,
            visibility=TreeReport.Visibility.PUBLIC,
        )

        self.private_report = TreeReport.objects.create(
            owner=self.user,
            title='Private oak report',
            description='Private tree report.',
            location_name='Brighton',
            latitude=50.823000,
            longitude=-0.138000,
            visibility=TreeReport.Visibility.PRIVATE,
        )

    def test_report_list_only_shows_public_reports(self):
        response = self.client.get(
            reverse('reports:report_list')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public oak report')
        self.assertNotContains(response, 'Private oak report')

    def test_public_report_detail_page(self):
        response = self.client.get(
            reverse(
                'reports:report_detail',
                args=[self.public_report.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public oak report')
        self.assertContains(response, 'Brighton')