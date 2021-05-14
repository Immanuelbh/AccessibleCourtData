# -*- coding: utf-8 -*-
from psutil import cpu_count
from concurrent.futures import ThreadPoolExecutor
from hcva.utils.db import DB
from hcva.utils.time import currTime
from hcva.utils.logger import Logger
from hcva.utils.path import getPath, sep, createDir


class Scraper:
    num_of_crawlers = None  # number of threads as well
    productsFolder = None  # product path as string
    logger = None
    db_exists = False

    def __init__(self, num_of_crawlers=0, site=None):
        log_path = getPath(N=0) + f'logs{sep}{site}{sep}' if site is not None else getPath(N=0) + f'logs{sep}'
        self.logger = Logger(f'{site}_Scraper.log', log_path).getLogger()
        self.db = DB(logger=self.logger)
        if self.db.client is not None:
            self.db = self.db.getDB(site)
            self.num_of_crawlers = min(cpu_count(), 4) if num_of_crawlers == 0 else num_of_crawlers
            self.productsFolder = getPath(N=0) + f'products{sep}json_products{sep}'  # product path
            self.backupFolder = getPath(N=0) + f'products{sep}backup_json_products{sep}'
            createDir(self.productsFolder)
        else:
            print('err no db connection')

    # Functions
    def getNumOfCrawlers(self):
        return self.num_of_crawlers

    # output - return case file name by date and page index as string
    @staticmethod
    def randomName(index=0):
        return f'{currTime()}_{index}.json'  # date_time_index.json

    def getSettings(self, key):
        if self.db_exists:
            collection = self.db.get_collection('settings')
            query = collection.find({})
            for item in query:
                if key in item:
                    return item[key]
        else:
            # first run
            self.db.collection.insert({"crawler Run": True})
            self.db_exists = True
            return True

    def uploadData(self, name, data):
        try:
            collection = self.db.get_collection('files')
            collection.insert_one({"name": name, "data": data})
            return True
        except Exception as _:  # TODO better Exception
            return False

    def get_link(self):
        return NotImplementedError

    def start_crawler(self, index):
        return NotImplementedError

    def start(self):
        with ThreadPoolExecutor() as executor:
            indexes = [index for index in range(1, self.getNumOfCrawlers() + 1)]
            results = executor.map(self.start_crawler, indexes)
        for result in results:
            print(result)
