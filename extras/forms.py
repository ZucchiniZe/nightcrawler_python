from django import forms

from .models import Playlist


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ('title', 'description', 'items')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            # 'items': forms.HiddenInput()
        }