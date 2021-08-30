import os
import platform

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# database
DB_NAME = 'hcva'
DB_URI = os.getenv('MONGO_DB_URI', f'mongodb://root:example@localhost:27017/{DB_NAME}?authSource=admin')

# crawler
BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chrome')
OS_TYPE = os.getenv('OS_TYPE', platform.system())
HEADLESS = os.getenv('HEADLESS', 'true')
NUM_OF_CRAWLERS = os.getenv('NUM_OF_CRAWLERS', '2')

# elastic
ELASTIC_INDEX_NAME = os.getenv('ELASTIC_INDEX_NAME', 'default_index')

# mongo
COLLECTION_NAME = 'dates'

# directories #
ROOT_DIR = os.path.abspath(os.curdir)
LOG_DIR = ROOT_DIR + f'/logs/{DB_NAME}/'
OUTPUT_DIR = ROOT_DIR + '/cases/'
# scraper
SCRAPED_DIR = OUTPUT_DIR + 'scraped/'
# parser
PARSED_SUCCESS_DIR = OUTPUT_DIR + 'parsed/success/'
PARSED_FAILED_DIR = OUTPUT_DIR + 'parsed/failed_parse/'
PARSED_FAILED_VALIDATION_DIR = OUTPUT_DIR + 'parsed/failed_validation/'
# normalizer
NORMALIZED_SUCCESS_DIR = OUTPUT_DIR + 'normalized/success/'
NORMALIZED_FAILED_DIR = OUTPUT_DIR + 'normalized/failed/'
# classifier
CLASSIFIED_SUCCESS_DIR = OUTPUT_DIR + 'classified/success/'
CLASSIFIED_FAILED_DIR = OUTPUT_DIR + 'classified/failed/'
CLASSIFIERS = ROOT_DIR + 'models/'
# elastic
ELASTIC_SUCCESS_DIR = OUTPUT_DIR + 'elastic/success_upload/'
ELASTIC_FAILED_VALIDATION_DIR = OUTPUT_DIR + 'elastic/failed_validation/'
ELASTIC_FAILED_UPLOAD_DIR = OUTPUT_DIR + 'elastic/failed_upload/'
ELASTIC_INDEX_PATH = ROOT_DIR + '/hcva/elastic/index/index_v7.json'
