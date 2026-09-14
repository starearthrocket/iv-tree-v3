from decimal import Decimal

from django import forms


class DonationForm(forms.Form):
    """Validate a one-off donation amount."""

    amount = forms.DecimalField(
        label='Donation amount',
        min_value=Decimal('1.00'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'min': '1.00',
                'step': '0.01',
                'placeholder': '10.00',
                'inputmode': 'decimal',
            }
        ),
        help_text='Enter an amount of £1 or more.',
    )