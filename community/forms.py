from django import forms

from .models import CommunityPost


class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = [
            'title',
            'content',
            'image',
            'is_published',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'Give your post a title',
                }
            ),
            'content': forms.Textarea(
                attrs={
                    'rows': 7,
                    'placeholder': (
                        'Share an update, conservation story or useful tip...'
                    ),
                }
            ),
        }