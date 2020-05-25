from django.urls import path
from retailer.views import ShopCredentials, ObtainAuthTokenView

urlpatterns = [
    path(r'shop-credentials/', ShopCredentials.as_view(), name="shop_credentials"),
    path(r'obtain-auth-token/', ObtainAuthTokenView.as_view(), name='auth-token')
]