import glob
import shutil

from time import sleep
from scripts.builder import *
from scripts.Moving import Moving
from scripts.json_validator import *
from ILCourtScraper.Extra.logger import Logger
from ILCourtScraper.Extra.time import callSleep
from ILCourtScraper.Extra.path import getPath, sep
from elasticsearch import Elasticsearch
import sys

sys.path.insert(1, './..')

HEADERS = {"Content-Type": "application/json"}
RULING_INDEX = 'supreme_court_verdicts'
HANDLED_JSON_PRODUCTS_PATH = "products/handled_json_products"
INDEXES_FILE_LOCATION = "products/indexes_7_10_2.txt"
NUMBER_OF_REPETITIONS_IN_CASE_OF_FAILURE = 5
THE_AMOUNT_OF_DELIVERABLES_TO_SEND_EACH_TIME = 100
DELAY_TIME_BETWEEN_ONE_REQUEST_AND_ANOTHER = 3  # In seconds
GET_REQUEST = "GET"
POST_REQUEST = "POST"
PUT_REQUEST = "PUT"
#
TEST_INDEX = 'test_index_1'
ROOT_DIR = os.path.abspath(os.curdir)
HANDLED_DIR = "/products/handled_json_products/"


class Elastic_7_10_2:
    _logger = None
    _moving = None
    _schema = None
    _counter = None
    _elk_id = None
    _elasticsearch_indexes_list = None
    elastic = None
    failed_upload = None
    failed_validation = None
    success_upload = None

    def __init__(self, logger, json_schema=True, the_amount_of_delivery=THE_AMOUNT_OF_DELIVERABLES_TO_SEND_EACH_TIME):
        self.index_exists = False
        self._logger = logger
        self._moving = Moving()
        self._schema = json_schema
        self._counter = the_amount_of_delivery
        self._elasticsearch_indexes_list = list()
        self.elastic = Elasticsearch()
        self.failed_upload = []
        self.failed_validation = []
        self.success_upload = []

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
        directory = get_path(folder=HANDLED_JSON_PRODUCTS_PATH)
        products = self.get_files_from_folder(folder_name=directory)
        self.index_with_schema(products)

    def flush(self):
        self.flush_files(self.success_upload, "elastic/success_upload")
        self.flush_files(self.failed_upload, "elastic/failed_upload")
        self.flush_files(self.failed_validation, "elastic/failed_validation")

    def flush_files(self, files, directory):
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

    def write_indexes_to_file(self):
        path = get_path(folder=INDEXES_FILE_LOCATION)
        list_of_indexes = self._elasticsearch_indexes_list

        # first append all indexes to file
        with open(path, "a") as file:
            for line in list_of_indexes:
                file.write(line + '\n')
            file.close()

        # second get all lines from file
        with open(path, 'r') as file:
            lines = file.readlines()
            file.close()

        # remove spaces
        lines = [line.replace(' ', '') for line in lines]
        lines.sort()

        # finally, write lines in the file
        with open(path, 'w') as file:
            file.writelines(lines)
            file.close()
        self._elasticsearch_indexes_list = list()

    def check_status_code(self, status, type_of_request):
        self._logger.info("{type_of_request}: The Elastic file revenue status code is {status} ".format(
            type_of_request=type_of_request, status=status.status_code))
        if 200 <= status.status_code <= 299:
            return True
        return False

    def get_files_from_folder(self, folder_name, file_type='json'):
        return [f for f in glob.glob(folder_name + os.sep + "*." + file_type)]

    def comparison_data(self, data_to_post, data_from_elastic):
        self._logger.info("Starting to compare")
        result1 = self.checks_if_identical(data_to_post['Doc Details']['מספר הליך'],
                                           data_from_elastic['_source']['Doc Details']['מספר הליך'])
        self._logger.info("Result 1: {0}".format(result1))
        result2 = self.checks_if_identical(data_to_post['Doc Details']['לפני'],
                                           data_from_elastic['_source']['Doc Details']['לפני'])
        self._logger.info("Result 2: {0}".format(result2))
        result3 = self.checks_if_identical(data_to_post['Doc Details']['העותר'],
                                           data_from_elastic['_source']['Doc Details']['העותר'])
        self._logger.info("Result 3: {0}".format(result3))
        result4 = self.checks_if_identical(data_to_post['Doc Details']['המשיב'],
                                           data_from_elastic['_source']['Doc Details']['המשיב'])
        self._logger.info("Result 4: {0}".format(result4))
        result5 = self.checks_if_identical(data_to_post['Doc Details']['סוג מסמך'],
                                           data_from_elastic['_source']['Doc Details']['סוג מסמך'])
        self._logger.info("Result 5: {0}".format(result5))
        result6 = self.checks_if_identical(data_to_post['Doc Details']['סיכום'],
                                           data_from_elastic['_source']['Doc Details']['סיכום'])
        self._logger.info("Result 6: {0}".format(result6))
        self._logger.info("The comparison is over and starts to calculate a result")
        total_result = result1 and result2 and result3 and result4 and result4 and result5 and result6
        return total_result

    def checks_if_identical(self, data_to_post, data_from_elastic):
        if data_to_post == data_from_elastic or data_from_elastic == "null":
            return True
        return False

    def upload(self, id, data):
        self._logger.info("trying to upload file to elasticsearch")
        res = self.elastic.index(index=TEST_INDEX, id=id, body=data)
        self._logger.info("file {}".format(res['result']))
        return res

    def handler(self, file_to_read):
        with open(file_to_read, encoding='utf-8') as json_file:
            try:
                json_data = json.load(json_file)  # Load json file
                self._logger.info("The file was successfully loaded")
                id_from_json = json_data['Doc Details']['מספר הליך']  # Take procedure number from json file
                self._logger.info("The procedure number is taken from the file for further treatment")

                elasticsearch_id = build_elasticsearch_id(json_id=id_from_json)  # Build id to get and post request
                self._logger.info("ID successfully built")
                get_url = build_get_request_7_10_2(index=RULING_INDEX, id=elasticsearch_id)  # Build get request url
                self._logger.info("Successfully built get request URL")
                self.sleep_now()
                get_result = self.send_get_request(url=get_url)  # Send get request
                self._logger.info("GET request sent")
                data_from_elastic = get_result.json()  # Convert result from get request to json format

                if self.check_status_code(get_result, GET_REQUEST) is False and data_from_elastic['found'] is False:
                    # Build post request url and data
                    post_url, post_data = build_post_request_7_10_2(json_file=json_data, index=RULING_INDEX,
                                                                    id=elasticsearch_id)
                    self._logger.info("Successfully built post request URL and data")
                    self.sleep_now()
                    post_status = self.sent_post_request(post_url, post_data)  # Do post request and get post status
                    self._logger.info("POST request sent")
                    return self.check_status_code(post_status,
                                                  POST_REQUEST), elasticsearch_id  # Check type of status code and return

                while self.check_status_code(get_result, GET_REQUEST) and data_from_elastic['found'] is True:
                    the_result_of_the_comparison = self.comparison_data(data_to_post=json_data,
                                                                        data_from_elastic=data_from_elastic)
                    self._logger.info(
                        "The result of comparison is: {result} ".format(result=the_result_of_the_comparison))
                    if the_result_of_the_comparison:
                        post_url, post_data = build_post_request_7_10_2(json_file=json_data, index=RULING_INDEX,
                                                                        id=elasticsearch_id)
                        self.sleep_now()
                        post_status = self.sent_post_request(post_url, post_data)  # Do post request and get post status
                        self._logger.info("POST request sent")
                        return self.check_status_code(post_status,
                                                      POST_REQUEST), elasticsearch_id  # Check type of status code and return
                    else:
                        elasticsearch_id = rebuilding_id(elasticsearch_id)
                        self._logger.info("ID successfully rebuild")
                        get_url = build_get_request_7_10_2(index=RULING_INDEX, id=elasticsearch_id)
                        self._logger.info("Successfully built get request URL")
                        self.sleep_now()
                        get_result = self.send_get_request(get_url)
                        self._logger.info("GET request sent")
                        data_from_elastic = get_result.json()

                if self.check_status_code(get_result, GET_REQUEST) is False and data_from_elastic['found'] is False:
                    post_url, post_data = build_post_request_7_10_2(json_file=json_data, index=RULING_INDEX,
                                                                    id=elasticsearch_id)
                    self._logger.info("Successfully built post request URL and data")
                    self.sleep_now()
                    post_status = self.sent_post_request(post_url, post_data)  # Do post request and get post status
                    self._logger.info("POST request sent")
                    return self.check_status_code(post_status,
                                                  POST_REQUEST), elasticsearch_id  # Check type of status code and return
                return False, None
            except:
                self._logger.info("There was an error event")
                return False, None

    def sleep_now(self):
        self._logger.info("The system is delayed for {0} seconds".format(DELAY_TIME_BETWEEN_ONE_REQUEST_AND_ANOTHER))
        sleep(DELAY_TIME_BETWEEN_ONE_REQUEST_AND_ANOTHER)
        self._logger.info("The delay is over")


def main():
    logger = Logger('elasticsearch.log', getPath(N=2) + f'logs{sep}').getLogger()
    elastic = Elastic_7_10_2(logger)
    index_created = elastic.init_index()
    if index_created:
        print("{} index created successfully".format(TEST_INDEX))
        while True:
            elastic.run()
            elastic.flush()
            callSleep(logger=logger, minutes=10) # after finished with all the files, wait - hours * minutes * seconds


if __name__ == '__main__':
    main()
