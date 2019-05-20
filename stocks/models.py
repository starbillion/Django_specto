from django.db import models
import certifi, urllib3
import json
import time
from datetime import datetime
from django.db.models import Avg
from django.utils.timezone import localdate
"""
 Get all active stocks
"""
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
from django.conf import settings


class Stock(models.Model):
    symbol = models.CharField(max_length=50, null=True, blank=True, unique=True, help_text="Company name, acts as key")
    name = models.CharField(max_length=150, null=True, blank=True, help_text="Name of the company")
    last_sale = models.CharField(max_length=100, default=False, blank=True)
    market_cap = models.CharField(max_length=100, default=False, blank=True)
    adr_tso = models.CharField(max_length=100, default=False, blank=True)
    ipo_year = models.CharField(max_length=100, default=False, blank=True)
    sector = models.CharField(max_length=100, default=False, blank=True)
    industry = models.TextField(default=False, blank=True)
    status = models.BooleanField(default=True, blank=True)
    coming_soon = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def get_symbol(self):
        '''
        Return the Char result corresponding to the company symbol
        '''
        return self.symbol

    def get_company_name(self):
        '''
        Return the Text result corresponding to the company's name
        '''
        return self.name

    def get_subscription_user(self):
        return self.subscription_set.filter(stock_id=1)

    @property
    def get_stock_company_data(self):
        """
        :return: Returns the company data from symbol, querying API
        """
        try:
            url = settings.C_API_STOCK___BASE_URL + 'stock/' + self.symbol.lower() + '/company/'
            r = http.request('get', url)
            return json.loads(r.data)
        except Exception as e:
            return dict()

    @property
    def get_stock_stats_left(self):
        """
        :return: left stats fro API
        """
        try:
            url = settings.C_API_STOCK___BASE_URL + 'stock/' + self.symbol.lower() + '/quote/'
            r = http.request('get', url)
            return json.loads(r.data)
        except Exception as e:
            return dict()

    @property
    def get_predictions(self):
        """
        :return: Returns predictions of a stock for current date
        """
        if self.stockprediction_set.filter(prediction_date=localdate()).exists():
            stock_prediction = self.stockprediction_set.filter(prediction_date=localdate()).first()
        else:
            stock_prediction = []
        return stock_prediction

    @property
    def get_all_time_avg(self):
        """
        Get all time avg of accuracy_prev_day from StockPrediction for a particular stock
        :return:
        """
        try:
            if self.stockprediction_set.first():
                all_average = self.stockprediction_set.aggregate(Avg('accuracy_prev_day'))
                if all_average.get('accuracy_prev_day__avg'):
                    return float(("%0.2f" % (all_average['accuracy_prev_day__avg'])))
                else:
                    return float()
        except Exception as e:
            print(e)
        return float()

    @property
    def get_prev_day_prediction(self):
        """
        Get accuracy_prev_day from StockPrediction for a particular stock
        :return:
        """
        try:
            prediction = self.stockprediction_set.first()
            if prediction:
                return float(("%0.2f" % (float(prediction.accuracy_prev_day))))
            else:
                return float()
        except Exception as e:
            pass
        return float()

    @property
    def has_subscription(self):
        """
        :return: Returns True if stock has subscription
        """
        return self.stocksubscription_set.filter(status=True, removed=False,
                                                 valid_until__gte=localdate()).first()

    @property
    def get_least_price(self):
        value = 0
        try:
            all_subscriptions_qs = self.stocksubscription_set.filter(status=True, valid_until__gte=localdate()).filter(removed=False)
            if all_subscriptions_qs.exists():
                sub = min(all_subscriptions_qs.all(), key=lambda o: o.per_month_price)
                return sub.per_month_price
            else:
                return 0
        except Exception as e:
            print(e)
        return value

    @property
    def get_highest_price(self):
        value = 0
        try:
            all_subscriptions_qs = self.stocksubscription_set.filter(status=True, valid_until__gte=localdate()).filter(
                removed=False)
            if all_subscriptions_qs.exists():
                sub = max(all_subscriptions_qs.all(), key=lambda o: o.per_month_price)
                return sub.per_month_price
            else:
                return 0
        except Exception as e:
            print(e)
        return value

    @property
    def get_subscribed_user_count(self):
        value = 0
        try:
            return self.stocksubscription_set.filter(subscription__subscription_ends__gte=localdate()).count()
        except Exception as e:
            print(e)
        return value

    @property
    def get_favourite_count(self):
        value = 0
        try:
            return self.favourite_set.filter(status=True).count()
        except Exception as e:
            print(e)
        return value
'''
 Company name and id both have been added, however id(stock) is more of a dependable factor,
 symbol has been added for ease in case of bulk uploads
'''


class StockPrediction(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    prediction_date = models.DateField(blank=True)
    high = models.CharField(max_length=100, default=False, blank=True)
    low = models.CharField(max_length=100, default=False, blank=True)
    close = models.CharField(max_length=100, default=False, blank=True)
    accuracy_prev_day = models.FloatField(blank=True)
    status = models.BooleanField(default=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def get_symbol(self):
        '''
        Return the Char result corresponding to the company symbol
        '''
        return self.symbol

    def get_company_name(self):
        '''
        Return the Text result corresponding to the company's name
        '''
        return self.name

    class Meta:
        unique_together = ('stock', 'prediction_date',)
