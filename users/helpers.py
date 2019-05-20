import os
from django.http import (
    HttpResponse, HttpResponseRedirect
)
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.conf import settings
from random import choice
from string import ascii_uppercase, digits
from django.core.mail import send_mail
from .models import UserProfile


def generate_random_string(length=30):
    return ''.join(choice(ascii_uppercase + digits) for i in range(length))


def create_profile(user_id):
    obj, created = UserProfile.objects.get_or_create(user_id=user_id)
    obj.save()
    return obj


def get_user_avatar(user):
    """
    @param: authenticated user object

    @return: user_image or image_not_found URI 
    """
    if not user.id:
        return False

    try:
        if not os.path.isfile(settings.BASE_DIR + user.userprofile.avatar.url):
            return settings.C_USER_IMAGE_NOT_FOUND
    except:
        return settings.C_USER_IMAGE_NOT_FOUND

    return user.userprofile.avatar.url


# def handle_uploaded_file(f):
#     with open('some/file/name.txt', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)

def send_email(subject='Subject here', html_message='Here is the message.', sender_email='from@example.com',
               receiver_emails=['to@example.com'], fail_silently=False):
    return send_mail(
        subject,
        html_message,
        sender_email,
        receiver_emails,
        fail_silently=fail_silently,
    )
