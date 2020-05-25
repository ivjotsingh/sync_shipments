import pika, os, json, environ, django

from decouple import config

environ.Env.read_env()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ['DJANGO_SETTINGS_MODULE'])
django.setup()


from shipment.helpers import ShipmentSync
from retailer.models import Shop


def sync_shipments(msg):
    print(" [x] Received " + str(msg))
    shop_id = json.loads(msg)['shop_id']
    sync = ShipmentSync(Shop.objects.get(id=shop_id))
    sync.sync_all_shipments()
    print("Shipments sync finished")
    return


# Access the CLODUAMQP_URL environment variable and parse it
url = config('CLOUDAMQP_URL')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel
channel.queue_declare(queue='shipments_sync') # Declare a queue


# create a function which is called on incoming messages
def callback(ch, method, properties, body):
    sync_shipments(body)


# set up subscription on the queue
channel.basic_consume('shipments_sync', callback, auto_ack=True)


# start consuming (blocks)
channel.start_consuming()
connection.close()