from monthdelta import monthdelta
from dateutil import relativedelta
from django.shortcuts import render
from django.http import (
    HttpResponse, HttpResponseRedirect
)
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import Stock, StockPrediction
from .helpers import (
    get_all_active_stocks, get_all_active_stocks_with_predictions, get_distinct,
    api_get_largest_trades,
    api_get_stock_data_recent, api_get_stock_chart, api_get_stock_stats_left,
    api_get_stock_logo, api_get_stock_company_data, api_get_stock_book, api_get_stock_stats,
    api_get_stock_earnings, api_get_stock_stats_most_active, point_round, is_stock_subscribed,
    api_get_stock_stats_losers, api_get_stock_stats_gainers, total_accu, prev_day_accu, calc_err_of_date
)
from decimal import Decimal
from django.db.models import Avg
from django.template import RequestContext
from django.template.loader import render_to_string
import simplejson
import json
import requests
from favourites.models import Favourite
from django.contrib.auth.decorators import login_required
import csv
import time
from cart.cart import Cart
from cart.models import Item
from subscriptions.models import (
    Subscription, StockSubscription
)
from django.core import serializers
from mainsite.custom_decorators import (
    anonymous_required,
    user_login_required
)
from django.conf import settings
from datetime import datetime
from django.utils.timezone import localdate
import random
import certifi, urllib3
import configparser
import os
from payment.models import (
    UserBillingAddress, Transaction
)

config = configparser.ConfigParser()
config.read(os.path.join(settings.BASE_DIR, 'config.txt'))

"""
 Get all active stocks
"""
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


