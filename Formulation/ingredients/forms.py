from django import forms
from .models import MaterialAttribute

class MaterialAttributeForm(forms.ModelForm):
    class Meta:
        model = MaterialAttribute
        fields = ['name', 'description']