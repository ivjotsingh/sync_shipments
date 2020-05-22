import time
import requests
import json

from retailer.helpers import refresh_access_token
from shipment.models import Shipment


def get_shipment_ids():
    pass


def sync_all_shipments(access_token):
    pass


def sync_shipment_by_id(shop, shipment_id=750036379):
    while True:
        sync = False
        try:
            if Shipment.objects.filter(shipment_id=shipment_id).exists():
                sync = True
                return sync
            shipment_url = f"https://api.bol.com/retailer/shipments/{shipment_id}"
            headers = {
                "Authorization": f"Bearer {shop.access_token}",
                "Accept": "application/vnd.retailer.v3+json",
            }

            response = requests.get(shipment_url, headers=headers)
            print(response)
            print(vars(response))
            response_data = json.loads(response._content)
            print(response_data['title'])
            print()
            # todo [add 2 attempts]
            if response_data['title'] == 'Expired JWT' and response_data['status'] == 401:
                print("coming here baby")
                refresh_access_token(shop=shop)
                continue
            else:
                sync = True

        except Exception as e:
            if Exception == '429':
                time.sleep(60)
            elif Exception == 'token Exception':
                refresh_access_token(shop=shop)
        if sync:
            break