# @method_decorator(user_login_required, name='dispatch')
class StockView(TemplateView):
    template_name = 'stocks/index.html'

    def get_context_data(self, **kwargs):
        context = super(StockView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        stocks = get_all_active_stocks_with_predictions()

        paginator = Paginator(stocks, 25)  # Show 25 contacts per page
        page = self.request.GET.get('page')
        try:
            stocks = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            stocks = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            stocks = paginator.page(paginator.num_pages)
        # Get the index of the current page
        index = stocks.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # Get our new page range. In the latest versions of Django page_range returns
        # an iterator. Thus pass it to list, to make our slice possible again.
        context['page_range'] = list(paginator.page_range)[start_index:end_index]
        context['stocks'] = stocks
        return context


# @method_decorator(user_login_required, name='dispatch')
class SingleView(TemplateView):
    template_name = 'stocks/single.html'

    def get_context_data(self, **kwargs):
        context = super(SingleView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


def ajax_stock_prediction(request):
    if request.is_ajax():
        data = {}
        symbol = request.GET.get('symbol')
        date = request.GET.get('date')

        stock = Stock.objects.filter(symbol=symbol.upper()).first()
        if StockPrediction.objects.filter(stock_id=stock.id, prediction_date=date).exists():
            temp = StockPrediction.objects.get(stock_id=stock.id, prediction_date=date)
            data['stock_prediction'] = {
                'high': temp.high,
                'low': temp.low,
                'close': temp.close,
                "accuracy_prev_day": temp.accuracy_prev_day,
                "prediction_date": temp.prediction_date
            }
        else:
            data['stock_prediction'] = None
        # total accuracy
        data['total_accuracy'] = total_accu(symbol)
        data['high_color'] = settings.HIGH_COLOR
        data['low_color'] = settings.LOW_COLOR
        data['close_color'] = settings.CLOSE_COLOR
        # previous day's accuracy
        # data['previous_day_accuracy'] = prev_day_accu(symbol, date)
        return JsonResponse({'symbol': symbol, 'data': data})


def ajax_stock_single(request):
    if request.is_ajax():
        data = {}
        symbol = request.GET.get('symbol')

        data['stats'] = json.loads(api_get_stock_stats(symbol))
        data['stats_left'] = json.loads(api_get_stock_stats_left(symbol))
        # print('symbol', symbol, "data", data['stats_left'])
        return JsonResponse({'symbol': symbol, 'data': data})


def stock_single(request, symbol):
    data = {}
    data['stock'] = Stock.objects.filter(symbol=symbol.upper()).first()
    current_date = time.strftime("%Y-%m-%d")
    if StockPrediction.objects.filter(stock_id=data['stock'].id, prediction_date=current_date).exists():
        data['stock_prediction'] = StockPrediction.objects.get(stock_id=data['stock'].id, prediction_date=current_date)
    else:
        data['stock_prediction'] = []
    # data['stock_today_dict'] = json.loads(api_get_stock_chart(symbol, ''))
    # data['stock_today'] = api_get_stock_chart(symbol, '')
    # data['book'] =  json.loads(api_get_stock_book(symbol))
    # data['low_color'] = "#ff0000"
    # data['high_color'] = "#ff0000"
    # data['close_color'] = "#ff0000"
    # data['accuracy_color'] = "#ff0000"
    # data['earnings'] = json.loads(api_get_stock_earnings(symbol))
    # data['stock_1d_dict'] = json.loads(api_get_stock_chart(symbol, '1d'))
    # data['stock_1d'] = api_get_stock_chart(symbol, '1d')
    # data['stock_5y_dict'] = json.loads(api_get_stock_chart(symbol, '5y'))
    # data['stock_5y'] = api_get_stock_chart(symbol, '5y')
    # data['previous_day_accuracy'] = prev_day_accu(symbol, current_date)
    # ----------------------------------------------------------------------------

    data['company'] = json.loads(api_get_stock_company_data(symbol))
    # data['stats_most_active'] = json.loads(api_get_stock_stats_most_active())
    # data['stats_losers'] = json.loads(api_get_stock_stats_losers())
    # data['stats_gainers'] = json.loads(api_get_stock_stats_gainers())
    data['stats'] = json.loads(api_get_stock_stats(symbol))
    data['stats_left'] = json.loads(api_get_stock_stats_left(symbol))
    data['stock_logo'] = api_get_stock_logo(symbol)
    data['total_accuracy'] = total_accu(symbol)
    data['low_color'] = settings.LOW_COLOR
    data['high_color'] = settings.HIGH_COLOR
    data['close_color'] = settings.CLOSE_COLOR
    data['accuracy_color'] = settings.ACCURACY_COLOR
    data['largest_trades'] = json.loads(api_get_largest_trades(symbol))

    return render(request, 'stocks/single_test.html', data)


# @method_decorator(user_login_required, name='dispatch')
def stock_stats(request):
    rq_type = request.GET.get('type')
    symbol = request.GET.get('symbol')
    data = {}

    if rq_type == 'stock_realtime':
        data['stock_realtime'] = json.loads(api_get_stock_data_recent(symbol))

    if rq_type == 'company':
        data['company'] = json.loads(api_get_stock_company_data(symbol))

    if rq_type == 'earnings':
        data['earnings'] = json.loads(api_get_stock_earnings(symbol))

    if rq_type == 'stock_1d_dict':
        data['stock_1d_dict'] = json.loads(api_get_stock_chart(symbol, '1d'))

    if rq_type == 'stock_1d':
        data['stock_1d'] = json.loads(api_get_stock_chart(symbol, '1d'))

    if rq_type == 'stats_most_active':
        data['stats_most_active'] = json.loads(api_get_stock_stats_most_active())

    if rq_type == 'stats_losers':
        data['stats_losers'] = json.loads(api_get_stock_stats_losers())

    if rq_type == 'stats_gainers':
        data['stats_gainers'] = json.loads(api_get_stock_stats_gainers())

    if rq_type == 'stock_5y_dict':

        # calculating the accuracy of every stock history value
        temp = json.loads(api_get_stock_chart(symbol, '5y'))
        for element in temp:
            accuracy = calc_err_of_date(symbol, element["date"])
            if StockPrediction.objects.filter(stock=Stock.objects.get(symbol=symbol), prediction_date=element["date"]).exists():
                tt = StockPrediction.objects.get(stock=Stock.objects.get(symbol=symbol),
                                               prediction_date=element["date"])
                element["accuracy"] = tt.accuracy_prev_day
            else:
                element["accuracy"] = 0
        data['stock_5y_dict'] = temp

    if rq_type == 'stock_5y':
        data['stock_5y'] = api_get_stock_chart(symbol, '5y')

    if rq_type == 'stock_logo':
        data['stock_logo'] = api_get_stock_logo(symbol)

    return JsonResponse({'type': rq_type, 'symbol': symbol, 'data': data})


# @method_decorator(user_login_required, name='dispatch')
def search(request):
    data = {}
    q = request.GET.get('query', '')
    stocks = Stock.objects.filter(Q(name__icontains=q) | Q(symbol__icontains=q))[:20]
    results = []
    for stock in stocks:
        stock_json = {}
        stock_json['id'] = stock.id
        stock_json['symbol'] = stock.symbol
        stock_json['name'] = stock.name
        results.append(stock_json)
    return JsonResponse({'content': results})


# @method_decorator(user_login_required, name='dispatch')
def load_db(request):
    with open('mainsite/static/companylist.csv') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)
        stock_objects = list()
        for row in reader:
            if not Stock.objects.filter(symbol=row[0]).exists():
                stock_objects.append(Stock(symbol=row[0], name=row[1], last_sale=row[2], market_cap=row[3],
                                           adr_tso=row[4], ipo_year=row[5], sector=row[6], industry=row[7]))
        Stock.objects.bulk_create(stock_objects)
    return HttpResponse('Import successful')


# @method_decorator(user_login_required, name='dispatch')
def get_list(request):
    page = request.POST.get('page')
    data = {}
    stocks = get_all_active_stocks_with_predictions()
    paginator = Paginator(stocks, 25)  # Show 25 contacts per page
    page = request.POST.get('page')
    try:
        stocks = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        stocks = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        stocks = paginator.page(paginator.num_pages)
    # Get the index of the current page
    index = stocks.number - 1  # edited to something easier without index
    # This value is maximum index of your pages, so the last page - 1
    max_index = len(paginator.page_range)
    # You want a range of 7, so lets calculate where to slice the list
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    # Get our new page range. In the latest versions of Django page_range returns
    # an iterator. Thus pass it to list, to make our slice possible again.
    # context['page_range'] = list(paginator.page_range)[start_index:end_index]
    # context['stocks'] = stocks
    html_data = {}
    html_data['html'] = render_to_string('stocks/snippets/ajax-stock-list.html', {'stocks': stocks}, request)
    return JsonResponse(html_data)


# @method_decorator(user_login_required, name='dispatch')
def test(request):
    # c_data = json.loads(api_get_stock_data_recent('PIH'))
    # c_data = api_get_stock_company_data('PIH')
    # return JsonResponse({'data': c_data['quote']})
    stocks = get_all_active_stocks_with_predictions()
    for stock in stocks:
        stock_data = stocks.stockpredictions.all()
    # c_data = json.loads(api_get_stock_data_recent('PIH'))
    return JsonResponse({'data': stocks})


# @method_decorator(user_login_required, name='dispatch')
def add_to_cart(request):
    id = request.POST.get('id')
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    duration = request.POST.get('plan_duration')
    data = {}
    stock = Stock.objects.get(id=product_id)
    if StockSubscription.objects.filter(id=id, stock_id=product_id, plan_duration=duration, removed=False,
                                        status=True).exists():
        product = StockSubscription.objects.get(id=id, stock_id=product_id, plan_duration=duration, removed=False,
                                                status=True)

        # begin calculating the days of product
        today = datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(datetime.strftime(datetime.now() + monthdelta(3), '%Y-%m-%d %H:%M:%S'),
                                     '%Y-%m-%d %H:%M:%S')
        delta = end_date - today
        product_days = delta.days
        # end

        # begin calculating the days of product_max_purchasable
        end_date = datetime.strptime(
            datetime.strftime(datetime.now() + monthdelta(int(product.max_months_purchasable)), '%Y-%m-%d %H:%M:%S'),
            '%Y-%m-%d %H:%M:%S')
        delta = end_date - today
        product_max_purchasable_days = delta.days

        # end

        # Number of Months Purchasable of stock symbol
        cart = Cart(request)

        purchased_days = 0
        purchased_months = 0

        # # calculating the purchased months
        if Subscription.objects.filter(stock_id=product_id, status=True).exists():
            for ele in Subscription.objects.filter(stock_id=product_id, status=True, subscription_ends__gt=datetime.now()):

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
                if StockSubscription.objects.filter(stock_id=product_id, id=cart_item.object_id).exists():
                    temp = StockSubscription.objects.get(stock_id=product_id, id=cart_item.object_id)
                    plan_durations += int(temp.plan_duration) * int(cart_item.quantity)

            # begin calculating the days of plan_durations
            end_date = datetime.strptime(
                datetime.strftime(datetime.now() + monthdelta(int(plan_durations)), '%Y-%m-%d %H:%M:%S'),
                '%Y-%m-%d %H:%M:%S')
            delta = end_date - today
            plan_durations_days = delta.days
            # end

            if (int(plan_durations_days) + int(product_days) + int(purchased_days)) <= int(
                    product_max_purchasable_days):
                cart.add(product, product.price, quantity)
                data['status'] = "1"
                data['message'] = "Product added to cart"
            else:
                data['status'] = "0"
                data['message'] = "Sorry, you can not purchase subscriptions longer than " + str(
                    product.max_months_purchasable) + " months for " + stock.symbol
        # if cart is empty
        else:
            if (int(product_days) + int(purchased_days)) <= int(product_max_purchasable_days):
                cart.add(product, product.price, quantity)
                data['status'] = "1"
                data['message'] = "Product added to cart"
            else:
                data['status'] = "0"
                data['message'] = "Sorry, you can not purchase subscriptions longer than " + str(
                    product.max_months_purchasable) + " months for " + stock.symbol
    else:
        data['status'] = "0"
        data['message'] = "This plan not available"
    return JsonResponse(data)


# @method_decorator(user_login_required, name='dispatch')
def remove_from_cart(request, product_id):
    product = StockSubscription.objects.get(id=product_id)
    cart = Cart(request)
    cart.remove(product)


# @method_decorator(user_login_required, name='dispatch')
def get_cart(request):
    cart_data = []
    cart = Cart(request)
    for item in cart:
        cart_data.append(
            {'plan_duration': item.product.plan_duration, 'quantity': item.quantity, 'price': item.total_price})
    return JsonResponse({"cart": cart_data})


# @method_decorator(user_login_required, name='dispatch')
def is_product_in_cart(request, product_id):
    cart = Cart(request)
    for item in cart:
        cart.append({'plan_duration': item.product.plan_duration, 'quantity': item.quantity, 'price': item.total_price})
    return JsonResponse({"cart": cart})


# @method_decorator(user_login_required, name='dispatch')
def clear_cart(request):
    data = {}
    cart = Cart(request)
    if cart.clear():
        data['message'] = "Cleared cart content"
    return JsonResponse(data)


"""
Helper methods
"""


# @method_decorator(user_login_required, name='dispatch')
def check_if_stock_in_cart(rq, stock_id):
    cart = Cart(rq)
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


# @method_decorator(user_login_required, name='dispatch')
def get_stock_subscription_status(rq, stock_id):
    stock_subs = StockSubscription.objects.filter(stock_id=stock_id, removed=False).first()
    if not stock_subs:
        return False
    # subs_obj = Subscription.objects.filter(user=rq.user, stock_subscription_id=stock_subs.id).first()
    subs_obj = Subscription.objects.filter(user=rq.user, stock_id=stock_id).first()
    return subs_obj.status if subs_obj != None else False


# @method_decorator(user_login_required, name='dispatch')
def get_stock_fav_status(rq, stock_id):
    fav_obj = Favourite.objects.filter(user=rq.user, stock_id=stock_id).first()
    return fav_obj.status if fav_obj != None else False


# @method_decorator(user_login_required, name='dispatch')
def check_if_subscribed_stock_hidden_by_user(rq, stock_id):
    # hidden = Subscription.objects.filter(user=rq.user, is_hidden=True).values_list('stock_subscription_id',
    #                                                                                'stock_subscription__stock_id').count()
    hidden = Subscription.objects.filter(user=rq.user, is_hidden=True).values_list('stock_id',
                                                                                   'stock_subscription__stock_id').count()
    if hidden > 0:
        return True
    return False


# @method_decorator(user_login_required, name='dispatch')
def convert_to_json(queryset):
    # lmodel = ValuesQuerySetToDict(queryset)
    response = simplejson.dumps(queryset)
    return response


# @method_decorator(user_login_required, name='dispatch')
def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]


