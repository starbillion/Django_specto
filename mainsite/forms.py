from django import forms
from django.core.exceptions import ValidationError
# from django.contrib.auth.models import User
from .models import User, RestrictedIPDevice
from django.contrib.auth import authenticate, password_validation


class LoginForm(forms.Form):
    # username = forms.CharField(max_length=120)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

    user = authenticate(username=username, password=password)
    if not user or not user.is_active:
        raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
    # return self.cleaned_data


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=120)
    last_name = forms.CharField(max_length=120)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        email = cleaned_data.get('email')
        confirm_password = cleaned_data.get('confirm_password')

        # Validating password and confirm password
        if password and confirm_password:
            if password != confirm_password:
                self.add_error('password', ValidationError('Password confirmation failed'))

    # return self.cleaned_data
    # raise forms.ValidationError(
    #                 "Password confirmation failed"
    #             )

    # def clean_email(self):
    # 	email = self.cleaned_data.get('email')
    # 	if check_unique_email(email) > 0:
    # 		self.add_error('email', ValidationError('Email address must be unique.'))
    # 		# raise forms.ValidationError(u'Email address must be unique.')
    # 	return email

    # def clean_password(self):
    # 	password = self.cleaned_data.get('password')
    # 	confirm_password = self.cleaned_data.get('confirm_password')
    # 	if not password or password != confirm_password:
    # 		self.add_error('password', ValidationError('Password confirmation failed.'))
    # 		# raise forms.ValidationError(u'Password confirmation failed.')
    # 	return password

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password',)
