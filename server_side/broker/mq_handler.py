import pika
import settings


class RabbitMQHandler:

    def __init__(self):
        try:
            parameters = pika.URLParameters('amqp://guest:guest@localhost:5672/%2F')
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
        except (pika.exceptions.AMQPConnectionError, AttributeError):
            quit('Cannot connect to RabbitMQ.')

        self.exchange_name = None
        self.queue_name = None

    def create_exchange(self, exchange_name='TestExchange'):
        self.channel.exchange_declare(exchange_name)
        self.exchange_name = exchange_name

    def create_and_bind_queue(self, queue_name='TestQueue', exchange_name=None):
        exchange_name = exchange_name if exchange_name else self.exchange_name
        self.queue_name = queue_name
        self.channel.queue_declare(queue_name, durable=True)
        self.channel.queue_bind(queue=queue_name, exchange=exchange_name)

    def send_message(self):
        properties = pika.BasicProperties(content_type='text/plain', delivery_mode=settings.MQ_DELIVERY_MODE)
        self.channel.basic_publish(exchange='TestExchange', routing_key=self.queue_name, body='Test message',
                                   properties=properties)

    def receive_message(self):
        method, _, body = self.channel.basic_get(self.queue_name)
        self.channel.basic_ack(method.delivery_tag)
        return body

    def __del__(self):
        if hasattr(self, 'channel'):
            self.channel.close()
        if hasattr(self, 'connection'):
            self.connection.close()


if __name__ == '__main__':
    handler = RabbitMQHandler()
    handler.create_exchange()
    handler.create_and_bind_queue()
    handler.send_message()
    handler.receive_message()
