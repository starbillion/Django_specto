from dateutil import relativedelta
from django.shortcuts import render
from django.urls import reverse
from django.http import (
    HttpResponse, HttpResponseRedirect
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from stocks.models import Stock
from django.contrib import messages
from .models import (
    Subscription, StockSubscription, SubscriptionOrder
)
from mainsite.custom_decorators import (
    anonymous_required,
    user_login_required
)
from stocks.helpers import (
    find_all_with_stock_info, api_get_stock_batch, point_round, is_stock_subscribed
)
from decimal import Decimal
import json
from datetime import datetime
from django.db.models import Case, When
from payment.models import Transaction
from django.utils.timezone import localdate
def reset_sources(request):
    # sources_set = [
    # 	{
    # 		name: 'new_stock_added',
    # 		display_name: 'New Stock Added',
    # 		description: 'A New Stock has been added',
    # 	},
    # 	{
    # 		name: 'stock_removed',
    # 		display_name: 'Stock Removed',
    # 		description: 'A Stock has been removed',
    # 	},
    # 	{
    # 		name: 'stock_subscription_price_increased',
    # 		display_name: 'Stock subscription price increased',
    # 		description: 'A Stock\'s price has been increased',
    # 	},
    # ]
    # for source in sources_set:
    # 	Source.objects.create(
    # 		name=source.name,
    # 		display_name=source.display_name,
    # 		description=source.description
    # 	)
    return JsonResponse({'result': []})


# @method_decorator(user_login_required, name='dispatch')
def subscribe_stock(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    stock = Stock.objects.get(pk=request.POST.get('stock_id'))
    status = request.POST.get('subscribe_status')
    if int(status) == 1:
        status = False
    else:
        status = True
    stock_subscription, created = Subscription.objects.get_or_create(user=request.user, stock=stock)
    stock_subscription.status = status
    stock_subscription.save()
    return JsonResponse({'status': status, 'message': 'Subscribed successfully'})


def reset_subscription_order(user, order_object):
    id_order_list = [int(__id) for __id in order_object.get_id_list if __id]
    id_list_from_db = user.subscription_set.filter(status=True).values_list('id', flat=True)
    pk_list = [__id for __id in id_order_list if int(__id) in id_list_from_db if __id]
    final_list = pk_list + list(set(id_list_from_db) - set(id_order_list))
    order_object.set_list(final_list)
    order_object.save()
    return final_list


# @method_decorator(user_login_required, name='dispatch')
class HistoryView(TemplateView):
    template_name = 'subscriptions/history.html'

    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        transactions = Transaction.objects.filter(status=True, user=self.request.user)
        result = []
        idx = 1
        for tran in transactions:
            subs = Subscription.objects.filter(transaction_id=tran.id, user=self.request.user)
            for sub in subs:
                stock = Stock.objects.get(pk=sub.stock_id)

                ele = {
                    "id": idx,
                    "transaction_id": tran.transaction_id,
                    "transaction_type": tran.transaction_type,
                    "created_at": tran.created_at,
                    "stock_name": stock.name,
                    "stock_symbol": stock.symbol,
                    "subscription_started": sub.subscription_started,
                    "subscription_ends": sub.subscription_ends,
                    "purchased_months": sub.purchased_months,
                    "total_price": sub.total_price
                }
                result.append(ele)
                idx += 1

        context['hists'] = result
        return context


# @method_decorator(user_login_required, name='dispatch')
class SubscriptionsView(TemplateView):
    template_name = 'subscriptions/subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super(SubscriptionsView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        # context['subscriptions'] = Subscription.objects.filter(user=self.request.user)

        headers = ['Symbol', 'Name', 'Price', 'Change', 'Change %', 'Volume', 'Days Range', '52 week range',
                   'Market Cap.', 'Avg accuracy', "Previous accuracy", 'Forecasted Low',
                   'Forecasted High', 'Forecasted Close', 'Expiry', 'id', 'Stock ID', 'Action']
        header_attributes = ['stock_symbol', 'stock_name', 'stock_price', 'change', 'changePercent', 'volume',
                             'days_range',
                             'week_52', 'market_cap', 'avg_acc_all_time', 'acc_prev_day', 'stock_low', 'stock_high',
                             'stock_close', 'expiry', 'id', 'stock_id', 'action']

        context['headers'] = headers
        context['header_attributes'] = header_attributes
        print(len(header_attributes))
        # Required for filter
        order_object = self.request.user.subscriptionorder_set.first()
        if order_object:
            pk_list = reset_subscription_order(self.request.user, order_object)
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
            object_list = Subscription.objects.filter(pk__in=pk_list, subscription_ends__gt=datetime.now()).order_by(preserved)
        else:
            object_list = Subscription.objects.filter(user=self.request.user, status=True, subscription_ends__gt=datetime.now()).all()
        # Order
        symbols_set = []
        for _sub in object_list:
            # symbols_set.append(_sub.stock_subscription.stock.symbol)
            symbols_set.append(_sub.stock.symbol)
        realtime_quotes = api_get_stock_batch(symbols_set)
        json_data = list()
        for sub_object in object_list:
            # __sub = sub_object.stock_subscription
            # realtime_quote = realtime_quotes.get(__sub.stock.symbol).get("quote")
            realtime_quote = realtime_quotes.get(sub_object.stock.symbol).get("quote")
            data_dict = {
                "id": sub_object.id,
                "status": sub_object.status,
                "stock_id": sub_object.stock.id,
                "stock_symbol": sub_object.stock.symbol,
                "avg_acc_all_time": sub_object.stock.get_all_time_avg,
                "acc_prev_day": sub_object.stock.get_prev_day_prediction,
                "stock_name": sub_object.stock.name,
                "stock_price": realtime_quote.get("latestPrice"),
                "change": point_round(realtime_quote.get("changePercent") * 100),
                "changePercent": point_round(realtime_quote.get("changePercent")),
                "volume": realtime_quote.get("latestVolume"),
                "days_range": "{} - {}".format(point_round(realtime_quote.get("low")),
                                               point_round(realtime_quote.get("high"))),
                "week_52": "{} - {}".format(point_round(realtime_quote.get("week52Low")),
                                            point_round(realtime_quote.get("week52High"))),
                "market_cap": str(round(Decimal(realtime_quote.get("marketCap") / 1000000000), 3)) + "B",
                "stock_status": sub_object.stock.status,
                "stock_open": realtime_quote.get("open")}
            # data_dict = {
            #     "id": sub_object.id,
            #     "status": sub_object.status,
            #     "stock_id": __sub.stock.id,
            #     "stock_symbol": __sub.stock.symbol,
            #     "avg_acc_all_time": __sub.stock.get_all_time_avg,
            #     "acc_prev_day": __sub.stock.get_prev_day_prediction,
            #     "stock_name": __sub.stock.name,
            #     "stock_price": realtime_quote.get("latestPrice"),
            #     "change": point_round(realtime_quote.get("changePercent") * 100),
            #     "changePercent": point_round(realtime_quote.get("changePercent")),
            #     "volume": realtime_quote.get("latestVolume"),
            #     "days_range": "{} - {}".format(point_round(realtime_quote.get("low")),
            #                                    point_round(realtime_quote.get("high"))),
            #     "week_52": "{} - {}".format(point_round(realtime_quote.get("week52Low")),
            #                                 point_round(realtime_quote.get("week52High"))),
            #     "market_cap": str(round(Decimal(realtime_quote.get("marketCap") / 1000000000), 3)) + "B",
            #     "stock_status": __sub.stock.status,
            #     "stock_open": realtime_quote.get("open")}

            data_dict["stock_close"] = realtime_quote.get("close")
            data_dict["stock_low"] = realtime_quote.get("low"),
            data_dict["stock_high"] = realtime_quote.get("high")
            data_dict["action"] = 'subscribe'

            today = datetime.strptime(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            # start_date is more than today
            if datetime.strftime(sub_object.subscription_started, '%Y-%m-%d %H:%M:%S') >= datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'):
                data_dict["expiry"] = sub_object.purchased_months
            else:
                end_date = datetime.strptime(datetime.strftime(sub_object.subscription_ends, '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                if relativedelta.relativedelta(end_date, today).months == 0:
                    if (end_date - today).days == 0:
                        diff = end_date - today

                        days, seconds = diff.days, diff.seconds
                        hours = days * 24 + seconds // 3600
                        data_dict["expiry"] = str(hours) + " Hour"
                    else:
                        data_dict["expiry"] =str((end_date - today).days) + " Day"
                else:
                    data_dict["expiry"] = str(relativedelta.relativedelta(end_date, today).months) + " Month"

            json_data.append(data_dict)

        context['table_data'] = json_data

        return context


def set_table_order(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'}, status=500)
    id_list = request.POST.getlist('id_list[0][]')
    if id_list:
        obj, created = SubscriptionOrder.objects.get_or_create(
            user=request.user
        )
        obj.set_list(id_list)
        obj.save()
    return JsonResponse({'status': 1, 'message': 'Invalid request!'}, status=200)


class SubscriptionsViewNew(TemplateView):
    template_name = 'subscriptions/my_subscriptions.html'

    def get_context_data(self, **kwargs):
        context = super(SubscriptionsViewNew, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['subscriptions'] = Subscription.objects.filter(user=self.request.user)
        return context


# @method_decorator(user_login_required, name='dispatch')
class TestView(TemplateView):
    template_name = 'subscriptions/test.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        return context


# @method_decorator(user_login_required, name='dispatch')
def test(request):
    return HttpResponse("Testing!!")


# @method_decorator(user_login_required, name='dispatch')
def subscribe_remove_all(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    updated = Subscription.objects.filter(user=request.user).delete()
    messages.add_message(request, messages.SUCCESS, 'Cleared alll subscriptions!')
    return HttpResponseRedirect(reverse('my-subscriptions'))


# @method_decorator(user_login_required, name='dispatch')
def subscribe_unsubscribe_all(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    updated = Subscription.objects.filter(user=request.user).update(status=False)
    messages.add_message(request, messages.SUCCESS, 'Unsubscribed successfully!')
    return HttpResponseRedirect(reverse('my-subscriptions'))


# @method_decorator(user_login_required, name='dispatch')
def subscribe_subscribe_all(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    updated = Subscription.objects.filter(user=request.user).update(status=True)
    messages.add_message(request, messages.SUCCESS, 'Subscribed successfully!')
    return HttpResponseRedirect(reverse('my-subscriptions'))


# @method_decorator(user_login_required, name='dispatch')
def subscribe_unsubscribe_selected(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    ids = request.GET.get('ids').split(",")
    updated = Subscription.objects.filter(user=request.user, id__in=ids).update(status=False)
    messages.add_message(request, messages.SUCCESS, 'Un-subscribed successfully!')
    return HttpResponseRedirect(reverse('my-subscriptions'))


# @method_decorator(user_login_required, name='dispatch')
def subscribe_remove_selected(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    ids = request.GET.get('ids').split(",")
    updated = Subscription.objects.filter(user=request.user, id__in=ids).delete()
    messages.add_message(request, messages.SUCCESS, 'Removed successfully!')
    return HttpResponseRedirect(reverse('my-subscriptions'))


# @method_decorator(user_login_required, name='dispatch')
def get_active_plans(request):
    data = {}
    now = datetime.now()
    plans = serializers.serialize("json", StockSubscription.objects.filter(stock_id=request.POST.get('id'),
                                                                           removed=False, status=True,
                                                                           valid_until__gte=now))
    data['plans'] = plans
    return JsonResponse(data)


# @method_decorator(user_login_required, name='dispatch')
def subscription_hide_stock(request):
    data = {}
    data['status'] = 0
    subs = Subscription.objects.get(stock_id=request.POST.get('stock_id'), user=request.user)
    if subs:
        subs.is_hidden = True
        subs.save(False)
        data['status'] = 1
    return JsonResponse(data)
