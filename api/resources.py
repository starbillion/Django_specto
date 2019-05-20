from tastypie.resources import ModelResource
from stocks.models import Stock

class StockResource(ModelResource):
    class Meta:
        queryset = Stock.objects.all()
        resource_name = 'stock'