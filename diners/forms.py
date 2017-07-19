from django import forms
from django.forms import ValidationError
from .models import Diner


class DinerForm(forms.ModelForm):
    class Meta:
        model = Diner
        fields = ('name', 'employee_number', 'RFID')
