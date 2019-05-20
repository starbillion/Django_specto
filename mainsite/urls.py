"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import (
    handler400, handler403,
    handler404, handler500
)
from .views import (
    LoginFormView, RegisterFormView,
    IndexView
)
from mainsite import views
from tastypie.api import Api
from api.resources import StockResource

v1_api = Api(api_name='v1')
v1_api.register(StockResource())

handler400 = 'mainsite.views.handler_400'
handler403 = 'mainsite.views.handler_403'
handler404 = 'mainsite.views.handler_404'
handler500 = 'mainsite.views.handler_500'

urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'^$', IndexView.as_view(), name='index'),
                  url(r'^logout/$', views.logout, name='logout'),
                  # url(r'^login/$', views.login, name='login'),
                  url(r'^login/$', LoginFormView.as_view(), name='login'),
                  url(r'^register/$', RegisterFormView.as_view(), name='register'),

                  # Registration Email
                  url(r'^registration/awaiting-confirmation/$', views.registration_awaiting_confirmation,
                      name='registration_awaiting_confirmation'),
                  url(r'^registration/verify/(?P<token>.+)/$', views.verify_email_registration,
                      name="registration_verify"),

                  # Reset Password
                  url(r'^password/request-reset/$', views.password_request_reset, name='password_request_reset'),
                  url(r'^password/process-reset/(?P<token>.+)/$', views.password_process_reset,
                      name="password_process_reset"),

                  url(r'^create/superuser/$', views.create_super_user, name='create_super_user'),

                  url(r'^users/', include('users.urls')),
                  url(r'^stocks/', include('stocks.urls')),
                  url(r'^subscriptions/', include('subscriptions.urls')),
                  # history of payment and subscription

                  url(r'^watchlist/', include('favourites.urls')),
                  url(r'^payment/', include('payment.urls')),
                  url(r'^predictions/', include('stocks.urls_prediction', namespace='predictions')),

                  ## Restful API
                  url(r'^api/', include(v1_api.urls)),

                  # Custom admin panel
                  url(r'^secret-admin/', include('secret-admin.urls')),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
