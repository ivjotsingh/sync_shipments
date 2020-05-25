from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password


from retailer.helpers import get_access_token
from retailer.models import Shop, User
from rest_framework.authtoken.models import Token

from shipment.helpers import sync_all_shipments, sync_shipments_async
# Create your views here.


class TestView(APIView):
    def get(self, request):
        print(request.data)
        return Response({"hey": "message"}, status=status.HTTP_200_OK)


class ShopCredentials(APIView):
    def post(self, request):
        try:
            client_id = str(request.data.get('client_id', None))
            if Shop.objects.filter(client_id=client_id).exists():
                # todo [IV] made status messages as constants
                return Response({"message": "shop already registered for this client_id"},
                                status=status.HTTP_400_BAD_REQUEST)

            client_secret = request.data.get('client_secret', None)
            if not any([client_id, client_secret]):
                return Response({"message": "client_id and client_secret for registering as a retailer"},
                                status=status.HTTP_400_BAD_REQUEST)

            shop_name = request.data.get('name', client_id[:3])

            access_token, message = get_access_token(client_id=client_id, client_secret=client_secret)
            if access_token:
                shop = Shop.objects.create(name=shop_name, client_id=client_id, client_secret=client_secret,
                                           access_token=access_token)
                user = User.objects.create(email=request.data['email'], shop=shop)
                user.set_password(request.data['password'])
                user.save()

                sync_shipments_async(shop=shop)
                return Response({"message": "shop credentials registered and shipments will be synced"},
                                status=status.HTTP_200_OK)
            else:
                return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # todo [IV] add logging
            print(e)


class ObtainAuthTokenView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.get(email=email)

        if check_password(password, user.password):
            return Response({"access_token": str(Token)}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Email id and password doesn't matched"}, status=status.HTTP_400_BAD_REQUEST)
