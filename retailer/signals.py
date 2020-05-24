from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from retailer.models import BolooUser

from rest_framework.authtoken.models import Token


# For saving token whenever a new user is created
@receiver(post_save, sender=BolooUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created is True:
        Token.objects.create(user=instance)
