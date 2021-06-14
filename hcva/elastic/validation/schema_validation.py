import sys
import json
import jsonschema
from hcva.utils import constants
from hcva.elastic.v5.relative_path import get_path

sys.path.insert(1, '../../..')

SCHEMA = constants.ROOT_DIR + '/hcva/elastic/validation/schema/schema_v7.json'
DEFAULT_SCHEMA = get_path('schema/schema_v7.json')


def load_data(data):
    with open(data, encoding='utf-8') as data_to_elastic:
        return json.load(data_to_elastic)


def validate_schema(data_file):
    try:
        data = load_data(data_file)
        schema = load_data(SCHEMA)
        return bool(jsonschema.validate(data, schema) is None)
    except:
        print('failed to open files')
        return False


def validate_v2(data_object, schema_file=DEFAULT_SCHEMA):
    with open(schema_file, encoding='utf-8') as json_schema:
        schema = json.load(json_schema)
    return bool(jsonschema.validate(data_object, schema) is None)
