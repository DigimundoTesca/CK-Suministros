from django import forms

from users.models import User as UserProfile, CustomerProfile


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'is_active']


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['user', 'email', 'phone_number', 'longitude', 'latitude', 'address', 'first_dabba']


