from cart.models import Item
from django import template
from datetime import date, timedelta
import json
from datetime import datetime
from django.utils.safestring import mark_safe
from django.core import serializers
from monthdelta import monthdelta

from subscriptions.models import (
    Subscription, StockSubscription
)
from stocks.models import Stock
from favourites.models import Favourite
from cart.cart import Cart
import requests

register = template.Library()
import configparser
from django.conf import settings
import os
from django.utils.timezone import localdate

config = configparser.ConfigParser()
config.read(os.path.join(settings.BASE_DIR, 'config.txt'))

def custom_datetime_convert(o):
    if isinstance(o, datetime.date):
        return "{}-{}-{}".format(o.day, o.month, o.year)


@register.simple_tag(takes_context=True)
def get_stock_subscription_plan(context, stock_id):
    request_obj = context['request']
    if not request_obj.user.is_authenticated:
        return False
    stock_subs = StockSubscription.objects.filter(stock_id=stock_id, removed=False, status=True, valid_until__gte=datetime.now()).first()
    if not stock_subs:
        return False
    return True


@register.filter
def to_json(value):
    raw_data = serializers.serialize('python', list(value),
                                     fields=('prediction_date', 'high', 'low', 'close', 'accuracy_prev_day'))
    raw_data_json = [d['fields'] for d in raw_data]
    return json.dumps(raw_data_json, default=custom_datetime_convert)


# return serializers.serialize('json', list(value), fields=('prediction_date'))

@register.simple_tag
def get_item(dictionary, key):
    return dictionary.get(key)


# request_obj = context['request']
# quote = request_obj.realtime_quotes
# return quote
# return serializers.serialize('json', list(value), fields=('prediction_date'))

@register.simple_tag(takes_context=True)
def get_stock_subscription_status(context, stock_id):
    request_obj = context['request']
    if not request_obj.user.is_authenticated:
        return False
    stock_subs = StockSubscription.objects.filter(stock_id=stock_id, removed=False, status=True,
                                                  valid_until__gte=datetime.now()).first()
    if not stock_subs:
        return False
    # subs_obj = Subscription.objects.filter(user=request_obj.user, stock_subscription_id=stock_subs.id,
    #                                        subscription_ends__gte=localdate()).first()
    subs_obj = Subscription.objects.filter(user=request_obj.user, stock_id=stock_id,
                                           subscription_ends__gt=datetime.now(), status=True).first()
    return subs_obj.status if subs_obj != None else False


@register.simple_tag(takes_context=True)
def get_plans_of_stock(context, stock_id):
    now = datetime.now()
    plans = StockSubscription.objects.filter(stock_id=stock_id, removed=False, status=True, valid_until__gte=now.isoformat())
    return plans


@register.simple_tag(takes_context=True)
def get_stock_fav_status(context, stock_id):
    request_obj = context['request']
    if not request_obj.user.is_authenticated:
        return False
    fav_obj = Favourite.objects.filter(user=request_obj.user, stock_id=stock_id).first()
    return fav_obj.status if fav_obj != None else False


