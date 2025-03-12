from django import forms
from .models import Studio, StudioVerification

class StudioForm(forms.ModelForm):
    class Meta:
        model = Studio
        fields = ['name', 'owner', 'workers', 'description', 'address', 'equipment_list', 'pricing', 'commission_percent']
        

class StudioVerificationForm(forms.ModelForm):
    class Meta:
        model = StudioVerification
        fields = ['documents']