def get_pagination(request, stocks, page=None):
    if not page:
        page = request.POST.get('page')
    # print('page', page)

    paginator = Paginator(stocks, int(config['STOCK']['CARDS_PER_PAGE']))  # Show 25 contacts per page
    num_pages = paginator.num_pages
    try:
        new_stocks = paginator.page(page)
        # print("stocks", len(new_stocks))
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        # print("PageNotAnInteger")
        new_stocks = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        # print("EmptyPage")
        # stocks = paginator.page(paginator.num_pages)
        new_stocks = []

    return new_stocks, num_pages


def __get_all_stocks_with_prediction():
    return Stock.objects.filter(stockprediction__status=True, stocksubscription__removed=False,
                                stocksubscription__valid_until__gte=datetime.now()) \
        .filter(stocksubscription__removed=False, stocksubscription__status=True).distinct().order_by('pk')


# @method_decorator(user_login_required, name='dispatch')
def view_all_stocks_with_predictions(request):
    stocks = __get_all_stocks_with_prediction()
    paged_stocks, num_pages = get_pagination(request, stocks, page=1)
    return render(request, 'stocks/all_stocks.html',
                  {'sort_required': True, 'search_required': True,
                   'page_name': 'all_stocks_with_prediction', 'predictions_active_li': 'm-menu__item--active',
                   'all_stocks': paged_stocks, 'num_pages': num_pages})


