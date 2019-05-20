from django.db import models
from mainsite.models import User
from stocks.models import Stock
from datetime import datetime, timedelta
from django.utils import timezone
from payment.models import Transaction
"""
Stock Subscription Plans
- Subscription time: 1 month | 6 month | 12 months
- Different subscription prices for each of the stock
"""
PLAN_DURATION_CHOICES = (
    (0, 'Unlimited'),
    (1, '1 month'),
    (2, '6 months'),
    (3, '12 months'),
)


class StockSubscription(models.Model):
    plan_duration = models.IntegerField(choices=PLAN_DURATION_CHOICES, default=0, blank=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=False, blank=True)
    status = models.BooleanField(default=True, blank=True, help_text="status is for enabling or disabling a plan")
    removed = models.BooleanField(default=False, blank=True,
                                  help_text="When a plan is removed/deleted, this is for maintaining a timeline for the plan for history")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    max_months_purchasable = models.IntegerField(default=1, blank=True,null=True,)

    @property
    def per_month_price(self):
        value = self.price / self.plan_duration
        return value


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # stock_subscription = models.ForeignKey(StockSubscription, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    subscription_started = models.DateTimeField(auto_now_add=False, blank=True)
    subscription_ends = models.DateTimeField(auto_now_add=False, default=timezone.now)
    status = models.BooleanField(default=True, blank=True)
    is_hidden = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    purchased_months = models.IntegerField(default=0, blank=True)
    total_price = models.DecimalField(max_digits=20, decimal_places=2, default=False, blank=True)

    def get_user(self):
        '''
        Return the Char result corresponding to the user
        '''
        return self.user

    def get_stock(self):
        '''
        Return the Stock corresponding to the subscription
        '''
        return self.stock

    def get_subscriptions(self):
        """
        Get the related subscriptions
        """
        return StockSubscription.objects.filter(stock_id=self.id)


class SubscriptionOrder(models.Model):
    id_list = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def set_list(self, id_list):
        if id_list:
            self.id_list = ','.join(map(str, id_list))

    @property
    def get_id_list(self):
        if self.id_list:
            return self.id_list.split(",")
        else:
            return []