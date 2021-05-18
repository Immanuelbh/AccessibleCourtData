import os
from concurrent.futures import ThreadPoolExecutor
from hcva.utils.json import save_data
from hcva.scraper.crawler.crawler import Crawler
from hcva.scraper.scrapers import s
from hcva.utils.database import Database
from hcva.utils.logger import Logger
from hcva.utils.path import create_dir

DB_NAME = 'hcva'
COLLECTION_NAME = 'test'
ROOT_DIR = os.path.abspath(os.curdir)
LOG_DIR = ROOT_DIR + f'/logs/{DB_NAME}/'
SCRAPED_DIR = ROOT_DIR + '/cases/scraped/'
BACKUP_DIR = ROOT_DIR + '/cases/scraped_backup/'


class A:
    logger = Logger('s.log', LOG_DIR).getLogger()

    def __init__(self, threads):
        self.threads = threads
        self.db_instance = Database()
        self.db_instance.init_collection(DB_NAME, COLLECTION_NAME)
        create_dir(SCRAPED_DIR)

    def m_run(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run, range(self.threads))

    def run(self, idx):
        self.logger.info(f'starting thread #{idx}')
        d = self.db_instance.get_date()  # TODO turn atomic
        cases = s.scrape(idx, d)
        for case in cases:
            name = f'{d}__{idx}.json'
            save_data(case, name, SCRAPED_DIR)  # save copy for parser
            save_data(case, name, BACKUP_DIR)  # save copy for backup
            print(f'saved {name}')


        # try:
        #     cases = s.scrape(Crawler(idx), d)
        #     crawler = Crawler()  # TODO initialize crawler in ctor? ###################
        #     case = lib.scrape(d)
            # for case in cases:
            #     save_data(case, "name", "path")

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
        # except Exception as err:
        #     self.logger.error(f'error: {err}')
        #
        # self.logger.info(f'finished thread #{idx}')

        # if self.crawler is not None:
        #     self.crawler.close()
        # return "crawler #{} is done".format(idx)


def main():
    app = A(threads=1)
    if app:
        app.m_run()


if __name__ == "__main__":
    main()