import random
import os
import string
from RabbitMQClient import RabbitMQClient
from dotenv import load_dotenv
import time
import json
from Logger import init_logger
load_dotenv()

class Producer:
    def __init__(self, rabbitmq_client, logger):
        self.rabbitmq_client = rabbitmq_client
        self.logger = logger
        self.id = 0

    def generate_random_message(self):
        message_length = random.randint(1, 100)
        message = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=message_length))
        return message

    def generate_random_number(self):
        return ''.join(random.choices(string.digits, k=10))

    def generate_payload(self):
        self.id += 1
        return {'message': self.generate_random_message(), 'number': self.generate_random_number(), 'id': self.id}
    
    def run(self, num_messages):
        producer_msg_delay = float(os.getenv('PRODUCER_MSG_DELAY'))
        for _ in range(num_messages):
            payload = json.dumps(self.generate_payload())
            self.rabbitmq_client.publish_message(payload)
            self.logger.info(f'PRODUCER: MESSAGE PUSHED SUCCESSFULLY {self.id}', extra={'message_id': self.id,  'logger': 'Producer', 'status': 'Pushed'})
        
            time.sleep(producer_msg_delay)
        
if __name__ == "__main__":
    logger = init_logger()
    client = RabbitMQClient()
    producer = Producer(client, logger)
    run_forever = os.getenv('PRODUCER_RUN_FOREVER') == 'True'
    while True:
        producer.run(int(os.environ['TOTAL_MESSAGES']))
        if not run_forever:
            break
        
    client.close_connection()
    