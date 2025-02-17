import os
import sys
import json
import jsonschema
import logging
from elasticsearch import Elasticsearch, TransportError
from hcva.elastic.validation.schema_validation import validate_schema
from hcva.utils import constants
from hcva.utils.case_utils import get_all_files
from hcva.utils.json import save_data, read_data
from hcva.utils.logger import Logger
from hcva.utils.time import call_sleep
from hcva.utils.path import create_dir
logger = Logger('elastic_v7_main.log', constants.LOG_DIR, log_level=logging.INFO).get_logger()
SCHEMA = constants.ROOT_DIR + '/hcva/elastic/validation/schema/schema_v7.json'

sys.path.insert(1, '../../..')


def format_id(json_id):
    initial_id = json_id.split(" ")[1]  # Acceptance only of procedure number without court type
    initial_id = initial_id.replace("/", "-")  # Change the procedure number format from 'xxxx/xx' to 'xxxx-xx'
    return initial_id


def validate_schema(case_data):
    try:
        with open(SCHEMA, encoding='utf-8') as json_schema:
            schema = json.load(json_schema)
        return bool(jsonschema.validate(case_data, schema) is None)
    except Exception as e:
        logger.error(f'failed to open files, {e}')
        return False


def extract_id(case_data):
    json_id = case_data['Doc Details']['מספר הליך']
    return format_id(json_id)


def get_date(file_name):
    return file_name.split('__')[0]


def create_id(date, case_data):
    extracted_id = extract_id(case_data)
    return f'{extracted_id}-{date}'


class Elastic:
    index_exists = False

    def __init__(self):
        self._logger = logger
        self.elastic = Elasticsearch(timeout=30, max_retries=10, retry_on_timeout=True)
        create_dir(constants.ELASTIC_SUCCESS_DIR)
        create_dir(constants.ELASTIC_FAILED_UPLOAD_DIR)
        create_dir(constants.ELASTIC_FAILED_VALIDATION_DIR)

    def id_exists(self, id_):
        return self.elastic.exists(index=constants.ELASTIC_INDEX_NAME, id=id_, ignore=404)

    def init_index(self):
        self._logger.info(f"initializing elasticsearch index :: {constants.ELASTIC_INDEX_NAME}")
        index = read_data('', constants.ELASTIC_INDEX_PATH)
        if self.elastic.indices.exists(index=constants.ELASTIC_INDEX_NAME):
            return True
        else:
            response = self.elastic.indices.create(
                index=constants.ELASTIC_INDEX_NAME,
                body=index,
                ignore=400
            )
            if 'acknowledged' in response:
                if response['acknowledged']:
                    self._logger.info(f'index created: {response["index"]}')
                    return True
            elif 'error' in response:
                self._logger.error(f"ERROR: {response['error']['root_cause']}")
                self._logger.error(f"TYPE: {response['error']['type']}")
        return False

    def run(self):
        cases = get_all_files(folder_name=constants.CLASSIFIED_SUCCESS_DIR)
        self._logger.info(f'trying to upload {len(cases)} cases')
        self.push_cases(cases)

    def push_cases(self, cases):
        for case in cases:
            file_name = os.path.basename(case)
            self._logger.info(f'trying to validate {file_name}')
            case_data = self.get_case_data(case)
            if case_data and validate_schema(case_data):
                self._logger.info(f'file {file_name} is valid')
                date = get_date(file_name)
                id_ = create_id(date, case_data)
                if self.id_exists(id_) is False:
                    res = self.upload(id_, case_data)
                    if res:
                        self._logger.info(f'{file_name} was uploaded to elasticsearch successfully')
                        save_data(case_data, file_name, constants.ELASTIC_SUCCESS_DIR)
                    else:
                        self._logger.error(f'failed to upload file {file_name}')
                        save_data(case_data, file_name, constants.ELASTIC_FAILED_UPLOAD_DIR)
                else:
                    self._logger.info(f'{file_name} already exists in elasticsearch')
            else:
                self._logger.error(f'file {file_name} is not valid')
                save_data(case_data, file_name, constants.ELASTIC_FAILED_VALIDATION_DIR)

    def get_case_data(self, file_name):
        self._logger.info("getting case data from file")
        with open(file_name, encoding='utf-8') as json_file:
            try:
                json_data = json.load(json_file)
                self._logger.info("file loaded successfully")
                return json_data
            except Exception as e:
                self._logger.error(f"error while trying to load file, {e}")
                return None

    def upload(self, id_, data):
        self._logger.info("trying to upload file to elasticsearch")
        try:
            res = self.elastic.index(index=constants.ELASTIC_INDEX_NAME, id=id_, body=data)
        except TransportError as e:
            self._logger.error(e.info)
        self._logger.info(f"file {res['result']}")
        return res


def elastic():
    e = Elastic()
    index_created = e.init_index()
    if index_created:
        logger.info(f"{constants.ELASTIC_INDEX_NAME} index created successfully")
        while True:
            logger.info("elastic starting")
            e.run()
            logger.info("elastic has finished")
            call_sleep(logger=logger, days=1)

