from django import forms
from .models import Profile, Order, Cake
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Profile
        fields = ['address', 'phone']

class OrderForm(forms.ModelForm):
    cake = forms.ModelChoiceField(queryset=Cake.objects.all(), empty_label="Select Cake")
    
    class Meta:
        model = Order
        fields = ['cake', 'quantity']

