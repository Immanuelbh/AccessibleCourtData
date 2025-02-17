import threading
from concurrent.futures import ThreadPoolExecutor
from hcva.scraper.scraper import get
from hcva.utils import constants
from hcva.utils.database import Database, StatusType
from hcva.utils.logger import Logger
from hcva.utils.path import create_dir
from hcva.utils.time import call_sleep

logger = Logger('scraper_main.log', constants.LOG_DIR).get_logger()
db = Database()


def scrape(date):
    date = date['date']
    logger.info(f'starting thread #{threading.current_thread().name} for date: {date}')
    try:
        get(date)
        logger.info(f'saving {date} cases to filesystem')
        db.update_status(date, StatusType.DONE)
    except Exception as e:
        logger.info(f'failed to scrape date: {date}, reason: {e}')
        db.update_status(date, StatusType.ERROR)
    logger.info(f'thread #{threading.current_thread().name} finished')


def scraper():
    create_dir(constants.SCRAPED_DIR)
    while True:
        logger.info(f'starting scraper')
        db.init_collection()
        dates = db.get_dates()
        threads = int(constants.NUM_OF_CRAWLERS)
        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(scrape, dates)
        logger.info(f'scraper has finished')
        call_sleep(logger=logger, days=1)
