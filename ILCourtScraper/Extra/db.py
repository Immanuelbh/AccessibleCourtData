from os import environ
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# DB_URI = "mongodb://root:example@localhost:27017/SupremeCourt?authSource=admin"
DB_URI = environ.get('MONGO_DB_URI')


class DB:
    def __init__(self, logger=None):
        self.logger = logger
        self.client = MongoClient(DB_URI)
        self.get_connection()

    def get_connection(self):
        try:
            self.log('db trying to connect...')
            connection = self.client
            self.log('db connected')
            print('db ', self.client.list_database_names())
        except ServerSelectionTimeoutError as err:
            message = 'db connection Timeout - check for if this machine ip is on whitelist'
            if self.logger is not None:
                self.logger.exception(message + err)
            else:
                print(message + err)
            connection = None
        return connection

    def getDB(self, dbName):
        self.log(f'db trying to get db: {dbName}')
        db = self.client[dbName]
        self.log(f'got db: {db.name}')
        return db

    def getCollection(self, db, collectionName):
        collection = db.get_collection(collectionName)
        self.log(f'got collection: {collectionName}')
        return collection

    def log(self, message):
        if self.logger is not None:
            self.logger.info(message)
