from django import forms

from .models import TreeReport


class TreeReportForm(forms.ModelForm):
    """Form used by members to report an affected tree."""

    class Meta:
        model = TreeReport
        fields = [
            'title',
            'tree_species',
            'description',
            'photo',
            'location_name',
            'latitude',
            'longitude',
            'what3words',
            'visibility',
        ]
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': (
                        'Describe the tree and the ivy affecting it.'
                    ),
                }
            ),
            'latitude': forms.NumberInput(
                attrs={
                    'step': '0.000001',
                    'placeholder': '51.507400',
                }
            ),
            'longitude': forms.NumberInput(
                attrs={
                    'step': '0.000001',
                    'placeholder': '-0.127800',
                }
            ),
            'what3words': forms.TextInput(
                attrs={
                    'placeholder': 'Added automatically later',
                    'readonly': 'readonly',
                }
            ),
        }
        labels = {
            'tree_species': 'Tree species',
            'location_name': 'Location',
            'what3words': 'What3words address',
        }