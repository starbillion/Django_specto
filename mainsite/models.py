from __future__ import unicode_literals
import sys
from django.contrib.postgres.fields import JSONField
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from users.managers import UserManager
# from django.utils import timezone
import datetime
from PIL import Image
from django.utils.timezone import utc
from cities_light.abstract_models import (AbstractCity, AbstractRegion,
                                          AbstractCountry)
from cities_light.receivers import connect_default_signals

"""
   Email Confirmation
   1. Upon registration, 64 char long email_verification_token is generated
   2. is_email_confirmed is set to False until email not verified
   3. Upon successful verification of email:
      3.1 email_verification_token is set to NULL
      3.2 is_email_confirmed is set to TRUE
      3.3 email_verification can be turned on/off from settings.py configuration, setting.py>C_USER_EMAIL_VERIFICATION_STATUS
      3.4 email_verification_token expires in a predefined time, settings.py>EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS
"""


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(_('active'), default=True, help_text=_(
        'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    is_email_confirmed = models.BooleanField(_('active'), default=True, help_text=_(
        'Designates whether this user has got email confirmation done or not'))
    email_verification_token = models.CharField(max_length=100, null=True, blank=True,
                                                help_text="Is updated to null post successful email confirmation")
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    verbose_name = _('user')
    verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def is_admin(self):
        '''
        Return the Boolean result corrsponsing to the users email verification status
        '''
        return self.is_staff

    def is_email_verified(self):
        '''
        Return the Boolean result corrsponsing to the users email verification status
        '''
        if not settings.C_USER_EMAIL_VERIFICATION_STATUS:
            return False
        return self.is_email_confirmed

    def get_email_verification_token(self):
        '''
        Return the Boolean result corrsponsing to the users email verification status
        '''
        return self.email_verification_token

    def is_email_verification_token_expired(self):
        '''
        Return the Boolean result corresponding to the users email verification status
        '''
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        timediff = now - self.created_at
        if timediff.seconds / 3600 - settings.C_EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS > 0:
            return True
        return False

    def get_email(self):
        '''
        Returns the short name for the user.
        '''
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


class PasswordResets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, null=True, blank=True,
                             help_text="Is updated to null post successful password reset")
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def get_token(self):
        '''
        Return the Boolean result corrsponsing to the users email verification status
        '''
        return self.token

    def is_token_expired(self):
        '''
        Return the Boolean result corresponding to the users email verification status
        '''
        if self.token == None:
            return False
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        timediff = now - self.created_at
        if timediff.seconds / 3600 - settings.C_PASSWORD_RECOVERY_TOKEN_EXPIRY_HOURS > 0:
            return True
        return False


"""
 <user_agent>: JSONField
 # Let's assume that the visitor uses an iPhone...
    request.user_agent.is_mobile # returns True
    request.user_agent.is_tablet # returns False
    request.user_agent.is_touch_capable # returns True
    request.user_agent.is_pc # returns False
    request.user_agent.is_bot # returns False

    # Accessing user agent's browser attributes
    request.user_agent.browser  # returns Browser(family=u'Mobile Safari', version=(5, 1), version_string='5.1')
    request.user_agent.browser.family  # returns 'Mobile Safari'
    request.user_agent.browser.version  # returns (5, 1)
    request.user_agent.browser.version_string   # returns '5.1'

    # Operating System properties
    request.user_agent.os  # returns OperatingSystem(family=u'iOS', version=(5, 1), version_string='5.1')
    request.user_agent.os.family  # returns 'iOS'
    request.user_agent.os.version  # returns (5, 1)
    request.user_agent.os.version_string  # returns '5.1'

    # Device properties
    request.user_agent.device  # returns Device(family='iPhone')
    request.user_agent.device.family  # returns 'iPhone'
"""


class LoginLog(models.Model):
    user = models.CharField(max_length=50, null=True, blank=True,
                            help_text="Email passed to login, might not exist with the system")
    ip = models.CharField(max_length=50, null=True, blank=True, help_text="IP address at the time of loggin in")
    user_agent = models.TextField()
    status = models.BooleanField(_('active'), default=False,
                                 help_text=_('Designates whether the request for login was successfull or not'))
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def get_ip(self):
        '''
        Return the Char result corrsponsing to the users ip when logging in
        '''
        return self.ip

    def get_user_agent(self):
        '''
        Return the Text result corresponding to the users user-agent
        '''
        return self.user_agent


class RestrictedIPDevice(models.Model):
    user = models.CharField(max_length=50, null=True, blank=True,
                            help_text="user ID")
    ip_device = models.CharField(max_length=250, null=True, blank=True, help_text="Restricted IP address or device")
    blocked_by_admin = models.BooleanField(_('active'), default=True,
                                           help_text=_('This field show IP or Device is blocked by admin'))
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    who_did = models.CharField(max_length=250, null=True, blank=True, help_text="Determines who added this User or Admin")

    def get_blocked_by_admin(self):
        '''
        Return the status of blocked_by_admin blocked by admin
        '''
        return self.blocked_by_admin