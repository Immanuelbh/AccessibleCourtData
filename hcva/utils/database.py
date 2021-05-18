import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from hcva.utils.logger import Logger

DB_URI = "mongodb://root:example@localhost:27017/SupremeCourt?authSource=admin"
# DB_URI = os.environ.get('MONGO_DB_URI')
SATURDAY = 6  # according to weekdays by datetime (monday=0, ...)
DB_NAME = 'hcva'
ROOT_DIR = os.path.abspath(os.curdir)
log_path = ROOT_DIR + f'/logs/{DB_NAME}/'

class Database:
    logger = Logger('db.log', log_path).getLogger()
    current = datetime.today()  # .strftime('%d-%m-%Y')
    collection = None

    def __init__(self):
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

    def get_collection(self, db, collectionName):
        collection = db.get_collection(collectionName)
        self.log(f'got collection: {collectionName}')
        return collection

    def log(self, message):
        if self.logger is not None:
            self.logger.info(message)

    def get_date(self):  # TODO should be atomic
        self.logger.info(f'getting next available date')
        while self.date_used(self.current):
            self.logger.info(f'date is exists')
            self.current = self.next_date(self.current)

        self.logger.info(f'date is available')
        self.update_status(self.current, 'in progress')
        return self.current.strftime("%d-%m-%Y")  # return formatted?

    def update_status(self, date, status):
        self.logger.info(f'setting {date.strftime("%d-%m-%Y")} status to: {status}')
        self.collection.update_one(
            {'date': date.strftime("%d-%m-%Y")},
            {'$set': {'status': status}},
        )

    def date_used(self, date):
        self.logger.info(f'trying {date.strftime("%d-%m-%Y")}')
        res = self.collection.find({
            'date': date.strftime('%d-%m-%Y'),
            'status': 'in progress'
        })
        return res.retrieved > 0

    def next_date(self, date):
        prev = date - datetime.timedelta(1)
        if prev.weekday() == SATURDAY:
            prev = prev - datetime.timedelta(1)

        return prev

    # def init_db(self, logger, db_name):
    #     if self.client is None:
    #         logger.error('err no db connection')
    #         return None
    #     return self.client.get_db(db_name)

    def init_collection(self, db_name, collection_name):
        self.collection = self.client[db_name].get_collection(collection_name)
        if self.collection.count() == 0:
            self.logger.info(f'initializing collection: {collection_name}')
            self.collection.insert({
                'date': self.current.strftime('%d-%m-%Y'),
                'status': 'available'
            })
        self.logger.info(f'collection @{collection_name} initialized')

        return self.collection
