from unittest.mock import patch

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

    def test_structured_location_displays_on_detail_page(self):
        report = TreeReport.objects.create(
            owner=self.user,
            title='Structured location report',
            description='Report with structured location data.',
            country='GB',
            region='East Sussex',
            town_city='Brighton',
            latitude=50.822500,
            longitude=-0.137200,
            what3words='///test.words.here',
        )

        response = self.client.get(
            reverse(
                'reports:report_detail',
                args=[report.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Brighton')
        self.assertContains(response, 'East Sussex')
        self.assertContains(response, 'United Kingdom')
        self.assertContains(response, '///test.words.here')


class TreeReportOwnershipTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            password='testpassword123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpassword123'
        )

        self.report = TreeReport.objects.create(
            owner=self.owner,
            title='Owner report',
            description='A report belonging to the owner.',
            location_name='Brighton',
            country='GB',
            region='East Sussex',
            town_city='Brighton',
            latitude=50.822500,
            longitude=-0.137200,
        )

    @patch(
        'reports.views.convert_to_what3words',
        return_value='///updated.test.words',
    )
    def test_owner_can_edit_report(
        self,
        mock_what3words,
    ):
        self.client.login(
            username='owner',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'reports:report_edit',
                args=[self.report.pk],
            ),
            {
                'title': 'Updated owner report',
                'tree_species': 'Oak',
                'description': 'Updated description.',
                'country': 'GB',
                'region': 'East Sussex',
                'town_city': 'Brighton',
                'latitude': '50.822500',
                'longitude': '-0.137200',
                'what3words': '',
                'visibility': 'PUBLIC',
            },
        )

        self.report.refresh_from_db()

        self.assertEqual(
            self.report.title,
            'Updated owner report'
        )

        self.assertEqual(
            self.report.what3words,
            '///updated.test.words'
        )

        self.assertEqual(response.status_code, 302)

        mock_what3words.assert_called_once()

    def test_other_user_cannot_edit_report(self):
        self.client.login(
            username='otheruser',
            password='testpassword123'
        )

        response = self.client.get(
            reverse(
                'reports:report_edit',
                args=[self.report.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_owner_can_delete_report(self):
        self.client.login(
            username='owner',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'reports:report_delete',
                args=[self.report.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            TreeReport.objects.filter(
                pk=self.report.pk
            ).exists()
        )


class What3WordsLookupTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='mapuser',
            password='testpassword123'
        )

    @patch(
        'reports.views.convert_from_what3words'
    )
    def test_logged_in_user_can_lookup_what3words(
        self,
        mock_lookup,
    ):
        mock_lookup.return_value = {
            'latitude': 50.822500,
            'longitude': -0.137200,
            'what3words': '///windy.order.moods',
            'country': 'GB',
            'nearest_place': 'Brighton',
        }

        self.client.login(
            username='mapuser',
            password='testpassword123'
        )

        response = self.client.post(
            reverse('reports:what3words_lookup'),
            {
                'what3words': '///windy.order.moods',
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data['success'])

        self.assertEqual(
            data['what3words'],
            '///windy.order.moods'
        )

        self.assertEqual(
            data['country'],
            'GB'
        )

        self.assertEqual(
            data['nearest_place'],
            'Brighton'
        )

    def test_logged_out_user_cannot_lookup_what3words(self):
        response = self.client.post(
            reverse('reports:what3words_lookup'),
            {
                'what3words': '///windy.order.moods',
            },
        )

        self.assertEqual(response.status_code, 302)


class ProgressUpdateViewTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='progressowner',
            password='testpassword123'
        )

        self.report = TreeReport.objects.create(
            owner=self.owner,
            title='Monitored oak',
            description='Tree being monitored.',
            location_name='Brighton',
            latitude=50.822500,
            longitude=-0.137200,
        )

    def test_owner_can_add_progress_update(self):
        self.client.login(
            username='progressowner',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'reports:progress_create',
                args=[self.report.pk],
            ),
            {
                'description': 'Ivy has been cut around the base.',
                'status': TreeReport.Status.IN_PROGRESS,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.report.progress_updates.count(),
            1
        )

        update = self.report.progress_updates.first()

        self.assertEqual(update.author, self.owner)

        self.assertEqual(
            update.status,
            TreeReport.Status.IN_PROGRESS
        )