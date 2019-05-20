from django.conf.urls import url, include
from . import views
from .views import (
    reset_sources, subscribe_stock,
    SubscriptionsView,
    test, TestView,
    subscribe_unsubscribe_all, subscribe_remove_all,
    subscribe_subscribe_all, subscribe_unsubscribe_selected,
    subscribe_remove_selected, get_active_plans,
    subscription_hide_stock, set_table_order, HistoryView
)

urlpatterns = [
    url(r'^test/$', test, name='stock.test'),
    url(r'^test-view/$', TestView.as_view(), name='subs.TestView'),
    url(r'^$', SubscriptionsView.as_view(), name='my-subscriptions'),

    url(r'^history/$', HistoryView.as_view(), name='my-subscriptions-history'),

    url(r'^subscriptions-unsubscribe-all/$', subscribe_unsubscribe_all, name='subs.unsubscribe_all'),
    url(r'^subscriptions-subscribe-all/$', subscribe_subscribe_all, name='subs.subscribe_all'),
    url(r'^subscriptions-unsubscribe-selected/$', subscribe_unsubscribe_selected, name='subs.unsubscribe_selected'),
    url(r'^subscriptions-remove-selected/$', subscribe_remove_selected, name='subs.remove_selected'),

    url(r'^subscriptions-hide-stock/$', subscription_hide_stock, name='subscription.hide_stock'),
    url(r'^active-plans/$', get_active_plans, name='subscription.get_active_plans'),
    url(r'^subscriptions-remove-all/$', subscribe_remove_all, name='subs.remove_all'),
    url(r'^reset-sources/$', reset_sources, name='subscription.reset_sources'),
    url(r'^subscribe-stock/$', subscribe_stock, name='subscription.subscribe_stock'),

    url(r'^set-table-order/$', set_table_order, name='subscription.set_table_order'),
]
