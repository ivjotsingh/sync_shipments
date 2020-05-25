from shipment.paginator import ShipmentListPagination
from shipment.serializers import ShipmentSerializer
from shipment.models import Shipment
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication


class ShipmentView(viewsets.ReadOnlyModelViewSet):
    pagination_class = ShipmentListPagination
    serializer_class = ShipmentSerializer
    authentication_classes = [TokenAuthentication, ]
    queryset = Shipment.objects.all()

    def get_queryset(self):
        if str(self.request.user) == 'AnonymousUser':
            # only authenticated users gets the data associated with user's shop
            filter_object = Shipment.objects.filter(shop=None)
        else:
            filter_object = Shipment.objects.filter(shop=self.request.user.shop)

        if 'fulfilment_method' in self.request.query_params:
            filter_object = filter_object.filter(fulfilment_method=self.request.query_params['fulfilment_method'])

        return filter_object

