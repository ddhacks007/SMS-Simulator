import unittest
from unittest.mock import Mock, patch, call
import os
import string
from Producer.Main import Producer  

class TestProducer(unittest.TestCase):

    def setUp(self):
        self.mock_rabbitmq_client = Mock()
        self.mock_logger = Mock()
        self.producer = Producer(self.mock_rabbitmq_client, self.mock_logger)

    def test_generate_random_message(self):
        message = self.producer.generate_random_message()
        self.assertTrue(1 <= len(message) <= 100)
        self.assertTrue(all(c in string.ascii_letters + string.digits + string.punctuation for c in message))

    def test_generate_random_number(self):
        number = self.producer.generate_random_number()
        self.assertEqual(len(number), 10)
        self.assertTrue(number.isdigit())

    def test_generate_payload(self):
        payload = self.producer.generate_payload()
        self.assertIn('message', payload)
        self.assertIn('number', payload)
        self.assertIn('id', payload)
        self.assertEqual(payload['id'], 1)


    @patch('time.sleep', return_value=None)
    def test_run(self, mock_sleep):
        with patch.dict(os.environ, {'PRODUCER_MSG_DELAY': '0.1'}):
            self.producer.run(1)
            self.mock_rabbitmq_client.publish_message.assert_called_once()
            self.mock_logger.info.assert_called_once()
            log_call_args = self.mock_logger.info.call_args
            self.assertIn('PRODUCER: MESSAGE PUSHED SUCCESSFULLY 1', log_call_args[0])
            self.assertEqual(log_call_args[1]['extra']['message_id'], 1)
            self.assertEqual(log_call_args[1]['extra']['logger'], 'Producer')
            self.assertEqual(log_call_args[1]['extra']['status'], 'Pushed')

    @patch('time.sleep', return_value=None)
    def test_run_multiple_messages(self, mock_sleep):
        with patch.dict(os.environ, {'PRODUCER_MSG_DELAY': '0.1'}):
            num_messages = 3
            self.producer.run(num_messages)
            self.assertEqual(self.mock_rabbitmq_client.publish_message.call_count, num_messages)
            self.assertEqual(self.mock_logger.info.call_count, num_messages)
            for i in range(1, num_messages + 1):
                self.mock_logger.info.assert_any_call(
                    f'PRODUCER: MESSAGE PUSHED SUCCESSFULLY {i}',
                    extra={'message_id': i, 'logger': 'Producer', 'status': 'Pushed'}
                )

    
    
if __name__ == '__main__':
    unittest.main()
