from django.contrib import admin

# Register your models here.
from stocks import models

admin.register(models.Stock)
admin.register(models.StockPrediction)