def __get_new_sub_available_with_predictions():
    stocks = Stock.objects.filter(stockprediction__status=True, stocksubscription__status=True,
                                  stocksubscription__removed=False,
                                  stocksubscription__valid_until__gte=datetime.now()).order_by(
        '-stocksubscription__created_at').distinct()
    return get_distinct(stocks)


# @method_decorator(user_login_required, name='dispatch')
def new_sub_available_with_predictions(request):
    stocks = __get_new_sub_available_with_predictions()
    paged_stocks, num_pages = get_pagination(request, stocks, page=1)
    return render(request, 'stocks/all_stocks.html',
                  {'page_name': 'new_subscription_available', 'predictions_active_li': 'm-menu__item--active',
                   'all_stocks': paged_stocks, 'num_pages': num_pages})


def __get_highest_accuracy_stocks():
    stocks = Stock.objects.filter(stockprediction__status=True,
                                  stocksubscription__removed=False,
                                  stocksubscription__valid_until__gte=datetime.now()).filter(
        stocksubscription__removed=False, stocksubscription__status=True).distinct().order_by('pk')
    average_stocks = stocks.annotate(avg_rating=Avg('stockprediction__accuracy_prev_day')).filter(
        avg_rating__gt=float(config['STOCK']['MIN_VALUE_FOR_ACCURACY'])).order_by('-avg_rating')
    # stocks = sorted(average_stocks, key=lambda t: t.get_all_time_avg, reverse=True)
    return get_distinct(average_stocks)[:int(config['STOCK']['MAX_NO_OF_HIGHEST_ACC_STOCKS'])]


