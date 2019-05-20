from django.db import models
from mainsite.models import User
from stocks.models import Stock
from datetime import datetime, timedelta


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    status = models.BooleanField(default=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def get_user(self):
        '''
        Return the Char result corresponding to the user
        '''
        return self.user

    def get_stock(self):
        '''
        Return the Stock corresponding to the subscription
        '''
        return self.stock


class FavouriteOrder(models.Model):
    id_list = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def set_list(self, id_list):
        if id_list:
            self.id_list = ','.join(map(str, id_list))

    @property
    def get_id_list(self):
        if self.id_list:
            return self.id_list.split(",")
        else:
            return []