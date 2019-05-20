from django import forms
from django.core.exceptions import ValidationError
# from django.contrib.auth.models import User
from .models import (
    User, UserProfile
)
from mainsite.models import RestrictedIPDevice
from PIL import Image
from django.contrib.auth import authenticate, password_validation

class RestrictedIPDeviceForm(forms.ModelForm):
    class Meta:
        model = RestrictedIPDevice
        fields = ('ip_device',)


class LoginForm(forms.Form):
    # username = forms.CharField(max_length=120)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


# remember = forms.BooleanField()


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=120)
    last_name = forms.CharField(max_length=120)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Validating password and confirm password
        if password and confirm_password:
            if password != confirm_password:
                self.add_error('password', ValidationError('Password confirmation failed'))

            # return self.cleaned_data

        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;,'\[\]]"
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError('Password must contain at least %(min_length)d digit.' % {'min_length': 2})

        if not any(char.isalpha() for char in password):
            raise forms.ValidationError('Password must contain at least %(min_length)d letter.' % {'min_length': 6})

        if not any(char in special_characters for char in password):
            raise forms.ValidationError('Password must contain at least %(min_length)d special character.' % {'min_length': 1})

        if len(password) < 8:
            raise forms.ValidationError('Password must contain at least %(min_length)d characters.' % {'min_length': 8})

    # def clean_email(self):
    # 	email = self.cleaned_data.get('email')
    # 	if not email or not User.objects.filter(email=email).exists():
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


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)


class AvatarUploadForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = UserProfile
        fields = ('avatar', 'x', 'y', 'width', 'height',)
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': 'image/*'  # this is not an actual validation! don't rely on that!
            })
        }

    def save(self):
        photo = super(AvatarUploadForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.avatar)
        cropped_image = image.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(photo.avatar.path)

        return photo
