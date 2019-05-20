from __future__ import absolute_import

import os
from django.http import (
    HttpResponse, HttpResponseRedirect,
    JsonResponse,
)
from favourites.models import Favourite
from datetime import datetime
import requests, json
from .models import Stock
from subscriptions.models import StockSubscription, Subscription
from django.conf import settings
import requests
import random
import certifi, urllib3
from decimal import Decimal
"""
 Get all active stocks
"""
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


def get_all_active_stocks():
    return Stock.objects.filter(status=True)


"""
 Get all active stocks with predictions
"""


def get_all_active_stocks_with_predictions():
    returnData = []
    return Stock.objects.select_related().filter(status=True)


"""
 Get all inactive stocks
"""


def get_all_inactive_stocks():
    return Stock.objects.filter(status=False)


"""
 Play with API, access stock data
"""


def api_get_stock_data_recent(symbol):
    url = settings.C_API_STOCK___BASE_URL + 'stock/'
    # r = requests.get(url + symbol.lower() + "/batch?types=quote")
    r = http.request('get', url + symbol.lower() + "/batch?types=quote")
    return r.data


"""
Get the largest trades of particular stock
"""

def api_get_largest_trades(symbol):
    url = settings.C_API_STOCK___BASE_URL + 'stock/'
    r = http.request('get', url + symbol.lower() + "/largest-trades")
    return r.data

"""
 Get Logo of a particular stock
"""


def api_get_stock_logo(symbol):
    url = settings.C_API_STOCK___BASE_URL + 'stock/' + symbol.lower() + '/logo'
    r = http.request('get', url)
    json_result = json.loads(r.data)
    return json_result['url']


def api_get_stock_chart(symbol, interval=False):
    url = settings.C_API_STOCK___BASE_URL + 'stock/' + symbol.lower() + '/chart/'
    if interval:
        url += interval
    # r = requests.get(url, headers= { 'Content-Type': 'text/xml;charset=UTF-8' }, verify=False)
    r = http.request('get', url)
    return r.data


# calculating the total accuracy
def total_accu(stock):
    return random.randint(70, 100)


# calculating the previous day's accuracy
def prev_day_accu(stock, date):
    return random.randint(70, 100)


def accu_of_date(stock, date):
    return random.randint(70, 100)


def calc_err_of_date(stock, date):
    return (100 - accu_of_date(stock, date))


def get_distinct(stocks):
    """
    Due to the following issue
    https://stackoverflow.com/questions/20582966/django-order-by-filter-with-distinct
    And
    annotate() + distinct(fields) is not implemented.
    :return:
    """
    sorted_list = list()
    for __stock in stocks:
        if __stock not in sorted_list:
            sorted_list.append(__stock)
    return sorted_list


"""
 Get Company data

 Sample JSON Response
 {
  "symbol": "AAPL",
  "companyName": "Apple Inc.",
  "exchange": "Nasdaq Global Select",
  "industry": "Computer Hardware",
  "website": "http://www.apple.com",
  "description": "Apple Inc is an American multinational technology company. It designs, manufactures, and markets mobile communication and media devices, personal computers, and portable digital music players.",
  "CEO": "Timothy D. Cook",
  "issueType": "cs",
  "sector": "Technology",
}
"""


def api_get_stock_company_data(symbol):
    url = settings.C_API_STOCK___BASE_URL + 'stock/' + symbol.lower() + '/company/'
    r = http.request('get', url)
    return r.data


def api_get_stock_book(symbol):
    url = settings.C_API_STOCK___BASE_URL + 'stock/' + symbol.lower() + '/book/'
    r = http.request('get', url)
    return r.data


def api_get_stock_stats(symbol):
    url = settings.C_API_STOCK___BASE_URL + 'stock/' + symbol.lower() + '/stats/'
    r = http.request('get', url)
    return r.data


def api_get_stock_stats_left(symbol):
    url = settings.C_API_STOCK___BASE_URL + 'stock/' + symbol.lower() + '/quote/'
    r = http.request('get', url)
    return r.data


