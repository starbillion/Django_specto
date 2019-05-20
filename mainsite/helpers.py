# from __future__ import absolute_import

import os
from django.http import (
    HttpResponse, HttpResponseRedirect
)

from .models import (
    User, PasswordResets,
    LoginLog, RestrictedIPDevice
)
from PIL import Image
import requests, json
from ipware.ip import get_real_ip
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.conf import settings
from random import choice
from string import ascii_uppercase, digits
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site


def direct_login(request, user):
    log_request(request, user.email, True)
    return login(request, user)


def authenticate_user(request, email, password, only_admin=False):
    """
    Calling the default user auth with custom authentication, based
    on email aand password fields
    """
    user = authenticate(username=email, password=password)
    # if not authenticated
    if not user:
        log_request(request, email, False)
        return False

    # if admin
    if only_admin == True:
        if not user.is_admin():
            log_request(request, email, False)
            return False
    # if authenticated
    else:
        # if not email verfified
        if not user.is_email_verified():
            log_request(request, email, False)
            return -1
        if user.is_admin():
            log_request(request, email, False)
            return False

    if user is not None:
        restricted = is_restricted(request, user)
        # if ip/device logged in is restricted
        if restricted:
            log_request(request, email, True)
            return "restricted"
        else:
            log_request(request, email, True)
            login(request, user)
    ##Log IP and User agent details
    return user


def get_request_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    return {
        'is_mobile': request.user_agent.is_mobile,  # returns True
        'is_tablet': request.user_agent.is_tablet,  # returns False
        'is_touch_capable': request.user_agent.is_touch_capable,  # returns True
        'is_pc': request.user_agent.is_pc,  # returns False
        'is_bot': request.user_agent.is_bot,  # returns False

        # Accessing user agent's browser attributes
        'browser': request.user_agent.browser,
        # returns Browser(family=u'Mobile Safari', version=(5, 1), version_string='5.1')
        'browser_family': request.user_agent.browser.family,  # returns 'Mobile Safari'
        'browser_version': request.user_agent.browser.version,  # returns (5, 1)
        'browser_version_string': request.user_agent.browser.version_string,  # returns '5.1'

        # Operating System properties
        'os': request.user_agent.os,  # returns OperatingSystem(family=u'iOS', version=(5, 1), version_string='5.1')
        'os_family': request.user_agent.os.family,  # returns 'iOS'
        'os_version': request.user_agent.os.version,  # returns (5, 1)
        'os_version_string': request.user_agent.os.version_string,  # returns '5.1'

        # Device properties
        'device': request.user_agent.device,  # returns Device(family='iPhone')
        'device_famiy': request.user_agent.device.family,  # returns 'iPhone'
    }


# Testing IP with 157.39.155.58
"""
  Dict: acessible as ['geoplugin_city'], etc
  Sample output
  {
  	"geoplugin_city": "", 
  	"geoplugin_countryName": "India", 
  	"geoplugin_continentCode": "AS", 
  	"geoplugin_request": "157.39.155.58", 
  	"geoplugin_region": "", 
  	"geoplugin_dmaCode": "0", 
  	"geoplugin_latitude": "20", 
  	"geoplugin_credit": "Some of the returned data includes GeoLite data created by MaxMind, available from <a href='http://www.maxmind.com'>http://www.maxmind.com</a>.", 
  	"geoplugin_regionName": "", 
  	"geoplugin_currencyCode": "INR", 
  	"geoplugin_longitude": "77", 
  	"geoplugin_countryCode": "IN", 
  	"geoplugin_areaCode": "0", 
  	"geoplugin_status": 206, 
  	"geoplugin_currencyConverter": 64.34, 
  	"geoplugin_currencySymbol": "&#8360;", 
  	"geoplugin_currencySymbol_UTF8": "\u20a8", 
  	"geoplugin_regionCode": ""
  }
"""


def get_location_info_from_ip(request):
    client_ip = get_request_ip(request)
    # use this ip address for testing
    # client_ip = '157.39.155.58'
    r = requests.get('http://www.geoplugin.net/json.gp?ip=' + client_ip)
    r = json.loads(r.text)
    return r


def is_restricted(request, user):
    ip = get_request_ip(request)
    # 'is_mobile': request.user_agent.is_mobile,  # returns True
    # 'is_tablet': request.user_agent.is_tablet,  # returns False
    # 'is_touch_capable': request.user_agent.is_touch_capable,  # returns True
    # 'is_pc': request.user_agent.is_pc,  # returns False
    # 'is_bot': request.user_agent.is_bot,  # returns False
    if RestrictedIPDevice.objects.filter(user=user, ip_device=ip):
        ele = RestrictedIPDevice.objects.get(user=user, ip_device=ip)
        if ele.blocked_by_admin:
            return True
        else:
            return False
    else:
        return False


