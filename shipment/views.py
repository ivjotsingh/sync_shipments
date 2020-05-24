from shipment.paginator import ShipmentListPagination
from shipment.serializers import ShipmentSerializer
from shipment.models import Shipment
from rest_framework import viewsets
# Create your views here.


class ShipmentView(viewsets.ReadOnlyModelViewSet):
    pagination_class = ShipmentListPagination
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.all()

    def get_queryset(self):
        print(self.request.query_params)
        filter_object = Shipment.objects.all()

        if 'fulfilment_method' in self.request.query_params:
            print("yes the condition is True")
            print(self.request.query_params['fulfilment_method'])
            filter_object = filter_object.filter(fulfilment_method=self.request.query_params['fulfilment_method'])

        return filter_object

