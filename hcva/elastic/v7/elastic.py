from hcva.elastic.builder import *
from hcva.elastic.json_validator import *
from hcva.utils.logger import Logger
from hcva.utils.time import call_sleep
from hcva.utils.path import get_path, sep, get_all_files
from elasticsearch import Elasticsearch
import os
import shutil
import sys
sys.path.insert(1, '../../..')

DB_NAME = 'hcva'
ELASTIC_INDEX = 'test_index_1'
ROOT_DIR = os.path.abspath(os.curdir)
LOG_DIR = ROOT_DIR + f'/logs/{DB_NAME}/'
PARSED_DIR = ROOT_DIR + "/cases/parsed/success/"
SUCCESS_DIR = "success_upload/"
FAILED_VALIDATION_DIR = "failed_validation"
FAILED_UPLOAD_DIR = "failed_upload"


def get_source(file_name):
    source = ROOT_DIR + PARSED_DIR + file_name
    return source


def get_destination(directory):
    destination = ROOT_DIR + "/cases/elastic" + directory
    os.makedirs(destination, exist_ok=True)
    return destination


def flush(files, directory):
    destination = get_destination(directory)
    for file in files:
        source = get_source(file)
        shutil.move(source, destination)


class Elastic:
    failed_upload = []
    failed_validation = []
    success_upload = []
    index_exists = False

    def __init__(self, logger):
        self._logger = logger
        self.elastic = Elasticsearch()

    def init_index(self):
        self._logger.info("initializing elasticsearch index :: {}".format(ELASTIC_INDEX))
        if self.elastic.indices.exists(index=ELASTIC_INDEX):
            self._logger.info("{} index exists".format(ELASTIC_INDEX))
            return True
        else:
            self._logger.info("creating index :: {} ".format(ELASTIC_INDEX))
            response = self.elastic.indices.create(index=ELASTIC_INDEX)
            if response:
                return response['acknowledged']
            else:
                self._logger.error("Error creating index")

    def run(self):
        products = get_all_files(folder_name=ROOT_DIR + PARSED_DIR)
        self.index_with_schema(products)

    def flush_all(self):
        self._logger.info("flushing folder")
        flush(self.success_upload, SUCCESS_DIR)
        flush(self.failed_upload, FAILED_UPLOAD_DIR)
        flush(self.failed_validation, FAILED_VALIDATION_DIR)
        self._logger.info("all files flushed")

    def index_with_schema(self, products):
        for product in products:
            file_name = os.path.basename(product)
            self._logger.info("trying to validate {}".format(file_name))
            if validate_v1(dataFile=product):
                self._logger.info("file is valid")
                id, data = self.extract_data(product)
                res = self.upload(id, data)
                if res:
                    self.success_upload.append(file_name)
                else:
                    self._logger.info("adding file to failed list")
                    self.failed_upload.append(file_name)
                    # TODO add retry
            else:
                self._logger.info("file is not valid")
                self.failed_validation.append(file_name)

    def extract_data(self, product):
        self._logger.info("extracting data from file")
        with open(product, encoding='utf-8') as json_file:
            try:
                json_data = json.load(json_file)
                self._logger.info("file loaded successfully")
                json_id = json_data['Doc Details']['מספר הליך']  # Take procedure number from json file
                elasticsearch_id = build_elasticsearch_id(json_id=json_id)
                return elasticsearch_id, json_data
            except:
                self._logger.info("error while trying to load file")
                return None, None

    def upload(self, id, data):
        self._logger.info("trying to upload file to elasticsearch")
        res = self.elastic.index(index=ELASTIC_INDEX, id=id, body=data)
        self._logger.info("file {}".format(res['result']))
        return res


def main():
    logger = Logger('elasticsearch.log', get_path(n=2) + f'logs{sep}').get_logger()
    elastic = Elastic(logger)
    index_created = elastic.init_index()
    if index_created:
        logger.info(f"{ELASTIC_INDEX} index created successfully")
        while True:
            elastic.run()
            elastic.flush_all()
            call_sleep(logger=logger, minutes=10)


if __name__ == '__main__':
    main()
