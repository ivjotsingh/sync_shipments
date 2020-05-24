from django.urls import path, include
from shipment.views import ShipmentView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ShipmentView)

urlpatterns = [
    path(r'', include(router.urls)),
]
