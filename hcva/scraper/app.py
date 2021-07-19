import threading
from concurrent.futures import ThreadPoolExecutor
from hcva.utils import constants
from hcva.scraper import scraper
from hcva.utils.database import Database
from hcva.utils.logger import Logger
from hcva.utils.path import create_dir


class App:
    logger = Logger('app.log', constants.LOG_DIR).get_logger()

    def __init__(self, threads):
        self.threads = threads
        self.db = Database()
        self.db.init_collection(constants.DB_NAME, constants.COLLECTION_NAME)
        create_dir(constants.SCRAPED_DIR)

    def run(self):
        dates = self.db.get_dates()
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.scrape, dates)

    def scrape(self, date):
        date = date['date']
        self.logger.info(f'starting thread #{threading.current_thread().name} for date: {date}')
        try:
            scraper.get(date)
            self.logger.info(f'saving {date} cases to filesystem')
            self.db.update_status(date, 'done')
        except Exception as e:
            self.logger.info(f'failed to scrape date: {date}, reason: {e}')
            self.db.update_status(date, 'error')
        self.logger.info(f'thread #{threading.current_thread().name} finished')


def main():
    app = App(threads=int(constants.NUM_OF_CRAWLERS))
    if app:
        app.run()


if __name__ == "__main__":
    main()
