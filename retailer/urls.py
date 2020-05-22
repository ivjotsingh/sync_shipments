from django.urls import path
from retailer.views import TestView, ShopCredentials

urlpatterns = [
    path(r'test/', TestView.as_view(), name="test_site"),
    path(r'shop-credentials/', ShopCredentials.as_view(), name="shop_credentials")
]