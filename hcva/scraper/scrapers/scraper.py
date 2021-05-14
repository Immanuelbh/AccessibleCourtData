# -*- coding: utf-8 -*-
import os

from psutil import cpu_count
from concurrent.futures import ThreadPoolExecutor
from hcva.utils.database import Database
from hcva.utils.time import currTime
from hcva.utils.logger import Logger
from hcva.utils.path import create_dir
ROOT_DIR = os.path.abspath(os.curdir)


class Scraper:
    num_of_crawlers = None  # number of threads as well
    scraped_path = None  # product path as string
    db_exists = False

    def __init__(self, threads=1):
        log_path = ROOT_DIR + '/logs/hcva/'
        self.logger = Logger('scraper.log', log_path).getLogger()
        ##
        self.db = Database(self.logger)
        if self.db.client is not None:
            self.db = self.db.get_db()
            self.num_of_crawlers = min(cpu_count(), 4) if threads == 0 else threads
            self.scraped_path = ROOT_DIR + '/cases/scraped/'
            self.backup_path = ROOT_DIR + '/cases/scraped_backup/'
            create_dir(self.scraped_path)
        else:
            self.logger.error('err no db connection')

    # Functions
    def get_num_of_crawlers(self):
        return self.num_of_crawlers

    # output - return case file name by date and page index as string
    @staticmethod
    def random_name(index=0):
        return f'{currTime()}_{index}.json'  # date_time_index.json

    def get_settings(self, key):
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

    def upload_data(self, name, data):
        try:
            collection = self.db.get_collection('files')
            collection.insert_one({"name": name, "data": data})
            return True
        except Exception as _:  # TODO better Exception
            return False

    def get_link(self):
        return NotImplementedError

    def start_crawlers(self):
        return NotImplementedError

    def start(self):
        with ThreadPoolExecutor() as executor:
            indexes = [index for index in range(1, self.get_num_of_crawlers() + 1)]
            results = executor.map(self.start_crawlers, indexes)
        for result in results:
            print(result)