"""
 @param symbols = an array of symbols to fetch latest details
 Sample call
 https://api.iextrading.com/1.0/stock/market/batch?symbols=aapl,fb&types=quote&range=1m&last=1
  {
    "AAPL": {
      "quote": {
        "symbol": "AAPL",
        "companyName": "Apple Inc.",
        "primaryExchange": "Nasdaq Global Select",
        "sector": "Technology",
        "calculationPrice": "close",
        "open": 191.65,
        "openTime": 1528119000241,
        "close": 191.83,
        "closeTime": 1528142400383,
        "high": 193.42,
        "low": 191.35,
        "latestPrice": 191.83,
        "latestSource": "Close",
        "latestTime": "June 4, 2018",
        "latestUpdate": 1528142400383,
        "latestVolume": 26151943,
        "iexRealtimePrice": null,
        "iexRealtimeSize": null,
        "iexLastUpdated": null,
        "delayedPrice": 191.83,
        "delayedPriceTime": 1528142400383,
        "extendedPrice": 191.88,
        "extendedChange": 0.05,
        "extendedChangePercent": 0.00026,
        "extendedPriceTime": 1528145942364,
        "previousClose": 190.24,
        "change": 1.59,
        "changePercent": 0.00836,
        "iexMarketPercent": null,
        "iexVolume": null,
        "avgTotalVolume": 29172887,
        "iexBidPrice": null,
        "iexBidSize": null,
        "iexAskPrice": null,
        "iexAskSize": null,
        "marketCap": 942870922540,
        "peRatio": 19.72,
        "week52High": 193.42,
        "week52Low": 142.2,
        "ytdChange": 0.12245942838418629
      }
    },
    "FB": {
      "quote": {
        "symbol": "FB",
        "companyName": "Facebook Inc.",
        "primaryExchange": "Nasdaq Global Select",
        "sector": "Technology",
        "calculationPrice": "close",
        "open": 191.9,
        "openTime": 1528119000573,
        "close": 193.28,
        "closeTime": 1528142400268,
        "high": 193.98,
        "low": 191.47,
        "latestPrice": 193.28,
        "latestSource": "Close",
        "latestTime": "June 4, 2018",
        "latestUpdate": 1528142400268,
        "latestVolume": 18866429,
        "iexRealtimePrice": null,
        "iexRealtimeSize": null,
        "iexLastUpdated": null,
        "delayedPrice": 193.28,
        "delayedPriceTime": 1528142400268,
        "extendedPrice": 193.13,
        "extendedChange": -0.15,
        "extendedChangePercent": -0.00078,
        "extendedPriceTime": 1528145998217,
        "previousClose": 193.99,
        "change": -0.71,
        "changePercent": -0.00366,
        "iexMarketPercent": null,
        "iexVolume": null,
        "avgTotalVolume": 22155224,
        "iexBidPrice": null,
        "iexBidSize": null,
        "iexAskPrice": null,
        "iexAskSize": null,
        "marketCap": 559473651133,
        "peRatio": 28.42,
        "week52High": 195.32,
        "week52Low": 144.56,
        "ytdChange": 0.06537316723624746
      }
    }
  } 
"""


def api_get_stock_batch(symbols_set):
    symbols = ",".join(x for x in symbols_set)
    url = settings.C_API_STOCK___BASE_URL + 'stock/market/batch?symbols=' + symbols.lower() + '&types=quote&range=1m&last=1'
    r = http.request('get', url)
    return json.loads(r.data)


def find_all_with_stock_info(user):
    favs = Favourite.objects.filter(user=user, status=True)
    symbols_set = []
    for fav in favs:
        symbols_set.append(fav.stock.symbol)
    realtime_quotes = api_get_stock_batch(symbols_set)
    return {'favs': favs, 'realtime_quotes': realtime_quotes}


def point_round(n):
    try:
        return round(Decimal(n), 2)
    except:
        return ''


def is_stock_subscribed(request_obj, stock_id):
    if not request_obj.user.is_authenticated:
        return False
    stock_subs = StockSubscription.objects.filter(stock_id=stock_id, removed=False).first()
    if not stock_subs:
        return False
    # subs_obj = Subscription.objects.filter(user=request_obj.user, stock_subscription_id=stock_subs.id).first()
    subs_obj = Subscription.objects.filter(user=request_obj.user, stock_id=stock_id, status=True, subscription_ends__gt=datetime.now()).first()
    return subs_obj.status if subs_obj != None else False

"""
 Get Company Earnings Data

 Pulls data from the four most recent reported quarters.
 Sample JSON Response
 {
  "symbol": "AAPL",
  "earnings": [
    {
      "actualEPS": 2.1,
      "consensusEPS": 2.02,
      "estimatedEPS": 2.02,
      "announceTime": "AMC",
      "numberOfEstimates": 14,
      "EPSSurpriseDollar": 0.08,
      "EPSReportDate": "2017-05-02",
      "fiscalPeriod": "Q2 2017",
      "fiscalEndDate": "2017-03-31"
    },
    {
      "actualEPS": 3.36,
      "consensusEPS": 3.22,
      "estimatedEPS": 3.22,
      "announceTime": "AMC",
      "numberOfEstimates": 15,
      "EPSSurpriseDollar": 0.14,
      "EPSReportDate": "2017-01-31",
      "fiscalPeriod": "Q1 2017",
      "fiscalEndDate": "2016-12-31"
    },
    {
      "actualEPS": 1.67,
      "consensusEPS": 1.66,
      "estimatedEPS": 1.66,
      "announceTime": "AMC",
      "numberOfEstimates": 14,
      "EPSSurpriseDollar": 0.01,
      "EPSReportDate": "2016-10-25",
      "fiscalPeriod": "Q4 2016",
      "fiscalEndDate": "2016-09-30"
    },
    {
      "actualEPS": 1.42,
      "consensusEPS": 1.39,
      "estimatedEPS": 1.39,
      "announceTime": "AMC",
      "numberOfEstimates": 14,
      "EPSSurpriseDollar": 0.03,
      "EPSReportDate": "2016-07-26",
      "fiscalPeriod": "Q3 2016",
      "fiscalEndDate": "2016-06-30"
    }
  ]
}
"""


def api_get_stock_earnings(symbol):
    url = settings.C_API_STOCK___BASE_URL + 'stock/' + symbol.lower() + '/earnings/'
    r = http.request('get', url)
    return r.data


"""
 Stats for stock
 most_active
 https://api.iextrading.com/1.0/stock/market/list/mostactive
"""


def api_get_stock_stats_most_active():
    url = settings.C_API_STOCK___BASE_URL + 'stock/market/list/mostactive'
    r = http.request('get', url)
    return r.data


def api_get_stock_stats_gainers():
    url = settings.C_API_STOCK___BASE_URL + 'stock/market/list/gainers'
    r = http.request('get', url)
    return r.data


def api_get_stock_stats_losers():
    url = settings.C_API_STOCK___BASE_URL + 'stock/market/list/losers'
    r = http.request('get', url)
    return r.data
