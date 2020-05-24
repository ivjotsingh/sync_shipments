import time
import requests
import json
import concurrent.futures

from retailer.helpers import refresh_access_token
from shipment.models import Shipment


def get_shipment_ids():
    pass


def sync_shipments_async(shop):
    pass


class ShipmentSync():
    def __init__(self, shop):
        self.shop = shop

    def sync_shipment_by_id(self, shipment_id):
        for _ in range(5):
            try:
                if Shipment.objects.filter(shipment_id=shipment_id).exists():
                    print("already")
                    break

                shipment_url = f"https://api.bol.com/retailer/shipments/{shipment_id}"
                headers = {
                    "Authorization": f"Bearer {self.shop.access_token}",
                    "Accept": "application/vnd.retailer.v3+json",
                }

                response = requests.get(shipment_url, headers=headers)
                response_data = json.loads(response._content)

                if response_data.get('title', '') == 'Expired JWT' and response_data.get('status') == 401:
                    refresh_access_token(shop=self.shop)

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
                                                       shop=self.shop,
                                                       fulfilment_method=response_data['shipmentItems'][0]
                                                       ['fulfilmentMethod'])
                    print(f"{shipment.shipment_id} synced")
                    break

            except Exception as e:
                # todo [IV] log exception
                print(e)

    def sync_all_shipments(self):
        all_shipments = []
        for i in range(5):
            try:
                print(f'iteration {i}')
                page = 1
                while True:
                    print("response data != {}")
                    shipment_url = f"https://api.bol.com/retailer/shipments?page={page}"
                    headers = {
                        "Authorization": f"Bearer {self.shop.access_token}",
                        "Accept": "application/vnd.retailer.v3+json",
                    }

                    response = requests.get(shipment_url, headers=headers)
                    response_data = json.loads(response._content)

                    if response_data.get('title', '') == 'Expired JWT' and response_data.get('status') == 401:
                        refresh_access_token(shop=self.shop)
                        break

                    elif response_data.get('status') == 429:
                        time.sleep(60)
                        break
                    else:
                        if response_data != {}:
                            for shipment in response_data['shipments']:
                                all_shipments.append(shipment['shipmentId'])
                                print(shipment['shipmentId'])
                            page += 1
                        else:
                            break
            except Exception as e:
                # todo [IV] log exception
                print(e)
            break
        for i in range(0, len(all_shipments), 5):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                shipment_ids_chunk = all_shipments[i:i + 5]
                executor.map(self.sync_shipment_by_id, shipment_ids_chunk)