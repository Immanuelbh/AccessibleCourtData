from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from hcva.utils.date import init_dates, get_gap_dates
from hcva.utils.logger import Logger
from hcva.utils import constants


def create_docs(dates):
    docs = []
    for date in dates:
        doc = {
            'date': date,
            'status': 'available'
        }
        docs.append(doc)

    return docs


class Database:
    logger = Logger('db.log', constants.LOG_DIR).get_logger()
    collection = None

    def __init__(self):
        self.client = MongoClient(constants.DB_URI)
        self.get_connection()

    def get_connection(self):
        try:
            self.logger.info('db trying to connect...')
            connection = self.client
            self.logger.info('db connected')
        except ServerSelectionTimeoutError as err:
            message = 'db connection Timeout - check for if this machine ip is on whitelist'
            if self.logger is not None:
                self.logger.exception(f'{message} {err}')
            else:
                print(f'{message} {err}')
            connection = None
        return connection

    def get_db(self, name):
        self.logger.info(f'db trying to get db: {name}')
        db = self.client[name]
        self.logger.info(f'got db: {db.name}')
        return db

    def get_collection(self, db, collection_name):
        collection = db.get_collection(collection_name)
        self.logger.info(f'got collection: {collection_name}')
        return collection

    # date format: %d-%m-%Y
    def update_status(self, date, status):
        self.logger.info(f'setting {date} status to: {status}')
        self.collection.update_one({
            'date': date
        }, {
            '$set': {
                'status': status
            }
        })

    def create_date(self, date):
        self.collection.insert({
            'date': date,
            'status': 'available'
        })

    def get_dates(self):
        res = self.collection.find({
            'status': {'$in': ['available', 'error']}
        }, {
            '_id': 0,
            'status': 0
        })
        self.logger.info(f'found {res.count()} dates')
        return res

    def get_latest_db_date(self):
        latest_db_date = list(self.collection.find().sort('_id', -1).limit(1))
        date = latest_db_date[0]['date']
        return date

    def insert_new_dates(self, dates):
        docs = create_docs(dates)
        self.collection.insert_many(docs)

    def init_collection(self, db_name, collection_name):
        self.collection = self.client[db_name].get_collection(collection_name)
        if self.collection.count() == 0:
            self.logger.info(f'initializing collection: {collection_name}')
            self.insert_new_dates(init_dates())
            self.logger.info(f'collection @{collection_name} initialized')
        else:
            self.logger.info(f'checking gap dates in collection: {collection_name}')
            latest_db_date = self.get_latest_db_date()
            gap_dates = get_gap_dates(latest_db_date)
            if len(gap_dates) != 0:
                self.logger.info(f'updating dates in collection: {collection_name}')
                self.insert_new_dates(gap_dates)
                self.logger.info(f'collection @{collection_name} was updated')
            else:
                self.logger.info(f'collection @{collection_name} is up to date')
        return self.collection
