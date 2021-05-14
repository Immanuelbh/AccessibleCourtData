from scripts.builder import *
from scripts.json_validator import *
from ILCourtScraper.Extra.logger import Logger
from ILCourtScraper.Extra.time import callSleep
from ILCourtScraper.Extra.path import getPath, sep
from elasticsearch import Elasticsearch
import glob
import shutil
import sys
sys.path.insert(1, './..')

TEST_INDEX = 'test_index_1'
ROOT_DIR = os.path.abspath(os.curdir)
HANDLED_DIR = "/products/handled_json_products/"

class Elastic_7_10_2:
    failed_upload = []
    failed_validation = []
    success_upload = []
    index_exists = False

    def __init__(self, logger):
        self._logger = logger
        self.elastic = Elasticsearch()

    def init_index(self):
        self._logger.info("initializing elasticsearch index :: {}".format(TEST_INDEX))
        if self.elastic.indices.exists(index=TEST_INDEX):
            self._logger.info("{} index exists".format(TEST_INDEX))
            return True
        else:
            self._logger.info("creating index :: {} ".format(TEST_INDEX))
            response = self.elastic.indices.create(index=TEST_INDEX)
            if response:
                return response['acknowledged']
            else:
                self._logger.error("Error creating index")

    def run(self):
        directory = get_path(folder="products/handled_json_products")
        products = self.get_all_files(folder_name=directory)
        self.index_with_schema(products)

    def flush_all(self):
        self._logger.info("flushing folder")
        self.flush(self.success_upload, "elastic/success_upload")
        self.flush(self.failed_upload, "elastic/failed_upload")
        self.flush(self.failed_validation, "elastic/failed_validation")
        self._logger.info("all files flushed")

    def flush(self, files, directory):
        destination = self.get_destination(directory)
        for file in files:
            source = self.get_source(file)
            shutil.move(source, destination)

    def get_source(self, file_name):
        source = ROOT_DIR + HANDLED_DIR + file_name
        return source

    def get_destination(self, directory):
        destination = ROOT_DIR + "/products/" + directory
        os.makedirs(destination, exist_ok=True)
        return destination

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

    def get_all_files(self, folder_name):
        return [f for f in glob.glob(folder_name + "/*.json")]

    def upload(self, id, data):
        self._logger.info("trying to upload file to elasticsearch")
        res = self.elastic.index(index=TEST_INDEX, id=id, body=data)
        self._logger.info("file {}".format(res['result']))
        return res


def main():
    logger = Logger('elasticsearch.log', getPath(N=2) + f'logs{sep}').getLogger()
    elastic = Elastic_7_10_2(logger)
    index_created = elastic.init_index()
    if index_created:
        print("{} index created successfully".format(TEST_INDEX))
        while True:
            elastic.run()
            elastic.flush_all()
            callSleep(logger=logger, minutes=10)  # after finished with all the files, wait - hours * minutes * seconds


if __name__ == '__main__':
    main()
