from django.conf.urls import url, include
from . import views
from .views import (
    ProfileView, SummaryView, StockView,
    ActivityView,
    AccountSettingsView, api_country,
    api_state, api_city
)

urlpatterns = [
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    url(r'^profile/save$', views.save_profile, name='save_profile'),

    url(r'^account-settings/$', AccountSettingsView.as_view(), name='account-settings'),

    url(r'^add-restricted-ip-device/$', views.add_restricted_ip_device, name='add-restricted-ip-device'),
    url(r'^edit-restricted-ip-device/$', views.edit_restricted_ip_device, name='edit-restricted-ip-device'),
    url(r'^remove-restricted-ip-device/$', views.remove_restricted_ip_device, name='remove-restricted-ip-device'),
    url(r'^activity/$', AccountSettingsView.as_view(), name='activity'),

    url(r'^summary/$', SummaryView.as_view(), name='summary'),

    # url(r'^stock/single/$', StockView.as_view(), name='stock.single'),

    url(r'^api/country/$', api_country, name='api_country'),
    url(r'^api/state/(?P<code>.+)$', api_state, name='api_state'),
    url(r'^api/city/(?P<code>.+)$', api_city, name='api_city'),

    # url(r'^stock/single/$', StockView.as_view(), name='stock.single'),
    # url(r'^stock/single/$', StockView.as_view(), name='stock.single'),

    # Image Uploading
    url(r'^upload-avatar/$', views.upload_avatar, name='upload_avatar'),
    url(r'^remove-avatar/$', views.remove_avatar, name='remove_avatar'),
    # Testing
    url(r'^test/$', views.test, name='test'),

]
