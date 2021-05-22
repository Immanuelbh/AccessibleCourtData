from os import path, curdir
from datetime import datetime, timedelta
from threading import Lock
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from hcva.utils.date import init_dates
from hcva.utils.logger import Logger

DB_URI = "mongodb://root:example@localhost:27017/SupremeCourt?authSource=admin"
# DB_URI = os.environ.get('MONGO_DB_URI')
SATURDAY = 6  # according to weekdays by datetime (monday=0, ...)
DB_NAME = 'hcva'
ROOT_DIR = path.abspath(curdir)
log_path = ROOT_DIR + f'/logs/{DB_NAME}/'


class Database:
    logger = Logger('db.log', log_path).getLogger()
    collection = None

    def __init__(self):
        self.current = self.day_before(datetime.today())  # yesterday
        self.client = MongoClient(DB_URI)
        self.get_connection()

    def get_connection(self):
        try:
            self.logger.info('db trying to connect...')
            connection = self.client
            self.logger.info('db connected')
        except ServerSelectionTimeoutError as err:
            message = 'db connection Timeout - check for if this machine ip is on whitelist'
            if self.logger is not None:
                self.logger.exception(message + err)
            else:
                print(message + err)
            connection = None
        return connection

    def get_db(self, name):
        self.log(f'db trying to get db: {name}')
        db = self.client[name]
        self.log(f'got db: {db.name}')
        return db

    def get_collection(self, db, collection_name):
        collection = db.get_collection(collection_name)
        self.log(f'got collection: {collection_name}')
        return collection

    def log(self, message):
        if self.logger is not None:
            self.logger.info(message)

    def get_date(self):
        self.logger.info(f'getting next available date')
        while self.date_used(self.current.strftime("%d-%m-%Y")):
            self.logger.info(f'date exists')
            self.current = self.day_before(self.current)

        self.logger.info(f'date is available')
        self.update_status(self.current.strftime("%d-%m-%Y"), 'in progress')
        return self.current.strftime("%d-%m-%Y")

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

    def date_used(self, date):
        self.logger.info(f'trying {date}')
        res = self.collection.find_one({  # TODO same date gets tested twice if newly created
            'date': date,
        })
        if res:
            return res['status'] == 'in progress'

        self.create_date(date)
        return False

    def create_date(self, date):
        self.collection.insert({
            'date': date,
            'status': 'available'
        })

    def day_before(self, date):
        prev = date - timedelta(1)
        if prev.weekday() == SATURDAY:
            prev = prev - timedelta(1)

        return prev

    def get_dates(self):
        res = self.collection.find({
            'status': 'available'
        }, {
            '_id': 0,
            'status': 0
        })
        print(f'found {res.count()}')
        return res

    def create_docs(self):
        docs = []
        dates = init_dates()
        for date in dates:
            doc = {
                'date': date,
                'status': 'available'
            }
            docs.append(doc)

        return docs

    def create_collection(self):
        docs = self.create_docs()
        self.collection.insert_many(docs)

    def init_collection(self, db_name, collection_name):
        self.collection = self.client[db_name].get_collection(collection_name)
        if self.collection.count() == 0:
            self.logger.info(f'initializing collection: {collection_name}')
            self.create_collection()
            # self.collection.insert({
            #     'date': self.current.strftime('%d-%m-%Y'),
            #     'status': 'available'
            # })
        self.logger.info(f'collection @{collection_name} initialized')

        return self.collection
