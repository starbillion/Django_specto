from django.conf.urls import url, include
from .views import (
    LoginFormView, IndexView,
    update_stock, remove_stock,
    admin_logout, stock_single,
    upload_csv_predictions, update_stock_predictions,
    get_stock_predictions_single, add_stock_predictions,
    remove_stock_prediction, ManageSubscriptionsView,
    update_stock_plan_subscriptions, get_stock_subscriptions,
    remove_stock_subscriptions, ManageSubscriptionsUsersView, send_email_to_expired_user,
    ManageRestrictedIPsDeviceView, single_user_ip_device, edit_single_user_ip_device,
    add_single_user_ip_device, remove_restricted_ip_device, add_single_user_ip_device_from
)

urlpatterns = [
    url(r'^$', LoginFormView.as_view(), name='admin.login'),
    url(r'^index/$', IndexView.as_view(), name='admin.index'),
    url(r'^logout/$', admin_logout, name='admin.logout'),
    url(r'^manage-subscriptions/$', ManageSubscriptionsView.as_view(), name='admin.manage-subscriptions'),
    url(r'^manage-subscriptions-of-users/$', ManageSubscriptionsUsersView.as_view(),
        name='admin.manage-subscriptions-of-users'),
    url(r'^manage-restricted-ips-device-of-users/$', ManageRestrictedIPsDeviceView.as_view(),
        name='admin.manage-restricted-ips-device-of-users'),

    url(r'^user/(?P<user_id>.+)/$', single_user_ip_device, name='admin.single-user-restricted-ip-device'),
    url(r'^edit-single-user-ip-device/$', edit_single_user_ip_device, name='admin.edit-single-user-ip-device'),

    url(r'^add-single-user-ip-device/$', add_single_user_ip_device, name='admin.add-single-user-ip-device'),
    url(r'^add-single-user-ip-device-from/$', add_single_user_ip_device_from, name='admin.add-single-user-ip-device-from'),

    url(r'^remove-single-user-ip-device/$', remove_restricted_ip_device, name='admin.remove-single-user-ip-device'),

    url(r'^send-email-to-expired-user/$', send_email_to_expired_user, name='admin.send-email-to-expired-user'),

    url(r'^update-stock-subscriptions', update_stock_plan_subscriptions, name='admin.update_stock_subscriptions'),
    url(r'^get-stock-subscriptions', get_stock_subscriptions, name='admin.get_stock_subscriptions'),
    url(r'^remove-stock-subscriptions', remove_stock_subscriptions, name='admin.remove_stock_subscriptions'),

    url(r'^get-stock-predictions-single/$', get_stock_predictions_single, name='admin.get_stock_predictions_single'),
    url(r'^stock-upload-csv/$', upload_csv_predictions, name='admin.upload_csv_predictions'),
    url(r'^stock-update-predictions/$', update_stock_predictions, name="admin.update_stock_predictions"),
    url(r'^stock-add-predictions/$', add_stock_predictions, name="admin.add_stock_predictions"),
    url(r'^stock/(?P<symbol>.+)/$', stock_single, name='admin.stock_single'),
    url(r'^update-stock/$', update_stock, name="admin.update_stock"),
    url(r'^remove-stock/$', remove_stock, name="admin.remove_stock"),
    url(r'^remove-stock-prediction/$', remove_stock_prediction, name="admin.remove_stock_prediction"),
]
