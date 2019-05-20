from django.conf.urls import url, include
from . import views
from .views import (
    StockView, SingleView,
    load_db, stock_single,
    search, stock_stats,
    add_to_cart, get_cart,
    get_list, ajax_stock_single, ajax_stock_prediction,
    test, view_all_stocks, gainer_looser_most_active, most_popular
)

urlpatterns = [
    url(r'get-list/$', get_list, name='stocks.get_list'),
    url(r'get-cart/$', get_cart, name='get_cart'),
    url(r'^add-to-cart/$', add_to_cart, name='add_to_cart'),
    url(r'^stock_stats/$', stock_stats, name='stock.stats'),
    url(r'^ajax_stock_single/$', ajax_stock_single, name='stock.ajax_stock_single'),

    url(r'^ajax_stock_prediction/$', ajax_stock_prediction, name='stock.ajax_stock_prediction'),

    url(r'^test/$', test, name='stock.test'),
    url(r'^search/$', search, name='stock.search'),
    url(r'^load-db/$', views.load_db, name='stock.load_db'),
    url(r'^$', view_all_stocks, name='stock.all'),
    url(r'^gainer-looser-most-active$', gainer_looser_most_active, name='stock.gainer_looser'),
    url(r'^most-popular$', most_popular, name='stock.most_popular'),
    url(r'^(?P<symbol>.+)/$', stock_single, name='stock.single'),
]
