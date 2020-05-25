import pika

from decouple import config

from utilities.loggers import logger as log


def send_async_message(message, queue_name, routing_key):
    # method defined is used to sync all the shipments
    url = config('CLOUDAMQP_URL')
    log.info(f'URL {url}')
    params = pika.URLParameters(url)
    params.socket_timeout = 5

    connection = pika.BlockingConnection(params)  # Connect to CloudAMQP
    channel = connection.channel()  # start a channel
    channel.queue_declare(queue=queue_name)  # Declare a queue
    # send a message

    channel.basic_publish(exchange='', routing_key=routing_key, body=message)
    log.info("[x] Message sent to consumer")
    connection.close()

