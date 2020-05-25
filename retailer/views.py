import datetime
import pytz

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password


from retailer.helpers import get_access_token
from retailer.models import Shop, User

from shipment.helpers import sync_shipments_async

from utilities.loggers import logger as log


class ShopCredentials(APIView):
    def post(self, request):
        try:
            client_id = str(request.data.get('client_id', None))
            if Shop.objects.filter(client_id=client_id).exists():
                return Response({"message": "shop already registered for this client_id"},
                                status=status.HTTP_400_BAD_REQUEST)

            client_secret = request.data.get('client_secret', None)

            shop_name = request.data.get('name', client_id[:3])

            email = request.data['email']

            password = request.data['password']

            if not any([client_id, client_secret, email, password]):
                return Response({"message": "client_id, client_secret, email and password required for "
                                            "registering shop"}, status=status.HTTP_400_BAD_REQUEST)

            access_token, message = get_access_token(client_id=client_id, client_secret=client_secret)
            if access_token:
                delta = datetime.timedelta(minutes=5)
                now = datetime.datetime.utcnow()
                now = now.replace(tzinfo=pytz.utc)
                access_token_ttl = now + delta
                shop = Shop.objects.create(name=shop_name, client_id=client_id, client_secret=client_secret,
                                           stored_access_token=access_token, access_token_ttl=access_token_ttl)
                user = User.objects.create(email=email, shop=shop)
                user.set_password(password)
                user.save()

                sync_shipments_async(shop=shop)
                return Response({"message": "shop credentials registered and shipments will be synced"},
                                status=status.HTTP_200_OK)
            else:
                return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            log.exception(msg=e)


class ObtainAuthTokenView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.get(email=email)

        if check_password(password, user.password):
            return Response({"access_token": str(Token.objects.get(user=user))}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Email id and password doesn't matched"}, status=status.HTTP_400_BAD_REQUEST)
