"""Software-only contract: capture -> graph -> model -> alert -> recovery."""
import os
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

os.environ['MQTT_ENABLED'] = 'false'
os.environ['AUTO_DETECTION'] = 'false'
os.environ['RESPONSE_MODE'] = 'record'

from fastapi.testclient import TestClient
from app.database import connection
from app.main import app
from app.services import response_service
from app.services.firewall_service import firewall_command
from app.ml.train_dataset import train


class FlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        connection.DATABASE_PATH = Path(self.tmp.name) / 'guardian_test.db'
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.tmp.cleanup()

    def register(self, name, ip):
        response = self.client.post('/devices/register', json={
            'device_id': name, 'ip_address': ip, 'firmware_version': 'test'
        })
        self.assertEqual(response.status_code, 200, response.text)

    def observation(self, source, destination, port):
        response = self.client.post('/network/observations', json={
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_ip': source, 'destination_ip': destination,
            'protocol': 'TCP', 'packet_length': 300,
            'source_port': port, 'destination_port': 1883,
        })
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_persistent_graph_detection_and_record_mode(self):
        self.register('d1', '10.0.0.1')
        self.register('d2', '10.0.0.2')
        self.assertEqual(self.observation('10.0.0.1', '10.0.0.3', 1001)['device_id'], 'd1')
        self.observation('10.0.0.2', '10.0.0.3', 1002)
        graph = self.client.get('/graph').json()
        self.assertEqual(len(graph['nodes']), 2)
        self.assertEqual(len(graph['edges']), 1)
        scores = self.client.post('/detections/run')
        self.assertEqual(scores.status_code, 200, scores.text)
        self.assertEqual(len(scores.json()), 2)
        self.assertTrue(all(0 <= value['risk_score'] <= 1 for value in scores.json()))
        self.assertEqual(len(self.client.get('/detections').json()), 2)
        self.assertNotIn('isolated', [d['status'] for d in self.client.get('/devices').json()])
        self.assertEqual(len(self.client.get('/network/observations').json()), 2)
        self.assertEqual(self.client.post('/responses/d1/enforce').status_code, 400)

    def test_identity_comes_from_source_ip(self):
        self.register('real', '10.0.0.1')
        response = self.client.post('/network/observations', json={
            'timestamp': datetime.now(timezone.utc).isoformat(), 'source_ip': '10.0.0.1',
            'destination_ip': '10.0.0.2', 'protocol': 'TCP', 'packet_length': 100,
            'device_id': 'forged'
        })
        self.assertEqual(response.json()['device_id'], 'real')

    def test_firewall_uses_narrow_address_and_port(self):
        with patch('app.services.firewall_service.platform.system', return_value='Windows'):
            cmd = firewall_command('d1', '10.0.0.1', True)
        self.assertIn('remoteip=10.0.0.1', cmd)
        self.assertIn('localport=1883', cmd)
        with self.assertRaises(ValueError):
            firewall_command('x & calc', '10.0.0.1', True)

    def test_opt_in_firewall_and_recovery(self):
        self.register('device-1', '10.0.0.1')
        with patch.object(response_service, 'RESPONSE_MODE', 'firewall'), \
             patch('app.api.responses.RESPONSE_MODE', 'firewall'), \
             patch('app.services.recovery_service.RESPONSE_MODE', 'firewall'), \
             patch('app.services.response_service.set_mqtt_block', return_value='MQTT ingress blocked') as block, \
             patch('app.services.recovery_service.set_mqtt_block', return_value='MQTT ingress rule removed') as unblock:
            self.assertEqual(self.client.post('/responses/device-1/enforce').status_code, 200)
            self.assertEqual(self.client.get('/devices/device-1').json()['status'], 'isolated')
            block.assert_called_once_with('device-1', '10.0.0.1', True)
            self.assertEqual(self.client.post('/recovery/device-1').status_code, 200)
            unblock.assert_called_once_with('device-1', '10.0.0.1', False)
            self.assertEqual(self.client.get('/devices/device-1').json()['status'], 'online')
            self.assertEqual(len(self.client.get('/responses').json()), 2)

    def test_firewall_mode_does_not_auto_block_without_separate_switch(self):
        self.register('device-1', '10.0.0.1')
        from app.ml.detection_service import DetectionResult
        with patch.object(response_service, 'RESPONSE_MODE', 'firewall'), \
             patch.object(response_service, 'AUTO_FIREWALL', False), \
             patch('app.services.response_service.set_mqtt_block') as block:
            result = response_service.response_service.respond(
                DetectionResult('device-1', 0.99, 'SUSPICIOUS'), packet_count=100
            )
            self.assertEqual(result.action, 'ALERT')
            block.assert_not_called()

    def test_training_splits_by_capture_session(self):
        dataset = Path(self.tmp.name) / 'captures.jsonl'
        with dataset.open('w') as output:
            for i in range(8):
                label = int(i >= 4)
                features = [3, 600, 200, 3, 0, 3] if not label else [40, 12000, 300, 30, 10, 25]
                features[0] += i
                nodes = [{'device_id': f'd{i}', 'features': features, 'label': label}]
                if label:
                    nodes.append({'device_id': f'neighbor{i}', 'features': [4, 800, 200, 4, 0, 2], 'label': 0})
                output.write(json.dumps({'session': f's{i}', 'nodes': nodes, 'edges': []}) + '\n')
        report = train(dataset, Path(self.tmp.name) / 'model.pt', epochs=3)
        self.assertEqual(len(report['held_out_sessions']), 2)
        self.assertTrue((Path(self.tmp.name) / 'model.evaluation.json').exists())


if __name__ == '__main__':
    unittest.main()
