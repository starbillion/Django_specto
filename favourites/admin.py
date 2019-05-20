from django.contrib import admin

# Register your models here.
from favourites import models

admin.register(models.Favourite)