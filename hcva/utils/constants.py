import os

# database
DB_NAME = 'hcva'
DB_URI = os.environ.get('MONGO_DB_URI') or f'mongodb://root:example@localhost:27017/{DB_NAME}?authSource=admin'

# elastic
ELASTIC_INDEX = 'test_index_1'

# mongo
COLLECTION_NAME = 'v3'

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
# elastic
ELASTIC_SUCCESS_DIR = OUTPUT_DIR + 'elastic/success_upload/'
ELASTIC_FAILED_VALIDATION_DIR = OUTPUT_DIR + 'elastic/failed_validation/'
ELASTIC_FAILED_UPLOAD_DIR = OUTPUT_DIR + 'elastic/failed_upload/'
