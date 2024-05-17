import os
import time
import unittest
from unittest.mock import patch, Mock
from RabbitMQClient import RabbitMQClient  
import pika

class TestRabbitMQClient(unittest.TestCase):

    @patch('pika.BlockingConnection')
    @patch('pika.ConnectionParameters')
    @patch.dict(os.environ, {'HOST': 'localhost', 'EXCHANGE_NAME': 'test_exchange', 'ROUTING_KEY': 'test_routing_key', 'QUEUE_NAME': 'test_queue', 'EXCHANGE_TYPE': 'direct', 'RMQ_RETRIES': '20'})
    def setUp(self, mock_connection_params, mock_blocking_connection):
        self.mock_channel = Mock()
        self.mock_connection = Mock()
        self.mock_connection.channel.return_value = self.mock_channel
        mock_blocking_connection.return_value = self.mock_connection
        self.client = RabbitMQClient()

    def test_create_exchange(self):
        self.client.create_exchange()
        self.mock_channel.exchange_declare.assert_called_with(exchange='test_exchange', exchange_type='direct', durable=True)

    def test_create_queue(self):
        self.client.create_queue()
        self.mock_channel.queue_declare.assert_called_with(queue='test_queue', durable=True)

    def test_bind_queue(self):
        self.client.bind_queue()
        self.mock_channel.queue_bind.assert_called_with(queue='test_queue', exchange='test_exchange', routing_key='test_routing_key')

    def test_connect_successful(self):
        self.assertIsNotNone( self.client.connection)
    
    @patch('pika.BlockingConnection', side_effect=pika.exceptions.AMQPConnectionError)
    @patch('time.sleep', return_value=None)
    def test_connect_failure(self,sleep, mock_blocking_connection):
        with self.assertRaises(pika.exceptions.AMQPConnectionError):
            RabbitMQClient()
        
    def test_init_exchange_and_queue(self):
        self.client.init_exchange_and_queue()
        self.mock_channel.exchange_declare.assert_called_with(exchange='test_exchange', exchange_type='direct', durable=True)
        self.mock_channel.queue_declare.assert_called_with(queue='test_queue', durable=True)
        self.mock_channel.queue_bind.assert_called_with(queue='test_queue', exchange='test_exchange', routing_key='test_routing_key')

    def test_publish_message(self):
        message = "test_message"
        self.client.publish_message(message)
        self.mock_channel.basic_publish.assert_called_with(exchange='test_exchange', routing_key='test_routing_key', body=message)

    def test_start_consuming(self):
        callback = Mock()
        with patch.object(self.mock_channel, 'start_consuming') as mock_start_consuming:
            self.client.start_consuming(callback)
            self.mock_channel.basic_consume.assert_called_with(queue='test_queue', on_message_callback=callback, auto_ack=False)
            mock_start_consuming.assert_called_once()
    
    def test_close_connection(self):
        self.client.close_connection()
        self.mock_connection.close.assert_called_once()
    
        
    
if __name__ == '__main__':
    unittest.main()
