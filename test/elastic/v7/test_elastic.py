import unittest
import logging
from unittest.mock import patch, MagicMock
from hcva.elastic.v7.elastic import Elastic

logger = logging.getLogger("elastic")


class TestElastic(unittest.TestCase):

    def setUp(self):
        self.elastic_class = Elastic(logger)

    @patch.object(logger, "info", MagicMock())
    @patch('hcva.elastic.v7.elastic.read_data', return_value='value')
    def test_init_index_success(self, mock_read_data):
        print('test init_index - success')
        with patch.object(
                self.elastic_class.elastic.indices,
                'create',
                return_value={
                    'acknowledged': True,
                    'index': 'created'
                }
        ) as mock_method:
            res = self.elastic_class.init_index()
            self.assertEqual(res, True)

        mock_method.assert_called_once()
        mock_read_data.assert_called_once()

    @patch.object(logger, "info", MagicMock())
    @patch('hcva.elastic.v7.elastic.read_data', return_value='value')
    def test_init_index_failure(self, mock_read_data):
        print('test init_index - failure')
        with patch.object(
                self.elastic_class.elastic.indices,
                'create',
                return_value={
                    'error': 'test'
                }
        ) as mock_method:
            res = self.elastic_class.init_index()
            self.assertEqual(res, False)

        mock_method.assert_called_once()
        mock_read_data.assert_called_once()
