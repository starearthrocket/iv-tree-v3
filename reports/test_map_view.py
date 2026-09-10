from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import TreeReport


class ReportMapViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='testpassword123',
        )

        self.public_report = TreeReport.objects.create(
            owner=self.user,
            title='Public ivy-covered oak',
            description='Visible on the public map.',
            location_name='Brighton',
            latitude=50.822500,
            longitude=-0.137200,
            visibility=TreeReport.Visibility.PUBLIC,
        )

        self.private_report = TreeReport.objects.create(
            owner=self.user,
            title='Private tree',
            description='Must not appear on the public map.',
            location_name='Brighton',
            latitude=50.820000,
            longitude=-0.140000,
            visibility=TreeReport.Visibility.PRIVATE,
        )

    def test_map_page_loads(self):
        response = self.client.get(
            reverse('reports:report_map')
        )

        self.assertEqual(response.status_code, 200)

    def test_public_reports_are_available_to_map(self):
        response = self.client.get(
            reverse('reports:report_map')
        )

        self.assertContains(
            response,
            'Public ivy-covered oak',
        )

    def test_private_reports_are_not_available_to_map(self):
        response = self.client.get(
            reverse('reports:report_map')
        )

        self.assertNotContains(
            response,
            'Private tree',
        )