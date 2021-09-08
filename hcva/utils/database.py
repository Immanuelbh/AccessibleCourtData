from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from hcva.utils.case_utils import get_case_dates
from hcva.utils.date import init_dates, get_gap_dates
from hcva.utils.logger import Logger
from hcva.utils import constants
from enum import Enum
logger = Logger('db.log', constants.LOG_DIR).get_logger()


class StatusType(Enum):
    AVAILABLE = 'available'
    DONE = 'done'
    ERROR = 'error'


def sync_existing_cases():
    path = constants.CASES_PATH
    if path == 'None' or path is None:
        logger.error('path is empty, please add the cases dir to CASES_PATH')
    else:
        dates = get_case_dates(path)
        db = Database()
        db.init_collection()
        for date in dates:
            db.update_status(date, StatusType.DONE)


def create_docs(dates):
    docs = []
    for date in dates:
        doc = {
            'date': date,
            'status': StatusType.AVAILABLE.value
        }
        docs.append(doc)

    return docs


class Database:

    def __init__(self):
        self.client = MongoClient(constants.DB_URI)
        self.db_name = constants.DB_NAME
        self.collection_name = constants.COLLECTION_NAME
        self.get_connection()
        self.collection = self.client[self.db_name].get_collection(self.collection_name)

    def get_connection(self):
        try:
            logger.info('db trying to connect...')
            connection = self.client
            logger.info('db connected')
        except ServerSelectionTimeoutError as err:
            message = 'db connection Timeout - check for if this machine ip is on whitelist'
            if logger is not None:
                logger.exception(f'{message} {err}')
            else:
                print(f'{message} {err}')
            connection = None
        return connection

    def get_db(self, name):
        logger.info(f'db trying to get db: {name}')
        db = self.client[name]
        logger.info(f'got db: {db.name}')
        return db

    def get_collection(self, db, collection_name):
        collection = db.get_collection(collection_name)
        logger.info(f'got collection: {collection_name}')
        return collection

    # date format: %d-%m-%Y
    def update_status(self, date, status):
        logger.info(f'setting {date} status to: {status.value}')
        self.collection.update_one({
            'date': date
        }, {
            '$set': {
                'status': status.value
            }
        })

    def get_dates(self):
        res = self.collection.find({
            'status': {'$in': [StatusType.AVAILABLE.value, StatusType.ERROR.value]}
        }, {
            '_id': 0,
            'status': 0
        })
        logger.info(f'found {res.count()} dates')
        return res

    def get_latest_db_date(self):
        latest_db_date = list(self.collection.find().sort('_id', -1).limit(1))
        date = latest_db_date[0]['date']
        return date

    def insert_new_dates(self, dates):
        docs = create_docs(dates)
        self.collection.insert_many(docs)

    def init_collection(self):
        if self.collection.count() == 0:
            logger.info(f'initializing collection: {self.collection_name}')
            self.insert_new_dates(init_dates())
            logger.info(f'collection @{self.collection_name} initialized')
        else:
            logger.info(f'checking gap dates in collection: {self.collection_name}')
            latest_db_date = self.get_latest_db_date()
            gap_dates = get_gap_dates(latest_db_date)
            if len(gap_dates) != 0:
                logger.info(f'updating dates in collection: {self.collection_name}')
                self.insert_new_dates(gap_dates)
                logger.info(f'collection @{self.collection_name} was updated')
            else:
                logger.info(f'collection @{self.collection_name} is up to date')
        return self.collection