def highest_accuracy_stocks(request):
    stocks = __get_highest_accuracy_stocks()
    paged_stocks, num_pages = get_pagination(request, stocks, page=1)
    return render(request, 'stocks/all_stocks.html',
                  {'all_stocks': paged_stocks, 'predictions_active_li': 'm-menu__item--active',
                   'num_pages': num_pages, 'page_name': 'highest_accuracy_stocks'})


def view_all_stocks(request):
    stocks = Stock.objects.filter(status=True).order_by('pk').distinct('pk')
    paged_stocks, num_pages = get_pagination(request, stocks, page=1)
    return render(request, 'stocks/all_stocks.html',
                  {'search_required': True, 'page_name': 'view_all_stocks', 'sub_nav': True,
                   'all_stocks_active_li': 'm-menu__item--active',
                   'all_stocks': paged_stocks, 'num_pages': num_pages})


def __get_api_data(data_type):
    url = settings.C_API_STOCK___BASE_URL + '/stock/market/list/{}'.format(data_type)
    r = http.request('get', url)
    return json.loads(r.data)


def __get_stock_data_for_gla(request, realtime_quote):
    stock = Stock.objects.filter(symbol=realtime_quote.get("symbol")).first()
    data_dict = {

        "stock_symbol": realtime_quote.get("symbol"),

        "stock_price": realtime_quote.get("latestPrice"),
        "change": point_round(realtime_quote.get("changePercent") * 100),
        "changePercent": point_round(realtime_quote.get("changePercent")),
        "volume": realtime_quote.get("latestVolume"),
        "days_range": "{} - {}".format(point_round(realtime_quote.get("low")),
                                       point_round(realtime_quote.get("high"))),
        "week_52": "{} - {}".format(point_round(realtime_quote.get("week52Low")),
                                    point_round(realtime_quote.get("week52High"))),
        "market_cap": str(round(Decimal(realtime_quote.get("marketCap") / 1000000000), 3)) + "B",
        "stock_open": realtime_quote.get("open")
    }
    if stock:
        stock_dict = {
            "stock_id": stock.id,
            "avg_acc_all_time": stock.get_all_time_avg,
            "acc_prev_day": stock.get_prev_day_prediction,
            "stock_name": stock.name
        }
    else:
        stock_dict = {
            "stock_id": '',
            "avg_acc_all_time": '',
            "acc_prev_day": '',
            "stock_name": realtime_quote.get("companyName")
        }
    data_dict.update(stock_dict)
    data_dict["id"] = ''
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(stock=stock, user=request.user).first()
        if fav:
            data_dict["id"] = fav.id

    if stock and is_stock_subscribed(request_obj=request, stock_id=stock.id):
        data_dict["stock_close"] = realtime_quote.get("close", "")
        data_dict["stock_low"] = realtime_quote.get("low", ""),
        data_dict["stock_high"] = realtime_quote.get("high", "")
        data_dict["action"] = ''
    else:
        data_dict["stock_close"] = ''
        data_dict["stock_low"] = ''
        data_dict["stock_high"] = ''
        data_dict["action"] = 'subscribe'

    return data_dict


