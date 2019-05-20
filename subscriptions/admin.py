from django.contrib import admin

# Register your models here.
from subscriptions.models import StockSubscription, Subscription

admin.register(StockSubscription)

admin.register(Subscription)
