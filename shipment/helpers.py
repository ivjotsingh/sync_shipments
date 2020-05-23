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
    for _ in range(2):
        try:
            if Shipment.objects.filter(shipment_id=shipment_id).exists():
                print("already")
                break

            shipment_url = f"https://api.bol.com/retailer/shipments/{shipment_id}"
            headers = {
                "Authorization": f"Bearer {shop.access_token}",
                "Accept": "application/vnd.retailer.v3+json",
            }

            response = requests.get(shipment_url, headers=headers)
            response_data = json.loads(response._content)

            if response_data.get('title', '') == 'Expired JWT' and response_data.get('status') == 401:
                refresh_access_token(shop=shop)

            elif response_data.get('status') == 429:
                time.sleep(60)
            else:
                shipment = Shipment.objects.create(shipment_id=response_data['shipmentId'],
                                                   pick_up_point=response_data['pickUpPoint'],
                                                   shipment_date=response_data['shipmentDate'],
                                                   shipment_reference=response_data['shipmentReference'],
                                                   shipment_items=response_data['shipmentItems'],
                                                   transport=response_data['transport'],
                                                   customer_details=response_data['customerDetails'],
                                                   billing_details=response_data['billingDetails'],
                                                   shop=shop,
                                                   fulfilment_method=response_data['shipmentItems'][0]
                                                   ['fulfilmentMethod'])
                break

        except Exception as e:
            # todo [IV] log exception
            print(e)
