import unittest
from unittest.mock import Mock, patch, call
import os
import json
import numpy as np
from Sender.Main import Sender 

class TestSender(unittest.TestCase):

    def setUp(self):
        self.mock_rabbitmq_client = Mock()
        self.mock_redis_client = Mock()
        self.mock_logger = Mock()
        
        os.environ['MESSAGE_PROCESSING_TIME'] = '[[0.5, 1], [0.6, 1]]'
        os.environ['FAILURE_RATE'] = '[0.1, 0.2]'
        
        self.mock_redis_client.get_unique_id.return_value = 1
        
        self.sender = Sender(self.mock_rabbitmq_client, self.mock_redis_client, self.mock_logger)

    def test_initialization(self):
        self.assertEqual(self.sender.fc, 0)
        self.assertEqual(self.sender.sc, 0)
        self.assertEqual(self.sender.message_index, 0)
        self.assertEqual(self.sender.batch_size, 10)
        self.assertEqual(self.sender.id, 0)
        self.assertEqual(self.sender.mean_time, [0.5,1])
        self.assertEqual(self.sender.failure_rate, 0.1)
        self.assertEqual(len(self.sender.failure_indexes), 0)

    def test_simulate_bernoulli_trials(self):
        trials = self.sender.simulate_bernoulli_trials(0.5)
        self.assertEqual(len(trials), self.sender.batch_size)
        self.assertTrue(all(t in [0, 1] for t in trials))

    @patch('random.sample')
    def test_update_failure_indexes(self, mock_random_sample):
        mock_random_sample.return_value = [1, 2, 3]
        self.sender.update_failure_indexes()
        self.assertEqual(self.sender.failure_indexes, {1, 2, 3})
    
    @patch('time.sleep', return_value=None) 
    @patch('random.gauss', return_value=0.8)
    def test_sleep_until_random_mean_time(self, mock_gauss, mock_sleep):
        payload = {'id': 1, 'number': '1231241241'}
        self.sender.failure_indexes = {2}
        self.sender.message_index = 1
        body = json.dumps(payload)
        ch = Mock()
        method = Mock()
        
        self.sender.send_sms(ch, method, None, body)
        self.assertEqual(self.mock_logger.info.call_args[1]['extra']['process_time'], 0.8)

    @patch('time.sleep', return_value=None)
    @patch('random.gauss', return_value=1.0)
    def test_send_sms_success(self, mock_gauss, mock_sleep):
        payload = {'id': 1, 'number': '1231241241'}
        self.sender.failure_indexes = {2}
        self.sender.message_index = 1
        
        body = json.dumps(payload)
        ch = Mock()
        method = Mock()
        
        self.sender.send_sms(ch, method, None, body)
        
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)
        self.mock_logger.info.assert_called_once_with(
            f'SENDER: Successfully sent the message to the number {payload["number"]} id: {payload["id"]}',
            extra={'message_id': payload['id'], 'process_time': 1.0, 'logger': 'Sender', 'status': 'MSG-SENT'}
        )

    @patch('time.sleep', return_value=None)
    @patch('random.gauss', return_value=0.2)
    def test_send_sms_failure(self, mock_gauss, mock_sleep):
        payload = {'id': 1, 'number': '1231241241'}
        body = json.dumps(payload)
        ch = Mock()
        method = Mock()
        self.sender.message_index = 1
        self.sender.failure_indexes = {1}
        self.sender.send_sms(ch, method, None, body)
        #this line assures that the message is enqueued back into the queue on failure
        ch.basic_nack.assert_called_once_with(delivery_tag=method.delivery_tag, requeue=True)
        self.mock_logger.info.assert_called_once_with(
            f'SENDER: Failed to send the message to the number {payload["number"]} id: {payload["id"]}',
            extra={'message_id': payload['id'], 'process_time': 0.2, 'logger': 'Sender', 'status': 'MSG-FAILED'}
        )
        
    
    @patch('time.sleep', return_value=None)
    @patch('random.gauss', return_value=0.2)
    def test_failure_rate_is_achieved(self, mock_gauss, mock_sleep):
        for i in range(self.sender.batch_size):
            payload = {'id': i+1, 'number': '1231241241'}
            body = json.dumps(payload)
            ch = Mock()
            method = Mock()            
            self.sender.send_sms(ch, method, None, body)
        fm = self.sender.failure_count
        self.assertEqual(self.sender.fc, fm)
        self.assertEqual(self.sender.sc,  self.sender.batch_size- fm)
        

if __name__ == '__main__':
    unittest.main()