def gainer_looser_most_active(request):
    headers = ['Symbol', 'Name', 'Price', 'Change', 'Change %', 'Volume', 'Days Range', '52 week range',
               'Market Cap.', 'Avg accuracy', "Previous accuracy", 'Forecasted Low',
               'Forecasted High', 'Forecasted Close', 'id', 'Stock ID', 'Action']
    header_attributes = ['stock_symbol', 'stock_name', 'stock_price', 'change', 'changePercent', 'volume',
                         'days_range',
                         'week_52', 'market_cap', 'avg_acc_all_time', 'acc_prev_day', 'stock_low', 'stock_high',
                         'stock_close', 'id', 'stock_id', 'action']
    gainers_stocks = list()
    for realtime_quote in __get_api_data('gainers'):
        __data = __get_stock_data_for_gla(request, realtime_quote)
        if __data:
            gainers_stocks.append(__data)

    losers_stocks = list()
    for realtime_quote in __get_api_data('losers'):
        __data = __get_stock_data_for_gla(request, realtime_quote)
        if __data:
            losers_stocks.append(__data)

    most_active_stocks = list()
    for realtime_quote in __get_api_data('mostactive'):
        __data = __get_stock_data_for_gla(request, realtime_quote)
        if __data:
            most_active_stocks.append(__data)

    return render(request, 'stocks/gainers_losers.html',
                  {'gainers_stocks': gainers_stocks,
                   'page_name': "gainers_losers",
                   'sub_nav': True,
                   'headers': headers,
                   'losers_stocks': losers_stocks,
                   'most_active_stocks': most_active_stocks,
                   'all_stocks_active_li': 'm-menu__item--active',
                   'header_attributes': header_attributes
                   })


