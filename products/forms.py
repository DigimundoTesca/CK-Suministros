# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django import forms

from products.models import Supply, SuppliesCategory, Cartridge


class SupplyForm(forms.ModelForm):

    class Meta:
        model = Supply
        fields = '__all__'

class SuppliesCategoryForm(forms.ModelForm):

    class Meta:
        model = SuppliesCategory
        fields = '__all__'


class CartridgeForm(forms.ModelForm):

    class Meta:
        model = Cartridge
        fields = '__all__'
