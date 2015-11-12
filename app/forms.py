from app.models import UserProfile
from django.contrib.auth.models import User
from django import forms

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('username', 'email','password')

class UserExtraForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ('address1','address2','ccn','ccnexp')
