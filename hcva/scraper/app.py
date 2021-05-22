import threading
from os import path, curdir
from concurrent.futures import ThreadPoolExecutor
from hcva.utils.json import save_data
from hcva.scraper import scraper
from hcva.utils.database import Database
from hcva.utils.logger import Logger
from hcva.utils.path import create_dir

DB_NAME = 'hcva'
COLLECTION_NAME = 'v3'
ROOT_DIR = path.abspath(curdir)
LOG_DIR = ROOT_DIR + f'/logs/{DB_NAME}/'
SCRAPED_DIR = ROOT_DIR + '/cases/scraped/'
# BACKUP_DIR = ROOT_DIR + '/cases/scraped_backup/'


class App:
    logger = Logger('app.log', LOG_DIR).get_logger()

    def __init__(self, threads):
        self.threads = threads
        self.db = Database()
        self.db.init_collection(DB_NAME, COLLECTION_NAME)
        create_dir(SCRAPED_DIR)

    def run(self):
        dates = self.db.get_dates()
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.scrape, dates)

    def scrape(self, d):
        self.logger.info(f'starting thread #{threading.current_thread().name}')
        d = d['date']
        cases = scraper.get(d)
        for i, case in enumerate(cases, start=1):
            name = f'{d}__{i}.json'
            save_data(case, name, SCRAPED_DIR)
            self.logger.info(f'saved {name}')

        self.db.update_status(d, 'done')  # TODO add empty/not empty
        self.logger.info(f'thread #{threading.current_thread().name} finished')


def main():
    app = App(threads=2)
    if app:
        app.run()


if __name__ == "__main__":
    main()
