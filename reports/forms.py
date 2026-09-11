from django import forms

from .models import ProgressUpdate, TreeReport


class TreeReportForm(forms.ModelForm):
    """Form used by members to report an affected tree."""

    class Meta:
        model = TreeReport
        fields = [
            'title',
            'tree_species',
            'description',
            'photo',
            'country',
            'region',
            'town_city',
            'latitude',
            'longitude',
            'what3words',
            'visibility',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': (
                        'e.g. Ivy-covered oak beside footpath'
                    ),
                }
            ),
            'tree_species': forms.TextInput(
                attrs={
                    'placeholder': (
                        'e.g. Oak, ash, beech — leave blank if unsure'
                    ),
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': (
                        'Describe the tree and the ivy affecting it.'
                    ),
                }
            ),
            'region': forms.TextInput(
                attrs={
                    'placeholder': (
                        'e.g. Worcestershire, Styria or California'
                    ),
                }
            ),
            'town_city': forms.TextInput(
                attrs={
                    'placeholder': (
                        'e.g. Malvern, Graz or Brighton'
                    ),
                }
            ),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'what3words': forms.HiddenInput(),
        }
        labels = {
            'tree_species': 'Tree species',
            'country': 'Country',
            'region': 'Region / county / state',
            'town_city': 'Town / city',
        }


class ProgressUpdateForm(forms.ModelForm):
    """Form used to add a progress update to a tree report."""

    class Meta:
        model = ProgressUpdate
        fields = [
            'description',
            'photo',
            'status',
        ]
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': (
                        'Describe what has changed or what action was taken.'
                    ),
                }
            ),
        }