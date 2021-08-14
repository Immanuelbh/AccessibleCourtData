import threading
from concurrent.futures import ThreadPoolExecutor
from hcva.scraper.scraper import get
from hcva.utils import constants
from hcva.utils.database import Database
from hcva.utils.logger import Logger
from hcva.utils.path import create_dir

logger = Logger('app.log', constants.LOG_DIR).get_logger()
db = Database()


def scrape(date):
    date = date['date']
    logger.info(f'starting thread #{threading.current_thread().name} for date: {date}')
    try:
        get(date)
        logger.info(f'saving {date} cases to filesystem')
        db.update_status(date, 'done')
    except Exception as e:
        logger.info(f'failed to scrape date: {date}, reason: {e}')
        db.update_status(date, 'error')
    logger.info(f'thread #{threading.current_thread().name} finished')


def scraper():
    create_dir(constants.SCRAPED_DIR)
    db.init_collection(constants.DB_NAME, constants.COLLECTION_NAME)
    dates = db.get_dates()
    threads = int(constants.NUM_OF_CRAWLERS)
    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(scrape, dates)
