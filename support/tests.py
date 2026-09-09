from django.contrib.auth.models import User
from django.test import TestCase

from .models import Donation


class DonationModelTest(TestCase):
    def test_donation_defaults(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        donation = Donation.objects.create(
            user=user,
            amount='10.00',
            stripe_session_id='cs_test_example'
        )

        self.assertEqual(donation.user, user)
        self.assertEqual(donation.payment_status, 'PENDING')
        self.assertEqual(str(donation), '£10.00 donation')