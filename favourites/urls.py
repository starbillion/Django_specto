from django.conf.urls import url, include
from . import views
from .views import (
    test, favourite_stock,
    FavouritesView, unfavourite_all,
    favourite_all, unfavourite_selected,
    favourite_remove_selected, favourites_remove_all, set_table_order
)

urlpatterns = [
    url(r'^test/$', test, name='favourite.test'),
    url(r'^favourite-stock/$', favourite_stock, name='favourites.favourite_stock'),
    #url(r'^new$', FavouritesViewNew.as_view(), name='my-favourites-new'),
    url(r'^$', FavouritesView.as_view(), name='my-favourites'),
    url(r'^unfavourite-all/$', unfavourite_all, name='fav.unfavourite_all'),
    url(r'^favourite-all/$', favourite_all, name='fav.favourite_all'),
    url(r'^unfavourite-selected/$', unfavourite_selected, name='fav.unfavourite_selected'),
    url(r'^favourites-remove-selected/$', favourite_remove_selected, name='fav.remove_selected'),
    url(r'^set-table-order/$', set_table_order, name='favorites.set_table_order'),
    url(r'^favourites-remove-all/$', favourites_remove_all, name='fav.remove_all'),

]
