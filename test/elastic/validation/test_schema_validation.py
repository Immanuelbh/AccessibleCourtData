import os
import unittest
from hcva.elastic.validation.schema_validation import validate_schema

ELASTIC_MOCK_SUCCESS = os.path.join(os.path.dirname(__file__), 'elastic_data_mock_success.json')
ELASTIC_MOCK_FAIL = os.path.join(os.path.dirname(__file__), 'elastic_data_mock_fail.json')


class TestSchemaValidation(unittest.TestCase):

    def test_validate_schema_success(self):
        print('test validate schema success')
        res = validate_schema(ELASTIC_MOCK_SUCCESS)
        self.assertEqual(res, True)

    def test_validate_schema_fail(self):
        print('test validate schema fail')
        res = validate_schema(ELASTIC_MOCK_FAIL)
        self.assertEqual(res, False)
