from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Certification
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_seller','is_legaladvisor', 'is_customer','is_admin')

from django import forms
from .models import Certification  # Import the Certification model from your app

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = [
            'certification_image',  # Change the field name to 'certification_image'
            'first_name',
            'last_name',
            'expiry_date_from',
            'expiry_date_to',
            'certification_authority',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['certification_image'].required = False  # Make it optional
    
    def clean_certification_image(self):
        certification_image = self.cleaned_data.get('certification_image')

        if certification_image:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # Define allowed image extensions
            if not any(certification_image.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Only JPG, JPEG, PNG, and GIF images are allowed.")

        return certification_image  # Return the cleaned image data


