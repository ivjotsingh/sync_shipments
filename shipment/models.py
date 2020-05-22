import uuid
import jsonfield

from django.db import models
from django_extensions.db.models import TimeStampedModel


from retailer.models import Shop


class Shipment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment_id = models.BigIntegerField(unique=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    pick_up_point = models.BooleanField()
    shipment_date = models.DateTimeField(null=True)
    shipment_reference = models.CharField(max_length=50, null=True)
    fulfilment_method = models.CharField(max_length=7, null=True)
    shipment_items = jsonfield.JSONField()
    transport = jsonfield.JSONField()
    customer_details = jsonfield.JSONField()
    billing_details = jsonfield.JSONField()

    class Meta:
        db_table = 'shipment'
