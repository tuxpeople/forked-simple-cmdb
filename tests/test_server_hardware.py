"""Run with python -m unittest discover -s tests -p test_server_hardware.py."""
import importlib
import os
import tempfile
import unittest
from unittest.mock import patch


class ServerHardwareTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        environment = patch.dict(os.environ, {
            'CMDB_DB': os.path.join(directory.name, 'cmdb.db'),
            'API_TOKENS': '',
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.module = importlib.reload(importlib.import_module('app'))
        self.client = self.module.app.test_client()
        with self.module.get_db() as connection:
            self.server_id = connection.execute(
                'INSERT INTO servers (hostname, cpu_cores, memory_gb) VALUES (?, ?, ?)',
                ('hardware-test', 10, 24.0),
            ).lastrowid
        self.url = f'/api/server/{self.server_id}'

    def hardware(self):
        connection = self.module.get_db()
        try:
            row = connection.execute(
                'SELECT cpu_cores, memory_gb FROM servers WHERE id = ?',
                (self.server_id,),
            ).fetchone()
            return tuple(row)
        finally:
            connection.close()

    def test_display_and_edit_inputs(self):
        response = self.client.get(f'/server/{self.server_id}')
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn('<th>CPU Cores</th>', page)
        self.assertIn('<td>10</td>', page)
        self.assertIn('<th>Memory (GB)</th>', page)
        self.assertIn('<td>24.0</td>', page)
        self.assertIn('id="edit_cpu_cores" min="0" step="1" value="10"', page)
        self.assertIn('id="edit_memory_gb" min="0" step="any" value="24.0"', page)

    def test_update_preserve_and_clear(self):
        self.assertEqual(self.client.put(self.url, json={'cpu_cores': 12, 'memory_gb': 32.5}).status_code, 200)
        self.assertEqual(self.hardware(), (12, 32.5))
        self.assertEqual(self.client.put(self.url, json={'owner': 'platform'}).status_code, 200)
        self.assertEqual(self.hardware(), (12, 32.5))
        self.assertEqual(self.client.put(self.url, json={'cpu_cores': None, 'memory_gb': None}).status_code, 200)
        self.assertEqual(self.hardware(), (None, None))
        page = self.client.get(f'/server/{self.server_id}').get_data(as_text=True)
        self.assertIn('id="edit_cpu_cores" min="0" step="1" value=""', page)
        self.assertIn('id="edit_memory_gb" min="0" step="any" value=""', page)

    def test_zero_is_displayed(self):
        self.assertEqual(self.client.put(self.url, json={'cpu_cores': 0, 'memory_gb': 0}).status_code, 200)
        page = self.client.get(f'/server/{self.server_id}').get_data(as_text=True)
        self.assertIn('id="edit_cpu_cores" min="0" step="1" value="0"', page)
        self.assertIn('<td>0.0</td>', page)

    def test_invalid_values_do_not_modify_server(self):
        for field, values in {
            'cpu_cores': [-1, 1.5, True, 'four'],
            'memory_gb': [-1, True, 'lots', float('inf'), float('nan')],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    response = self.client.put(self.url, json={field: value})
                    self.assertEqual(response.status_code, 400)
                    self.assertFalse(response.get_json()['success'])
                    self.assertEqual(self.hardware(), (10, 24.0))