def log_request(request, user, status):
    if settings.C_IS_ENABLED_LOGIN_REQUEST_LOGGING:
        ip = get_request_ip(request)
        user_agnet = get_user_agent(request)
        created = LoginLog.objects.create(user=user,
                                          ip=ip,
                                          user_agent=user_agnet,
                                          status=status)
        return created
    return True


def register_user(data, request):
    """
    Unified func to add a new user to the system
    For now 2 tables are filled when a user is added, namely
    users.user & users.userprofile
    @return Boolean
    """
    created = False
    # try:
    is_email_confirmed = True
    email_verification_token = None
    if settings.C_USER_EMAIL_VERIFICATION_STATUS:
        is_email_confirmed = False
        email_verification_token = generate_random_string()
    user = User(email=data['email'],
                first_name=data['first_name'], last_name=data['last_name'], password=make_password(data['password']),
                is_email_confirmed=is_email_confirmed, email_verification_token=email_verification_token)
    user.save()
    # Email user with email_confirmation_token
    if settings.C_USER_EMAIL_VERIFICATION_STATUS:
        access_site = get_current_site(request)
        rendered_email_body = render_to_string('emails/registration_pending_test.html',
                                               {'user': user, 'domain': access_site.domain})
        # created = sending_email(settings.C_EMAIL_VERIFICATION_SUBJECT, rendered_email_body, settings.C_EMAIL_VERIFICATION_SENDER, [user.email])
        created = send_mail(settings.C_EMAIL_VERIFICATION_SUBJECT,
                            rendered_email_body,
                            settings.C_EMAIL_VERIFICATION_SENDER, [user.email])
    return created


def check_unique_email(email):
    return User.objects.filter(email=email).count() == 0


def generate_random_string(length=30):
    return ''.join(choice(ascii_uppercase + digits) for i in range(length))


def verify_password_token(token):
    try:
        user = PasswordResets.objects.get(token=token)
    except:
        user = None
    if user and not user.is_token_expired():
        return user
    return False


def generate_password_reset_token(email, request):
    try:
        user = User.objects.get(email=email)
    except:
        user = None
    if not user:
        return False
    ## Generate token for the requested user's password
    ## First remove all previous tokens
    PasswordResets.objects.filter(user=user).delete()
    random_string = generate_random_string()
    created = PasswordResets.objects.create(user=user, token=random_string)
    ## Send email to user for password recovery
    if settings.C_USER_PASSWORD_RECOVERY_STATUS:
        # email template for sending tmp file
        # rendered_email_body = render_to_string('emails/password_recovery.html', {'user': user, 'token': random_string})

        # email html template email
        current_site = get_current_site(request)
        rendered_email_body = render_to_string('emails/password_recovery_test.html',
                                               {'user': user,
                                                'domain': current_site.domain,
                                                'token': random_string})

        # sending email with text
        created = send_mail(settings.C_USER_PASSWORD_RECOVERY_EMAIL_SUBJECT,
                            rendered_email_body,
                            settings.C_PASSWORD_RECOVERY_SENDER, [user.email])

    # sending html template email
    # msg = EmailMessage(settings.C_USER_PASSWORD_RECOVERY_EMAIL_SUBJECT, rendered_email_body, settings.C_PASSWORD_RECOVERY_SENDER, [user.email])
    # msg.content_subtype = "html"  # Main content is now text/html
    # created = msg.send()

    if not created:
        return False
    return True


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

def sending_email(subject='Subject here', html_message='Here is the message.', sender_email='from@example.com',
                  receiver_emails=['to@example.com'], fail_silently=False):
    return send_mail(
        subject,
        html_message,
        sender_email,
        receiver_emails,
        fail_silently=fail_silently
    )


def resize_and_crop(img_obj, size, crop_type='top'):
    """
    Resize and crop an image to fit the specified size.
    args:
        img_path: path for the image to resize.
        modified_path: path to store the modified image.
        size: `(width, height)` tuple.
        crop_type: can be 'top', 'middle' or 'bottom', depending on this
            value, the image will cropped getting the 'top/left', 'midle' or
            'bottom/rigth' of the image to fit the size.
    raises:
        Exception: if can not open the file in img_path of there is problems
            to save the image.
        ValueError: if an invalid `crop_type` is provided.
    """
    # If height is higher we resize vertically, if not we resize horizontally
    # img = Image.open(img_path)
    img = img_obj
    # Get current and desired ratio for the images
    img_ratio = img.size[0] // float(img.size[1])
    ratio = size[0] // float(size[1])
    # The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], size[0] * img.size[1] // img.size[0]),
                         Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, (img.size[1] - size[1]) // 2, img.size[0], (img.size[1] + size[1]) // 2)
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else:
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((size[1] * img.size[0] // img.size[1], size[1]),
                         Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = ((img.size[0] - size[0]) // 2, 0, (img.size[0] + size[0]) // 2, img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else:
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else:
        img = img.resize((size[0], size[1]),
                         Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
    return img
