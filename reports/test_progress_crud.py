from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ProgressUpdate, TreeReport


class ProgressUpdateCrudTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='progressowner',
            password='testpassword123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
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

        self.update = ProgressUpdate.objects.create(
            tree_report=self.report,
            author=self.owner,
            description='Initial progress update.',
            status=TreeReport.Status.IN_PROGRESS,
        )

    def test_owner_can_edit_progress_update(self):
        self.client.login(
            username='progressowner',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'reports:progress_edit',
                args=[self.update.pk],
            ),
            {
                'description': 'Updated progress information.',
                'status': TreeReport.Status.PROTECTED,
            },
        )

        self.update.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.update.description,
            'Updated progress information.'
        )
        self.assertEqual(
            self.update.status,
            TreeReport.Status.PROTECTED
        )

    def test_other_user_cannot_edit_progress_update(self):
        self.client.login(
            username='otheruser',
            password='testpassword123'
        )

        response = self.client.get(
            reverse(
                'reports:progress_edit',
                args=[self.update.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_owner_can_delete_progress_update(self):
        self.client.login(
            username='progressowner',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'reports:progress_delete',
                args=[self.update.pk],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            ProgressUpdate.objects.filter(
                pk=self.update.pk
            ).exists()
        )