import time
import requests
import json
import concurrent.futures

from shipment.models import Shipment

from utilities.loggers import logger as log
from utilities.exceptions import TooManyRequestsException
from utilities.communication import send_async_message


def sync_shipments_async(shop):
    body = {
        'shop_id': str(shop.id)
    }
    send_async_message(message=json.dumps(body), queue_name='shipment_queue', routing_key='shipment_queue')


class ShipmentSync:
    def __init__(self, shop):
        self.shop = shop

    def sync_shipment_by_id(self, shipment_id):
        for _ in range(5):
            try:
                if Shipment.objects.filter(shipment_id=shipment_id).exists():
                    log.info("Shipment Already exists in the database")
                    break

                shipment_url = f"https://api.bol.com/retailer/shipments/{shipment_id}"
                headers = {
                    "Authorization": f"Bearer {self.shop.access_token}",
                    "Accept": "application/vnd.retailer.v3+json",
                }

                response = requests.get(shipment_url, headers=headers)
                response_data = json.loads(response._content)

                if response_data.get('status') == 429:
                    log.info("sleeping in sync_shipment_by_id for 60 seconds")
                    raise TooManyRequestsException

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
                    log.info(f"{shipment.shipment_id} synced")
                    break

            except TooManyRequestsException:
                time.sleep(60)
                continue

            except Exception as e:
                log.exception(e)

    def sync_all_shipments(self):
        all_shipments = []
        for i in range(5):
            page = 1
            all_shipments_collected = False
            while True:
                try:
                    log.info(f'iteration {i}')
                    log.info("response data != {}")
                    shipment_url = f"https://api.bol.com/retailer/shipments?page={page}"
                    headers = {
                        "Authorization": f"Bearer {self.shop.access_token}",
                        "Accept": "application/vnd.retailer.v3+json",
                    }

                    response = requests.get(shipment_url, headers=headers)
                    response_data = json.loads(response._content)

                    if response_data.get('status') == 429:
                        raise TooManyRequestsException
                    else:
                        if response_data != {}:
                            for shipment in response_data['shipments']:
                                all_shipments.append(shipment['shipmentId'])
                                log.info(shipment['shipmentId'])
                            page += 1
                        else:
                            all_shipments_collected = True
                            break

                except TooManyRequestsException:
                    log.info("sleeping in sync all shipments for 60 seconds")
                    time.sleep(60)
                    continue

                except Exception as e:
                    log.exception(e)
                    break
            if all_shipments_collected:
                break

        # syncing shipments in chunk of 5
        for i in range(0, len(all_shipments), 5):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                shipment_ids_chunk = all_shipments[i:i + 5]
                executor.map(self.sync_shipment_by_id, shipment_ids_chunk)
