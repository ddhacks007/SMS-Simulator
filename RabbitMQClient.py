import os
import time
import logging
from dotenv import load_dotenv
import pika
load_dotenv()
logging.basicConfig(level=logging.ERROR)

class RabbitMQClient:
    """Client for interacting with RabbitMQ, supporting both consumer and producer roles."""
    
    def __init__(self):
        self.connection = None
        self.connect()
        self.channel = self.connection.channel()
        self.exchange_name = os.getenv('EXCHANGE_NAME', 'default_exchange')
        self.routing_key = os.getenv('ROUTING_KEY', 'default_routing_key')
        self.queue_name = os.getenv('QUEUE_NAME', 'default_queue')
        self.exchange_type = os.getenv('EXCHANGE_TYPE', 'direct')
        self.max_retries = int(os.getenv('RMQ_RETRIES', 20))
        self.init_exchange_and_queue()

    def connect(self):
        """Establish a connection to RabbitMQ."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('HOST', 'localhost')))
                return
            except pika.exceptions.AMQPConnectionError as e:
                if attempt < max_retries - 1:
                    logging.error('Connection Failed, retrying in 3 seconds...')
                    time.sleep(3)
                else:
                    logging.exception("Failed to connect to RabbitMQ after several attempts.")
                    raise

    def init_exchange_and_queue(self):
        """Initialize exchange and queue on RabbitMQ server."""
        try:
            self.create_exchange()
            self.create_queue()
            self.bind_queue()
        except Exception as e:
            pass

    def create_exchange(self):
        """Declare an exchange on RabbitMQ."""
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type, durable=True)

    def create_queue(self):
        """Declare a queue on RabbitMQ."""
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def bind_queue(self):
        """Bind the queue to an exchange with a specific routing key."""
        self.channel.queue_bind(queue=self.queue_name, exchange=self.exchange_name, routing_key=self.routing_key)

    def publish_message(self, message: str):
        """Publish a message to a RabbitMQ exchange."""
        self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=message)
        logging.info("Message published to %s using routing key %s.", self.exchange_name, self.routing_key)

    def start_consuming(self, callback):
        """Start consuming messages from a RabbitMQ queue."""
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            logging.info("Consuming stopped by KeyboardInterrupt.")

    def close_connection(self):
        """Close the connection to RabbitMQ."""
        if self.connection:
            self.connection.close()
            logging.info("RabbitMQ connection closed.")
    
