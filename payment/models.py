from django.db import models
from mainsite.models import User
from decimal import Decimal
from django.contrib.postgres.fields import JSONField

from payments import PurchasedItem
from payments.models import BasePayment


class Payment(BasePayment):
    def get_failure_url(self):
        return 'http://example.com/failure/'

    def get_success_url(self):
        return 'http://example.com/success/'

    def get_purchased_items(self):
        # you'll probably want to retrieve these from an associated order
        yield PurchasedItem(name='The Hound of the Baskervilles', sku='BSKV',
                            quantity=9, price=Decimal(10), currency='USD')


class UserBillingAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=55, blank=True, null=True)
    state = models.CharField(max_length=55, blank=True, null=True)
    city = models.CharField(max_length=55, blank=True, null=True)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_type = models.CharField(max_length=255, blank=True, null=True)
    cart_details = models.TextField(blank=True, null=True)
    user_agent = models.TextField()
    ip = models.CharField(max_length=255, blank=True, null=True)
    amount = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.BooleanField(default=True, help_text='Designates whether the tr for login was successfull or not')