def __get_popular_stocks():
    stocks = Stock.objects.filter(favourite__status=True).distinct('pk')
    return sorted(stocks[:int(config['STOCK']['MAXIMUM_POPULAR_CARDS'])], key=lambda t: t.get_favourite_count,
                  reverse=True)


def most_popular(request):
    stocks = __get_popular_stocks()
    paged_stocks, num_pages = get_pagination(request, stocks, page=1)
    # print([(stock.id, stock.get_favourite_count) for stock in stocks])
    return render(request, 'stocks/all_stocks.html',
                  {'all_stocks': paged_stocks, 'sub_nav': True, 'num_pages': num_pages, 'page_name': 'most_popular',
                   'all_stocks_active_li': 'm-menu__item--active'})


def get_stocks_ajax(request):
    page_name = request.POST.get('page_name')
    sort_method = request.POST.get('sort_method')
    search_term = request.POST.get('term')
    if page_name == "all_stocks_with_prediction":
        stocks = __get_all_stocks_with_prediction()
        if search_term:
            stocks = stocks.filter(Q(name__icontains=search_term) | Q(symbol__icontains=search_term)).distinct(
                'pk').order_by('pk')

        if sort_method == "cheapest_per_month":
            stocks = sorted(stocks, key=lambda t: t.get_least_price)
            # print([stock.get_least_price for stock in stocks])

        elif sort_method == "most_expensive_per_month":
            stocks = sorted(stocks, key=lambda t: t.get_highest_price, reverse=True)
            # print([stock.get_highest_price for stock in stocks])

        elif sort_method == "highest_acc_prev_day":
            stocks = sorted(stocks, key=lambda t: t.get_prev_day_prediction, reverse=True)
            # print([stock.get_prev_day_prediction for stock in stocks])

        elif sort_method == "highest_acc_avg_all_time":
            stocks = sorted(stocks, key=lambda t: t.get_all_time_avg, reverse=True)
            # print([stock.get_all_time_avg for stock in stocks])

        elif sort_method == "popularity":
            stocks = stocks.filter(stocksubscription__subscription__subscription_ends__gte=datetime.now())
            stocks = sorted(stocks, key=lambda t: t.get_subscribed_user_count, reverse=True)
            # print([stock.get_subscribed_user_count for stock in stocks])

    elif page_name == "new_subscription_available":
        stocks = __get_new_sub_available_with_predictions()

    elif page_name == "highest_accuracy_stocks":
        stocks = __get_highest_accuracy_stocks()

    elif page_name == "view_all_stocks":
        stocks = Stock.objects.filter(status=True).order_by('-pk').distinct('pk')
        if search_term:
            stocks = stocks.filter(Q(name__icontains=search_term) | Q(symbol__icontains=search_term))

    elif page_name == "most_popular":
        stocks = __get_popular_stocks()
        # print([(stock.id, stock.get_favourite_count) for stock in stocks])
    paged_stocks, num_pages = get_pagination(request, stocks)
    html = list()

    for stock in paged_stocks:
        html.append(render_to_string('stocks/snippets/stock_card.html', {'stock': stock}, request))
    html_data = {'html_content': html}
    return JsonResponse(html_data)
    # if page_name == "all_stocks_with_prediction":
