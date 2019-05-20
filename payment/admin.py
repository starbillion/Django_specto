from django.contrib import admin

# Register your models here.
from payment import models

admin.register(models.Payment)
admin.register(models.Transaction)
admin.register(models.UserBillingAddress)
