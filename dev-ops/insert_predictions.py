import sys
import os
import django
import json
__path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(__path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainsite.settings")
django.setup()
import random
from stocks.models import StockPrediction, Stock
from subscriptions.models import StockSubscription
from stocks.helpers import (api_get_stock_chart, calc_err_of_date)
from datetime import timedelta
from django.utils import timezone
import pytz

from decimal import Decimal

def point_round(n):
    try:
        return round(Decimal(n), 2)
    except:
        return ''

predictions = list()
for stock in Stock.objects.all()[:10]:
    symbol = stock.symbol

    # add plans
    plans = list()
    for i in range(3):
        plans.append(StockSubscription(
            plan_duration=point_round(random.uniform(1, 6)),
            stock=stock,
            price=point_round(random.uniform(20, 100)),
            valid_until=timezone.now() + timedelta(weeks=random.uniform(4, 48)),
            max_months_purchasable=point_round(8),
        ))
    StockSubscription.objects.bulk_create(plans)

    temp = json.loads(api_get_stock_chart(symbol, '5y'))
    temp.reverse()
    days = temp[:20]
    for element in days:   # 20 days
        print("Symbol - ", symbol, ", Date - ", element["date"])
        if days.index(element) % 2 == 0:
            pred_close = element["close"] - random.uniform(0, element["close"] / 10)
        else:
            pred_close = element["close"] + random.uniform(0, element["close"] / 10)
        __accuracy = point_round(((abs(element["close"] - pred_close) / element["close"]) * 100))
        _stock = StockPrediction(stock=stock,
                                 prediction_date=element["date"],
                                 high=point_round(element["high"] + 12),
                                 low=point_round(element["low"] - 10),
                                 close=point_round(pred_close),
                                 accuracy_prev_day=__accuracy,
                                 )
        predictions.append(_stock)

StockPrediction.objects.bulk_create(predictions)