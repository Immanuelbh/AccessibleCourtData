import os
from concurrent.futures import ThreadPoolExecutor
from hcva.utils.json import save_data
from hcva.scraper.crawler.crawler import Crawler
from hcva.scraper.scrapers import lib
from hcva.utils.database import Database
from hcva.utils.logger import Logger

DB_NAME = 'hcva'
COLLECTION_NAME = 'test'
ROOT_DIR = os.path.abspath(os.curdir)
log_path = ROOT_DIR + f'/logs/{DB_NAME}/'


class S:
    logger = Logger('s.log', log_path).getLogger()

    def __init__(self, threads):
        # self.crawler = crawler
        self.threads = threads
        self.db_instance = Database()
        # self.db_instance.init_db(self.logger, DB_NAME)
        self.db_instance.init_collection(DB_NAME, COLLECTION_NAME)

    def m_run(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run, range(self.threads))

    def run(self, idx):
        self.logger.info(f'starting thread #{idx}')
        try:
            d = self.db_instance.get_date()  # TODO turn atomic
            crawler = Crawler()  # TODO initialize crawler in ctor? ###################
            case = lib.scrape(d)
            save_data(case)

            ###
            # date, link, first, last, case_list = self.get_link()
            # if first <= last or last == -1:
            #     self.logger.info(f'starting to scrape date: {date}')
            #     t1 = time()
            #     self.get_cases_data(self.crawler, date, link, first, last, case_list)
            #     self.logger.info(f'finished crawling page with the date: {date}, it took {(time() - t1) / 60} minutes')
            # else:
            #     self.logger.info('nothing to crawl here')
        # except WebDriverException as err:
        #     self.logger.exception(f'browser closed or crashed :: {err}')
        except Exception as err:
            self.logger.error(f'error: {err}')

        self.logger.info(f'finished thread #{idx}')

        # if self.crawler is not None:
        #     self.crawler.close()
        # return "crawler #{} is done".format(idx)


def main():
    scraper = S(threads=1)
    if scraper:
        scraper.m_run()


if __name__ == "__main__":
    main()