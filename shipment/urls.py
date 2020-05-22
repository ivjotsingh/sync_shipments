from django.urls import path
from retailer.views import TestView

urlpatterns = [
    path(r'test/', TestView.as_view(), name="test_site"),
]