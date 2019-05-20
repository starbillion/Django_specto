from django.conf.urls import url, include
from . import views
from .views import (get_stocks_ajax,
                    view_all_stocks_with_predictions,
new_sub_available_with_predictions, highest_accuracy_stocks
)
app_name = 'stocks'
urlpatterns = [
    url(r'get-all-stocks-with-predictions-list/ajax/$', get_stocks_ajax, name='get_stocks_ajax'),
    url(r'^all-stocks-with-predictions$', view_all_stocks_with_predictions, name='view_all_stocks_with_predictions'),
    url(r'^new-subscription-available$', new_sub_available_with_predictions, name='new_sub_available_with_predictions'),
    url(r'^highest-accuracy-stocks$', highest_accuracy_stocks, name='highest_accuracy_stocks'),

]
