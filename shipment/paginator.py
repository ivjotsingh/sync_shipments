from rest_framework.pagination import PageNumberPagination


class ShipmentListPagination(PageNumberPagination):
    page_size = 10
