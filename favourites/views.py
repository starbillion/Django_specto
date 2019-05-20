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
from .models import (
    Favourite, FavouriteOrder
)
from stocks.helpers import (
    find_all_with_stock_info, api_get_stock_batch, point_round, is_stock_subscribed
)
from cart.cart import Cart
from django.contrib import messages
from subscriptions.models import (
    Subscription, StockSubscription
)
from mainsite.custom_decorators import (
    anonymous_required,
    user_login_required
)
from decimal import Decimal
import json
from django.db.models import Case, When
"""
Set a stock as favourite/un-favourite
Status var decides the action
Status: 1 => Set a stock as favourite
Status: 0 => Remove a stock from favourite list
"""


def reset_favourite_order(user, order_object):
    id_order_list = [int(__id) for __id in order_object.get_id_list if __id]
    id_list_from_db = user.favourite_set.filter(status=True).values_list('id', flat=True)
    pk_list = [__id for __id in id_order_list if int(__id) in id_list_from_db if __id]
    final_list = pk_list + list(set(id_list_from_db) - set(id_order_list))
    order_object.set_list(final_list)
    order_object.save()
    return final_list


# @method_decorator(user_login_required, name='dispatch')
def favourite_stock(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    stock = Stock.objects.get(pk=request.POST.get('stock_id'))
    status = request.POST.get('favourite_status')
    if int(status) == 1:
        status = False
    else:
        status = True
    stock_subscription, created = Favourite.objects.get_or_create(user=request.user, stock=stock)
    stock_subscription.status = status
    stock_subscription.save()
    return JsonResponse({'status': status, 'message': 'Subscribed successfully'})


# @method_decorator(user_login_required, name='dispatch')
class FavouritesViewNew(TemplateView):
    template_name = 'favourites/my_favourites.html'

    def get_context_data(self, **kwargs):
        context = super(FavouritesViewNew, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        favs_set = find_all_with_stock_info(self.request.user)
        context['favourites'] = favs_set['favs']
        context['realtime_quotes'] = favs_set['realtime_quotes']
        return context

# @method_decorator(user_login_required, name='dispatch')
class FavouritesView(TemplateView):
    template_name = 'favourites/favourites.html'

    def get_context_data(self, **kwargs):
        context = super(FavouritesView, self).get_context_data(**kwargs)
        context['user'] = self.request.user

        headers = ['Symbol', 'Name', 'Price', 'Change', 'Change %', 'Volume', 'Days Range', '52 week range',
                   'Market Cap.', 'Avg accuracy', "Previous accuracy", 'Forecasted Low',
                   'Forecasted High', 'Forecasted Close', 'id', 'Stock ID', 'Action']
        header_attributes = ['stock_symbol', 'stock_name', 'stock_price', 'change', 'changePercent', 'volume',
                            'days_range',
                            'week_52', 'market_cap', 'avg_acc_all_time', 'acc_prev_day', 'stock_low', 'stock_high',
                            'stock_close', 'id', 'stock_id', 'action']

        context['headers'] = headers
        context['header_attributes'] = header_attributes

        # Required for filter
        order_object = self.request.user.favouriteorder_set.first()
        if order_object:
            pk_list = reset_favourite_order(self.request.user, order_object)
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
            object_list = Favourite.objects.filter(pk__in=pk_list).order_by(preserved)
        else:
            object_list = Favourite.objects.filter(user=self.request.user, status=True).all()
        # Order

        symbols_set = []
        for fav in object_list:
            symbols_set.append(fav.stock.symbol)
        realtime_quotes = api_get_stock_batch(symbols_set)
        json_data = list()
        for fav in object_list:
            realtime_quote = realtime_quotes.get(fav.stock.symbol).get("quote")
            data_dict = {
                "id": fav.id,
                "status": fav.status,
                "stock_id": fav.stock.id,
                "stock_symbol": fav.stock.symbol,
                "avg_acc_all_time": fav.stock.get_all_time_avg,
                "acc_prev_day": fav.stock.get_prev_day_prediction,
                "stock_name": fav.stock.name,
                "stock_price": realtime_quote.get("latestPrice"),
                "change": point_round(realtime_quote.get("changePercent") * 100),
                "changePercent": point_round(realtime_quote.get("changePercent")),
                "volume": realtime_quote.get("latestVolume"),
                "days_range": "{} - {}".format(point_round(realtime_quote.get("low")), point_round(realtime_quote.get("high"))),
                "week_52": "{} - {}".format(point_round(realtime_quote.get("week52Low")), point_round(realtime_quote.get("week52High"))),
                "market_cap": str(round(Decimal(realtime_quote.get("marketCap")/1000000000), 3)) + "B",
                "stock_status": fav.stock.status,
                "stock_open": realtime_quote.get("open"),

            }
            if is_stock_subscribed(request_obj=self.request, stock_id=fav.stock.id):
                data_dict["stock_close"] = realtime_quote.get("close")
                data_dict["stock_low"] = realtime_quote.get("low"),
                data_dict["stock_high"] = realtime_quote.get("high")
                data_dict["action"] = ''
            else:
                data_dict["stock_close"] = ''
                data_dict["stock_low"] = ''
                data_dict["stock_high"] = ''
                if fav.stock.has_subscription:
                    data_dict["action"] = 'subscribe'
                else:
                    data_dict["action"] = ''
            json_data.append(data_dict)

        context['table_data'] = json_data

        return context


# @method_decorator(user_login_required, name='dispatch')
class TestView(TemplateView):
    template_name = 'subscriptions/test.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        return context


# @method_decorator(user_login_required, name='dispatch')
def test(request):
    data = find_all_with_stock_info(request.user)
    return HttpResponse(data)


# @method_decorator(user_login_required, name='dispatch')
def favourites_remove_all(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    updated = Favourite.objects.filter(user=request.user).delete()
    messages.add_message(request, messages.SUCCESS, 'Cleared alll subscriptions!')
    return HttpResponseRedirect(reverse('my-favourites'))


# @method_decorator(user_login_required, name='dispatch')
def unfavourite_all(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    updated = Favourite.objects.filter(user=request.user).update(status=False)
    messages.add_message(request, messages.SUCCESS, 'Unfavourited successfully!')
    return HttpResponseRedirect(reverse('my-favourites'))


# @method_decorator(user_login_required, name='dispatch')
def favourite_all(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    updated = Favourite.objects.filter(user=request.user).update(status=True)
    messages.add_message(request, messages.SUCCESS, 'Favourited successfully!')
    return HttpResponseRedirect(reverse('my-favourites'))


# @method_decorator(user_login_required, name='dispatch')
def unfavourite_selected(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    ids = request.GET.get('ids').split(",")
    updated = Favourite.objects.filter(user=request.user, id__in=ids).update(status=False)
    messages.add_message(request, messages.SUCCESS, 'Unfavourited successfully!')
    return HttpResponseRedirect(reverse('my-favourites'))


# @method_decorator(user_login_required, name='dispatch')
def favourite_remove_selected(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'})
    ids = request.GET.get('ids').split(",")
    updated = Favourite.objects.filter(user=request.user, id__in=ids).delete()
    messages.add_message(request, messages.SUCCESS, 'Favourites removed successfully!')
    return HttpResponseRedirect(reverse('my-favourites'))


def set_table_order(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'message': 'Invalid request!'}, status=500)
    id_list = request.POST.getlist('id_list[0][]')
    if id_list:
        obj, created = FavouriteOrder.objects.get_or_create(
            user=request.user
        )
        obj.set_list(id_list)
        obj.save()
    return JsonResponse({'status': 1, 'message': 'Invalid request!'}, status=200)