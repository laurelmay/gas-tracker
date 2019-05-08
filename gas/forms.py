from django import forms
from django.forms import ModelForm

from .models import *


class GasPurchaseForm(ModelForm):
    class Meta:
        model = GasPurchase
        fields = [
            'vehicle',
            'datetime',
            'odometer_reading',
            'cost_per_gallon',
            'gallons',
        ]
