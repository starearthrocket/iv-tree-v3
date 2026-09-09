from django.contrib.auth.models import User
from django.test import TestCase

from .models import TreeReport


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