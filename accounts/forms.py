from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegistrationForm(UserCreationForm):
    """Registration form for new I-V Tree members."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email address already exists.'
            )

        return email


class ProfileForm(forms.ModelForm):
    """Allow an I-V Tree member to update their profile."""

    class Meta:
        model = Profile
        fields = (
            'avatar_choice',
            'bio',
        )
        widgets = {
            'bio': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': (
                        'Tell the community a little about yourself.'
                    ),
                }
            ),
        }