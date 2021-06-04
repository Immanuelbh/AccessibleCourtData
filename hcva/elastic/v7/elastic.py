from hcva.elastic.validation.schema_validation import *
from hcva.utils import constants
from hcva.utils.json import save_data, read_data
from hcva.utils.logger import Logger
from hcva.utils.time import call_sleep
from hcva.utils.path import get_all_files, create_dir
from elasticsearch import Elasticsearch
import os
import sys
sys.path.insert(1, '../../..')


def save(files, directory):
    for file in files:
        d = read_data(file, constants.PARSED_SUCCESS_DIR)
        save_data(d, file, directory)


def build_elasticsearch_id(json_id):
    initial_id = build_an_initial_id(json_id)
    elasticsearch_id = build_first_continuous_number(initial_id)
    return elasticsearch_id


def build_an_initial_id(json_id):
    initial_id = json_id.split(" ")[1]  # Acceptance only of procedure number without court type
    initial_id = initial_id.replace("/", "-")  # Change the procedure number format from 'xxxx/xx' to 'xxxx-xx'
    return initial_id


def build_first_continuous_number(initial_id):
    first_continuous_number = 1  # Set an initial runner number to a procedure number
    elasticsearch_id = f"{initial_id}-{first_continuous_number}"
    return elasticsearch_id


class Elastic:
    failed_upload = []
    failed_validation = []
    success_upload = []
    index_exists = False

    def __init__(self, logger):
        self._logger = logger
        self.elastic = Elasticsearch()
        create_dir(constants.ELASTIC_SUCCESS_DIR)
        create_dir(constants.ELASTIC_FAILED_UPLOAD_DIR)
        create_dir(constants.ELASTIC_FAILED_VALIDATION_DIR)

    def init_index(self):
        self._logger.info(f"initializing elasticsearch index :: {constants.ELASTIC_INDEX}")
        if self.elastic.indices.exists(index=constants.ELASTIC_INDEX):
            self._logger.info(f"{constants.ELASTIC_INDEX} index exists")
            return True
        else:
            self._logger.info(f"creating index :: {constants.ELASTIC_INDEX} ")
            response = self.elastic.indices.create(index=constants.ELASTIC_INDEX)
            if response:
                return response['acknowledged']
            else:
                self._logger.error("Error creating index")

    def run(self):
        cases = get_all_files(folder_name=constants.PARSED_SUCCESS_DIR)
        self._logger.info(f'trying to upload {len(cases)} cases')
        self.push_cases(cases)

    def save_all(self):
        self._logger.info("saving results")
        save(self.success_upload, constants.ELASTIC_SUCCESS_DIR)
        save(self.failed_upload, constants.ELASTIC_FAILED_UPLOAD_DIR)
        save(self.failed_validation, constants.ELASTIC_FAILED_VALIDATION_DIR)
        self._logger.info("all files saved")

    def push_cases(self, cases):
        for case in cases:
            file_name = os.path.basename(case)
            self._logger.info(f'trying to validate {file_name}')
            if validate_schema(data_file=case):
                self._logger.info("file is valid")
                id_, data = self.extract_data(case)
                res = self.upload(id_, data)
                if res:
                    self._logger.info(f'{case} was uploaded to elasticsearch successfully')
                    self.success_upload.append(file_name)
                else:
                    self._logger.info("adding file to failed list")
                    self.failed_upload.append(file_name)
                    # TODO add retry
            else:
                self._logger.info("file is not valid")
                self.failed_validation.append(file_name)

    def extract_data(self, case):
        self._logger.info("extracting data from file")
        with open(case, encoding='utf-8') as json_file:
            try:
                json_data = json.load(json_file)
                self._logger.info("file loaded successfully")
                json_id = json_data['Doc Details']['מספר הליך']  # Take procedure number from json file
                elasticsearch_id = build_elasticsearch_id(json_id=json_id)
                return elasticsearch_id, json_data
            except:
                self._logger.info("error while trying to load file")
                return None, None

    def upload(self, id_, data):
        self._logger.info("trying to upload file to elasticsearch")
        res = self.elastic.index(index=constants.ELASTIC_INDEX, id=id_, body=data)
        self._logger.info(f"file {res['result']}")
        return res


def main():
    logger = Logger('elasticsearch.log', constants.LOG_DIR).get_logger()
    elastic = Elastic(logger)
    index_created = elastic.init_index()
    if index_created:
        logger.info(f"{constants.ELASTIC_INDEX} index created successfully")
        while True:
            elastic.run()
            elastic.save_all()
            call_sleep(logger=logger, minutes=10)


if __name__ == '__main__':
    main()