@register.simple_tag(takes_context=True)
def check_if_stock_in_cart(context, stock_id):
    request_obj = context['request']
    cart = Cart(request_obj)
    # in_cart = False
    # for item in cart:
    #     if item.product and item.product.stock_id == stock_id:
    #         in_cart = True
    #         break
    # return in_cart

    if StockSubscription.objects.filter(stock_id=stock_id, removed=False,status=True).exists():
        product = StockSubscription.objects.filter(stock_id=stock_id, removed=False, status=True)[0]
        today = datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

        # begin calculating the days of product_max_purchasable
        end_date = datetime.strptime(
            datetime.strftime(datetime.now() + monthdelta(int(product.max_months_purchasable)), '%Y-%m-%d %H:%M:%S'),
            '%Y-%m-%d %H:%M:%S')
        delta = end_date - today
        product_max_purchasable_days = delta.days

        # end

        # Number of Months Purchasable of stock symbol
        # cart = Cart(request)

        purchased_days = 0

        # # calculating the purchased months
        if Subscription.objects.filter(stock_id=stock_id, status=True).exists():
            for ele in Subscription.objects.filter(stock_id=stock_id, status=True, subscription_ends__gt=datetime.now()):

                # start_date is more than today
                if datetime.strftime(ele.subscription_started, '%Y-%m-%d %H:%M:%S') >= datetime.strftime(datetime.now(),
                                                                                                         '%Y-%m-%d %H:%M:%S'):
                    start_date = datetime.strptime(
                        datetime.strftime(ele.subscription_started, '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    end_date = datetime.strptime(
                        datetime.strftime(ele.subscription_ends, '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    purchased_days += (end_date - start_date).days
                else:
                    end_date = datetime.strptime(
                        datetime.strftime(ele.subscription_ends, '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    delta = end_date - today
                    purchased_days += delta.days

        # if cart is not empty and some plan are already added to cart
        if Item.objects.filter(cart_id=cart.cart.id).exists():
            cart_items = Item.objects.filter(cart_id=cart.cart.id)

            # variable for summarizing
            plan_durations = 0
            for cart_item in cart_items:

                # summarizing plan_duration and comparing with NMP
                if StockSubscription.objects.filter(stock_id=stock_id, id=cart_item.object_id).exists():
                    temp = StockSubscription.objects.get(stock_id=stock_id, id=cart_item.object_id)
                    plan_durations += int(temp.plan_duration) * int(cart_item.quantity)

            # begin calculating the days of plan_durations
            end_date = datetime.strptime(
                datetime.strftime(datetime.now() + monthdelta(int(plan_durations)), '%Y-%m-%d %H:%M:%S'),
                '%Y-%m-%d %H:%M:%S')
            delta = end_date - today
            plan_durations_days = delta.days
            # end

            if (int(plan_durations_days) + int(purchased_days)) <= int(
                    product_max_purchasable_days):
                return False
            else:
                return True
        # if cart is empty
        else:
            if int(purchased_days) <= int(product_max_purchasable_days):
                return False
            else:
                return True
    else:
        return True


@register.simple_tag(takes_context=True)
def total_item_in_cart(context):
    request_obj = context['request']
    cart = Cart(request_obj)
    return cart.count()


@register.simple_tag(takes_context=True)
def check_if_subscribed_stock_hidden_by_user(context, stock_id):
    request_obj = context['request']
    if not request_obj.user.is_authenticated:
        return False
    # hidden = Subscription.objects.filter(user=request_obj.user, is_hidden=True).values_list('stock_subscription_id',
    #                                                                                         'stock_subscription__stock_id').count()
    hidden = Subscription.objects.filter(user=request_obj.user, is_hidden=True).values_list('stock_id',
                                                                                            'stock_subscription__stock_id').count()
    if hidden > 0:
        return True
    return False

@register.simple_tag(takes_context=True)
def get_subs_obj_by_transaction(context, transaction_id):
    subs_obj = Subscription.objects.filter(transaction_id=transaction_id, user=context.request.user)
    if subs_obj == None:
        return False
    return subs_obj

@register.simple_tag(takes_context=True)
def get_stock_obj_by_subscription(context, stock_subs_id):
    stock_obj = Stock.objects.get(pk=stock_subs_id)
    if stock_obj == None:
        return False
    return stock_obj


@register.simple_tag(takes_context=True)
def get_stock_obj_by_stock_subscription(context, stock_subs_id):
    stock_obj = StockSubscription.objects.get(pk=stock_subs_id)
    if stock_obj == None:
        return False
    return Stock.objects.select_related().get(pk=stock_obj.stock_id)

@register.simple_tag(takes_context=False)
def get_no_prediction_text():
    return config['HOMEPAGE']['NO_PREDICTION_TEXT']

"""
converting True/False to Yes/No
"""


@register.filter(name='change_yes_no')
def change_yes_no(false_or_yes):
    if not false_or_yes:
        return "No"
    else:
        return "Yes"
