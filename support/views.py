import logging
from decimal import Decimal

import stripe

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import DonationForm
from .models import Donation


logger = logging.getLogger(__name__)


def support_page(request):
    """Display the support page and create Stripe Checkout sessions."""

    if request.method == 'POST':
        form = DonationForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']

            if not settings.STRIPE_SECRET_KEY:
                messages.error(
                    request,
                    (
                        'Secure payments are temporarily unavailable. '
                        'Please try again later.'
                    ),
                )

                return render(
                    request,
                    'support/support.html',
                    {
                        'form': form,
                    },
                )

            amount_in_pence = int(
                amount * Decimal('100')
            )

            success_url = (
                request.build_absolute_uri(
                    reverse(
                        'support:donation_success'
                    )
                )
                + '?session_id={CHECKOUT_SESSION_ID}'
            )

            cancel_url = request.build_absolute_uri(
                reverse(
                    'support:donation_cancel'
                )
            )

            try:
                checkout_session = (
                    stripe.checkout.Session.create(
                        api_key=settings.STRIPE_SECRET_KEY,
                        mode='payment',
                        payment_method_types=[
                            'card',
                        ],
                        line_items=[
                            {
                                'price_data': {
                                    'currency': (
                                        settings.STRIPE_CURRENCY
                                    ),
                                    'unit_amount': (
                                        amount_in_pence
                                    ),
                                    'product_data': {
                                        'name': (
                                            'Support I-V Tree'
                                        ),
                                        'description': (
                                            'Voluntary contribution '
                                            'towards the operating and '
                                            'development costs of '
                                            'I-V Tree.'
                                        ),
                                    },
                                },
                                'quantity': 1,
                            },
                        ],
                        success_url=success_url,
                        cancel_url=cancel_url,
                        metadata={
                            'source': (
                                'iv-tree-support'
                            ),
                        },
                    )
                )

            except stripe.StripeError as error:
                logger.warning(
                    'Stripe Checkout session creation failed: %s',
                    error,
                )

                messages.error(
                    request,
                    (
                        'We could not start the secure payment '
                        'process. Please try again.'
                    ),
                )

                return render(
                    request,
                    'support/support.html',
                    {
                        'form': form,
                    },
                )

            Donation.objects.create(
                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                amount=amount,
                stripe_session_id=checkout_session.id,
                payment_status=(
                    Donation.PaymentStatus.PENDING
                ),
            )

            return redirect(
                checkout_session.url
            )

    else:
        form = DonationForm()

    return render(
        request,
        'support/support.html',
        {
            'form': form,
        },
    )


def donation_success(request):
    """Display the return page after Stripe Checkout."""

    return render(
        request,
        'support/donation_success.html',
    )


def donation_cancel(request):
    """Display feedback when Stripe Checkout is cancelled."""

    return render(
        request,
        'support/donation_cancel.html',
    )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Receive and verify Stripe payment events."""

    payload = request.body

    signature = request.META.get(
        'HTTP_STRIPE_SIGNATURE',
        '',
    )

    webhook_secret = (
        settings.STRIPE_WEBHOOK_SECRET
    )

    if not webhook_secret:
        logger.error(
            'Stripe webhook secret is not configured.'
        )

        return HttpResponse(
            status=400
        )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            webhook_secret,
        )

    except ValueError as error:
        logger.warning(
            'Invalid Stripe webhook payload: %s',
            error,
        )

        return HttpResponse(
            status=400
        )

    except stripe.SignatureVerificationError as error:
        logger.warning(
            'Invalid Stripe webhook signature: %s',
            error,
        )

        return HttpResponse(
            status=400
        )

    event_data = event.to_dict()

    event_type = event_data.get(
        'type'
    )

    checkout_session = (
        event_data.get('data', {})
        .get('object', {})
    )

    stripe_session_id = (
        checkout_session.get('id')
    )

    if stripe_session_id:

        try:
            donation = Donation.objects.get(
                stripe_session_id=stripe_session_id
            )

        except Donation.DoesNotExist:
            logger.warning(
                (
                    'Stripe webhook received for '
                    'unknown Checkout Session: %s'
                ),
                stripe_session_id,
            )

            return HttpResponse(
                status=200
            )

        if (
            event_type
            == 'checkout.session.completed'
            and checkout_session.get(
                'payment_status'
            ) == 'paid'
        ):
            donation.payment_status = (
                Donation.PaymentStatus.PAID
            )

            donation.save(
                update_fields=[
                    'payment_status',
                ]
            )

        elif (
            event_type
            == 'checkout.session.async_payment_failed'
        ):
            donation.payment_status = (
                Donation.PaymentStatus.FAILED
            )

            donation.save(
                update_fields=[
                    'payment_status',
                ]
            )

        elif (
            event_type
            == 'checkout.session.expired'
        ):
            donation.payment_status = (
                Donation.PaymentStatus.CANCELLED
            )

            donation.save(
                update_fields=[
                    'payment_status',
                ]
            )

    return HttpResponse(
        status=200
    )