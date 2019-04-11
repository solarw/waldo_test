from typing import Union


import pika
from sqlalchemy.dialects.postgresql.base import UUID

from conf import AMQP_URI
from conf import QUEUE_NAME


class PikaClient:
    """ cause lost connection after timeout
        possible can be fixed with threads, but not sure
    """

    def __init__(self, amqp_uri, queue_name):
        self.amqp_uri = amqp_uri
        self.queue_name = queue_name
        self.set_channel()
        self.set_queue()

    def set_queue(self):
        self.channel.queue_declare(queue=self.queue_name)

    def set_channel(self):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(
                self.amqp_uri,
            )
        )
        self.channel = self.connection.channel()

    def publish(self, body):
        try:
            self._publish(body)
        except pika.exceptions.StreamLostError:
            self.set_channel()
            self._publish(body)

    def _publish(self, body):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=body,
        )


pika_client = PikaClient(AMQP_URI, QUEUE_NAME)


def trigger_process_photo_task(uuid: Union[UUID, str]):
    uuid = str(uuid)
    pika_client.publish(uuid)
