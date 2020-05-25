import uuid
import datetime

from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    shop = models.ForeignKey("retailer.Shop", on_delete=models.CASCADE, null=True, related_name='user')

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'user'


class Shop(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.CharField(max_length=51, blank=True, null=True)
    client_secret = models.CharField(max_length=250, blank=True, null=True)
    stored_access_token = models.CharField(max_length=250, blank=True, null=True)
    access_token_ttl = models.DateTimeField(null=True)
    name = models.CharField(max_length=50, null=True)

    @property
    def access_token(self):
        from shipment.helpers import refresh_access_token

        if datetime.datetime.now() > self.access_token_ttl:
            return refresh_access_token(self)
        else:
            return self.stored_access_token

    class Meta:
        db_table = 'shop'
