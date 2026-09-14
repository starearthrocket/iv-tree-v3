from unittest.mock import Mock, patch

import stripe

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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


class SupportPageTest(TestCase):
    def test_support_page_loads(self):
        response = self.client.get(
            reverse('support:support_page')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Help keep I-V Tree growing'
        )

    @patch(
        'support.views.stripe.checkout.Session.create'
    )
    def test_valid_donation_creates_checkout_session(
        self,
        mock_session_create,
    ):
        mock_session = Mock()
        mock_session.id = 'cs_test_checkout'
        mock_session.url = (
            'https://checkout.stripe.com/test-session'
        )

        mock_session_create.return_value = (
            mock_session
        )

        response = self.client.post(
            reverse('support:support_page'),
            {
                'amount': '5.00',
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url,
            'https://checkout.stripe.com/test-session'
        )

        donation = Donation.objects.get(
            stripe_session_id='cs_test_checkout'
        )

        self.assertEqual(
            str(donation.amount),
            '5.00'
        )

        self.assertEqual(
            donation.payment_status,
            Donation.PaymentStatus.PENDING
        )

        mock_session_create.assert_called_once()

    @patch(
        'support.views.stripe.checkout.Session.create'
    )
    def test_logged_in_donation_links_to_user(
        self,
        mock_session_create,
    ):
        user = User.objects.create_user(
            username='supporter',
            password='testpassword123'
        )

        self.client.login(
            username='supporter',
            password='testpassword123'
        )

        mock_session = Mock()
        mock_session.id = 'cs_test_user'
        mock_session.url = (
            'https://checkout.stripe.com/user-session'
        )

        mock_session_create.return_value = (
            mock_session
        )

        self.client.post(
            reverse('support:support_page'),
            {
                'amount': '12.00',
            },
        )

        donation = Donation.objects.get(
            stripe_session_id='cs_test_user'
        )

        self.assertEqual(
            donation.user,
            user
        )

    def test_donation_below_minimum_is_rejected(self):
        response = self.client.post(
            reverse('support:support_page'),
            {
                'amount': '0.50',
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Donation.objects.count(),
            0
        )

        self.assertContains(
            response,
            'Ensure this value is greater than or equal to 1.00'
        )

    @patch(
        'support.views.stripe.checkout.Session.create'
    )
    def test_stripe_error_does_not_create_donation(
        self,
        mock_session_create,
    ):
        mock_session_create.side_effect = (
            stripe.StripeError(
                'Stripe test error'
            )
        )

        response = self.client.post(
            reverse('support:support_page'),
            {
                'amount': '5.00',
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Donation.objects.count(),
            0
        )

        self.assertContains(
            response,
            (
                'We could not start the secure '
                'payment process.'
            )
        )

    def test_success_page_loads(self):
        response = self.client.get(
            reverse('support:donation_success')
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            'Thank you for supporting I-V Tree'
        )

    def test_cancel_page_loads(self):
        response = self.client.get(
            reverse('support:donation_cancel')
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            'No payment was taken'
        )


class StripeWebhookTest(TestCase):
    def setUp(self):
        self.donation = Donation.objects.create(
            amount='10.00',
            stripe_session_id='cs_test_webhook',
            payment_status=(
                Donation.PaymentStatus.PENDING
            ),
        )

    @patch(
        'support.views.stripe.Webhook.construct_event'
    )
    def test_completed_checkout_marks_donation_paid(
        self,
        mock_construct_event,
    ):
        mock_event = Mock()

        mock_event.to_dict.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_webhook',
                    'payment_status': 'paid',
                },
            },
        }

        mock_construct_event.return_value = (
            mock_event
        )

        response = self.client.post(
            reverse('support:stripe_webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 200)

        self.donation.refresh_from_db()

        self.assertEqual(
            self.donation.payment_status,
            Donation.PaymentStatus.PAID
        )

    @patch(
        'support.views.stripe.Webhook.construct_event'
    )
    def test_failed_payment_marks_donation_failed(
        self,
        mock_construct_event,
    ):
        mock_event = Mock()

        mock_event.to_dict.return_value = {
            'type': (
                'checkout.session.async_payment_failed'
            ),
            'data': {
                'object': {
                    'id': 'cs_test_webhook',
                },
            },
        }

        mock_construct_event.return_value = (
            mock_event
        )

        response = self.client.post(
            reverse('support:stripe_webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 200)

        self.donation.refresh_from_db()

        self.assertEqual(
            self.donation.payment_status,
            Donation.PaymentStatus.FAILED
        )

    @patch(
        'support.views.stripe.Webhook.construct_event'
    )
    def test_expired_checkout_marks_donation_cancelled(
        self,
        mock_construct_event,
    ):
        mock_event = Mock()

        mock_event.to_dict.return_value = {
            'type': 'checkout.session.expired',
            'data': {
                'object': {
                    'id': 'cs_test_webhook',
                },
            },
        }

        mock_construct_event.return_value = (
            mock_event
        )

        response = self.client.post(
            reverse('support:stripe_webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 200)

        self.donation.refresh_from_db()

        self.assertEqual(
            self.donation.payment_status,
            Donation.PaymentStatus.CANCELLED
        )

    @patch(
        'support.views.stripe.Webhook.construct_event'
    )
    def test_invalid_webhook_signature_returns_400(
        self,
        mock_construct_event,
    ):
        mock_construct_event.side_effect = (
            stripe.SignatureVerificationError(
                'Invalid signature',
                'test-signature',
            )
        )

        response = self.client.post(
            reverse('support:stripe_webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 400)

        self.donation.refresh_from_db()

        self.assertEqual(
            self.donation.payment_status,
            Donation.PaymentStatus.PENDING
        )

    @patch(
        'support.views.stripe.Webhook.construct_event'
    )
    def test_unknown_checkout_session_returns_200(
        self,
        mock_construct_event,
    ):
        mock_event = Mock()

        mock_event.to_dict.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_unknown',
                    'payment_status': 'paid',
                },
            },
        }

        mock_construct_event.return_value = (
            mock_event
        )

        response = self.client.post(
            reverse('support:stripe_webhook'),
            data=b'{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test-signature',
        )

        self.assertEqual(response.status_code, 200)