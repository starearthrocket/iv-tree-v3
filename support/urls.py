from django.urls import path

from . import views


app_name = 'support'


urlpatterns = [
    path(
        '',
        views.support_page,
        name='support_page',
    ),
    path(
        'success/',
        views.donation_success,
        name='donation_success',
    ),
    path(
        'cancel/',
        views.donation_cancel,
        name='donation_cancel',
    ),
    path(
        'webhook/',
        views.stripe_webhook,
        name='stripe_webhook',
    ),
]