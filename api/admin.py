from django.contrib import admin
from subscriptions.models import Subscription
admin.site.site_header = "Specto super admin"
admin.site.register(Subscription)