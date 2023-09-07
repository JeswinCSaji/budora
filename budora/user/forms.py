from django import forms
from .models import Certification  # Import the Certification model from your app

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = [
            'certification_image',  # Change the field name to 'certification_image'
            'owner_name', 'store_name',
            'expiry_date_from',
            'expiry_date_to',
            
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


