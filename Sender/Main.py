import os
import random
import json
import ast
import numpy as np
import time
from dotenv import load_dotenv
from RabbitMQClient import RabbitMQClient
from RedisClient import RedisClient
from Logger import init_logger
load_dotenv()


class Sender:
    """Class for sending messages through RabbitMQ with simulated processing times and failure rates."""

    def __init__(self, rabbitmq_client: RabbitMQClient, redis_client: RedisClient, logger):
        self.logger = logger
        self.fc = 0
        self.sc = 0
        
        self.redis_client = redis_client
        self.rabbitmq_client = rabbitmq_client
        self.message_index = 0
        self.batch_size = 10
        self.id = self.redis_client.get_unique_id() - 1

        processing_times_str = os.getenv('MESSAGE_PROCESSING_TIME')
        self.mean_time = ast.literal_eval(processing_times_str)[self.id]

        failure_rates_str = os.getenv('FAILURE_RATE')
        self.failure_rate = ast.literal_eval(failure_rates_str)[self.id]
        self.failure_count = sum(self.simulate_bernoulli_trials(self.failure_rate))
        self.failure_indexes = set()

    def simulate_bernoulli_trials(self, probability: float):
        """Simulate Bernoulli trials for a given probability."""
        return np.random.binomial(1, probability, self.batch_size)

    def update_failure_indexes(self):
        """Update the set of indexes where message sending should fail."""
        self.failure_indexes = set(random.sample(range(self.batch_size), self.failure_count))

    def send_sms(self, ch, method, properties, body):
        """Process and send SMS messages with simulated failures."""
        payload = json.loads(body)
        if self.message_index % self.batch_size == 0:
            self.update_failure_indexes()

        processing_time = max(0, random.gauss(*self.mean_time))
        time.sleep(processing_time)
        if self.message_index % self.batch_size in self.failure_indexes:
            self.logger.info(f'SENDER: Failed to send the message to the number {payload["number"]} id: {payload["id"]}', extra={
                'message_id': payload['id'], 'process_time': processing_time, 'logger': 'Sender', 'status': 'MSG-FAILED'
            })
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            self.fc += 1
        else:
            self.logger.info(f'SENDER: Successfully sent the message to the number {payload["number"]} id: {payload["id"]}', extra={
                'message_id': payload['id'], 'process_time': processing_time, 'logger': 'Sender', 'status': 'MSG-SENT'
            })
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.sc += 1
        
        self.message_index += 1


if __name__ == "__main__":
    logger = init_logger()
    redis_client = RedisClient()
    rmq_client = RabbitMQClient()
    sender = Sender(rmq_client, redis_client, logger)
    rmq_client.start_consuming(sender.send_sms)
