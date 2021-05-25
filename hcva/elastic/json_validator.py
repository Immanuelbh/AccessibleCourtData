import sys
import jsonschema
import json
from hcva.elastic.v5.relative_path import get_path

sys.path.insert(1, '../..')

DEFAULT_SCHEMA = get_path('json_schema/json_schema.json')


def validate_v1(data_file, schema_file=DEFAULT_SCHEMA):
    try:
        with open(data_file, encoding='utf-8') as data_to_elastic:
            elastic_data = json.load(data_to_elastic)
        with open(schema_file, encoding='utf-8') as json_schema:
            schema = json.load(json_schema)
        if jsonschema.validate(elastic_data, schema) is None:
            return True
        else:
            return False
    except:
        return False


def validate_v2(data_object, schema_file=DEFAULT_SCHEMA):
    with open(schema_file, encoding='utf-8') as json_schema:
        schema = json.load(json_schema)
    if jsonschema.validate(data_object, schema) is None:
        return True
    else:
        return False
