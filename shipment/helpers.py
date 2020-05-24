import time
import requests
import json
import concurrent.futures
import pika, os, logging

from decouple import config

from retailer.helpers import refresh_access_token
from shipment.models import Shipment

#from boloo_env_helper import boloo_env
logging.basicConfig()


def sync_shipments_async(shop):
    # method defined is used to sync all the shipments
    url = config('CLOUDAMQP_URL')
    print(f'URL {url}')
    params = pika.URLParameters(url)
    params.socket_timeout = 5

    connection = pika.BlockingConnection(params)  # Connect to CloudAMQP
    channel = connection.channel()  # start a channel
    channel.queue_declare(queue='shipments_sync')  # Declare a queue
    # send a message
    body = {
        'shop_id': str(shop.id)
    }
    channel.basic_publish(exchange='', routing_key='shipments_sync', body=json.dumps(body))
    print("[x] Message sent to consumer")
    connection.close()


def sync_all_shipments():
    pass


class ShipmentSync:
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
                    print("sleeping in sync_shipment_by_id for 60 seconds")
                    time.sleep(60)
                else:
                    shipment = Shipment.objects.create(shipment_id=response_data['shipmentId'],
                                                       pick_up_point=response_data['pickUpPoint'],
                                                       shipment_date=response_data['shipmentDate'],
                                                       shipment_reference=response_data.get('shipmentReference', None),
                                                       shipment_items=response_data['shipmentItems'],
                                                       transport=response_data['transport'],
                                                       customer_details=response_data['customerDetails'],
                                                       billing_details=response_data.get('billingDetails', None),
                                                       shop=self.shop,
                                                       fulfilment_method=response_data['shipmentItems'][0]
                                                       ['fulfilmentMethod'])
                    print(f"{shipment.shipment_id} synced")
                    break

            except Exception as e:
                # todo [IV] log exception
                print(e)
                raise Exception

    def confirm_complete_sync(self):
        pass

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
                        print("sleeping in sync all shipments for 60 seconds")
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
                raise Exception
            break
        for i in range(0, len(all_shipments), 5):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                shipment_ids_chunk = all_shipments[i:i + 5]
                executor.map(self.sync_shipment_by_id, shipment_ids_chunk)
