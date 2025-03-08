from django import forms
from .models import Post, User

class NewPost(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'What\'s on your mind?'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control-file text-light',
            })
        }
        labels = {
            'content': '',
            'image': '',
        }

class ProfilePicture(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']