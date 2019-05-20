from __future__ import unicode_literals
from django.db import models
from mainsite.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.contrib.auth.models import PermissionsMixin


# from datetime import datetime
# import datetime

##Referencing the custom user model as settings.AUTH_USER_MODEL instead of importing directly
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    braintree_customer_id = models.CharField(max_length=255, blank=True, null=True)
    client_token = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=55, blank=True, null=True)
    state = models.CharField(max_length=55, blank=True, null=True)
    city = models.CharField(max_length=55, blank=True, null=True)

    # def save_avatar(self):
    #     # Opening the uploaded image
    #     im = Image.open(self.avatar)
    #     im = resize_and_crop(im, [100, 100])
    #     output = BytesIO()
    #
    #     # Resize/modify the image
    #     # im = im.resize( (200,200) )
    #
    #     # after modifications, save it to the output
    #     im.save(output, format='JPEG', quality=100)
    #     output.seek(0)
    #
    #     # change the imagefield value to be the newley modifed image value
    #     self.avatar = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.avatar.name.split('.')[0],
    #                                        'image/jpeg', sys.getsizeof(output), None)
    #     return self
    #
    # def save(self, **kwargs):
    #     self_data = self
    #     if self.avatar:
    #         self_data = self.save_avatar()
    #     super(UserProfile, self_data).save()
