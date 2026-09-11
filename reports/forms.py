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
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'what3words': forms.HiddenInput(),
        }
        labels = {
            'tree_species': 'Tree species',
            'location_name': 'Town or county',
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