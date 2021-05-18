# -*- coding: utf-8 -*-
from hcva.scraper.scrapers.scraper import Scraper
from hcva.utils.json import save_data
from hcva.utils.time import callSleep, time
from hcva.scraper.crawler.crawler import Crawler, WebDriverException
from hcva.scraper.scrapers.linker import get_links, update_date_in_db, dateURL_P1, dateURL_P2, dateURL_P3
from concurrent.futures import ThreadPoolExecutor


class SupremeCourtScraper(Scraper):
    site = 'SupremeCourt'

    def __init__(self, crawler, threads=1):
        super().__init__(threads)
        self.crawler = crawler
        self.threads = threads

    def get_link(self):
        item = get_links(self.db)
        if item is not None:
            self.logger.info(f'crawler took date {item["date"]}')
            url = dateURL_P1 + item['date'] + dateURL_P2 + item['date'] + dateURL_P3
            return item['date'], url, item['first'], item['last'], item['case List']
        else:
            self.logger.info('Did not get dates from db')
            return None, None, None, None, None

    def get_frame(self, crawler, elem_type, string):
        frame = crawler.find_elem(elem_type, string)
        if frame is not None:
            return crawler.switch_frame(frame)
        else:
            self.logger.info(f'could not switch to frame: {string}')
            return False

    # input - crawler as web driver
    # output - return number of case in the page as int
    def get_num_of_cases(self, crawler):
        case_num_loc = ['/html/body/div[2]/div/form/section/div/div']
        crawler.switch_to_default_content()
        self.get_frame(crawler, 'id', 'serviceFram')
        for location in case_num_loc:
            elem = crawler.find_elem('xpath', location, delay=8)
            if elem is not None:
                update = crawler.read_elem_text(elem)
                text = crawler.get_text_query(update)
                if text is not None and len(text) > 0:
                    n = [int(s) for s in text.split() if s.isdigit()][0]
                    self.logger.info('this page got {} cases'.format(n))
                    return n
        self.logger.warning('could not get this page amount of cases')
        return 500

    # input - N as int, first as int, last as int
    # output - start as int, finish as int
    @staticmethod
    def case_picker(N, first, last):
        delta = N - last
        if delta > 0:  # got new cases
            if first < last:  # didn't finish scrape page - so start from scratch
                return 1, N, N
            return 1, delta - 1, N  # scrape only new cases
        elif first < last:  # keep going where left off
            return first, last, N

    @staticmethod
    def get_string_by_index(xpath, index):
        if xpath == 'שם':
            return f'/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[{index}]/div[2]/a'
        elif xpath == 'column':
            return f'/html/body/div/div[1]/div/div/div[{index}]/a'
        elif xpath == 'inside column':
            return f'/html/body/div/div[2]/div[{index}]'
        elif xpath == 'no info column':
            return f'/html/body/div/div[2]/div[{index}]/table/tbody/tr[4]/td/h4'
        elif xpath == 'many rows':
            return f'/html/body/div/div[2]/div[{index}]/table/tbody/tr[1]/td[1]'
        elif xpath == 'html':
            return f'/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[{index}]/div[4]/div[2]/a[3]'
        elif xpath == 'תאריך':
            return f'/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[{index}]/div[4]/div[1]/span[1]'
        elif xpath == 'עמודים':
            return f'/html/body/div[2]/div/form/div/div/div[1]/div[3]/ul/li[{index}]/div[4]/div[1]/span[3]'

    def get_elem(self, crawler, xpath, index):
        string = self.get_string_by_index(xpath, index)
        return crawler.find_elem('xpath', string, raise_error=False)

    # input - crawler as web driver, N is the index we want to reach as int
    # do - put in view the item we want to click
    def scroll_into_view(self, crawler, n):
        result = True
        if n > 90:
            for index in range(84, n - 5):
                elem = self.get_elem(crawler, 'שם', index)
                result = crawler.scroll_to_elem(elem)
            if result:
                self.logger.debug('scrolled to elem')
            else:
                self.logger.debug('could not scrolled to case')

    # input - crawler as web driver, index as int
    # output - return date, page number and case name in dict
    # do - return case name, date and page number of the case and enter that case
    def get_case(self, crawler, index):
        res = dict()
        xpath_keys = ['תאריך', 'עמודים', 'שם']
        for key in xpath_keys:
            elem = self.get_elem(crawler, key, index)
            if elem is not None:
                update = crawler.read_elem_text(elem)
                res[key] = crawler.get_text_query(update)
                self.logger.info(f'got {key}: {res[key]}')
                if key == 'שם':
                    crawler.click_elem(elem)
            else:
                self.logger.warning(f'did not found {key}')
        return res

    # input - crawler as web driver
    # do - call switchWindow, getFramebyID and getFramebyXpath functions
    def setUpBeforeGetCaseInsideDetails(self, crawler):
        # position browser to see all info
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/section/div/a[1]')
        crawler.scroll_to_elem(elem)
        # get second frame
        self.get_frame(crawler, 'xpath', '/html/body/div[2]/div/div/div[2]/div/div[1]/div/div/iframe')

    # input - index as int
    # output - array of titles as strings
    @staticmethod
    def get_titles(index):
        if index == 1:
            return [['מספר הליך', 'מדור', 'תאריך הגשה', 'סטטוס תיק'], ['מערער', 'משיב', 'אירוע אחרון']]
        elif index == 2:
            return ['סוג צד', '#', 'שם', 'באי כוח']
        elif index == 3:
            return ['שם בית המשפט', 'מספר תיק דלמטה', 'ת.החלטה', 'הרכב/שופט']
        elif index == 4:
            return ['תאריך', 'שעת דיון', 'אולם', 'גורם שיפוטי', 'סטטוס']
        elif index == 5:
            return ['#', 'ארוע ראשי', 'ארוע משני', 'תאריך', 'יוזם']
        elif index == 6:
            return ['#', 'נמען', 'תאריך חתימה']
        elif index == 7:
            return ['#', 'תיאור בקשה', 'תאריך', 'מגיש', 'נדחה מהמרשם']

    def get_general_details(self, crawler, index):
        m_dict = dict()
        title = self.get_titles(index)
        for col in range(len(title)):
            for row in range(len(title[col])):
                string = '/html/body/div/div[2]/div[1]/div[' + str(col + 1) + ']/div[' + str(row + 1) + ']/span[2]'
                elem = crawler.find_elem('xpath', string)
                update = crawler.read_elem_text(elem)
                m_dict[title[col][row]] = crawler.get_text_query(update)
        return m_dict

    def get_other_case_details(self, crawler, index):
        m_list = list()
        title = self.get_titles(index)
        row = 0
        keepGoing = True

        elem = self.get_elem(crawler, 'many rows', index)
        multiRow = crawler.read_elem_text(elem)

        while keepGoing is True:
            row += 1
            m_dict = dict()
            for col in range(len(title)):
                if multiRow:
                    xpath = '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr[' + str(
                        row) + ']/td[' + str(col + 1) + ']'
                else:
                    xpath = '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr/td[' + str(col) + ']'

                elem = crawler.find_elem('xpath', xpath, raise_error=False)
                update = crawler.read_elem_text(elem)
                text = crawler.get_text_query(update)

                if update:
                    m_dict[title[col]] = text
                else:  # No more info to scrape here
                    keepGoing = False
                    break

            if keepGoing is True:
                m_list.append(m_dict)
                if multiRow is False:
                    break
        return m_list

    # input - crawler as web driver, index as int
    # output - return column inside text
    def get_column_text(self, crawler, index):
        string = self.get_string_by_index('no info column', index)
        elem = crawler.find_elem('xpath', string, raise_error=False)
        update = crawler.read_elem_text(elem)
        if update is True:  # No info here
            return None

        string = self.get_string_by_index('inside column', index)
        elem = crawler.find_elem('xpath', string)
        callSleep(seconds=1)

        if index == 1:
            func = self.get_general_details
        else:
            func = self.get_other_case_details

        if elem is not None:
            return func(crawler, index)
        else:
            return None

    # input - crawler as web driver
    # output - return False if this is a private case, otherwise True
    def is_blocked_case(self, crawler):
        elem = crawler.find_elem('xpath', '/html/body/table/tbody/tr[1]/td/b', raise_error=False)
        if elem is not None:
            self.logger.info('this case in a private !!!')
            result = False
        else:
            self.logger.info('this case in not private - we can scrape more info')
            result = True
        return result

    # input - crawler as web driver
    # output - return all of the case info as dict[column name] = text
    def get_case_inside_details(self, crawler):
        table = dict()
        if self.is_blocked_case(crawler):
            start, finish = 1, 8  # make more loops for more columns
            for index in range(start, finish):
                elem = self.get_elem(crawler, 'column', index)
                if elem is not None:
                    update = crawler.read_elem_text(elem)
                    headline = crawler.get_text_query(update)
                    crawler.click_elem(elem)
                    table[headline] = self.get_column_text(crawler, index)
                    self.logger.info('got info from column number: {}'.format(index))
                else:
                    self.logger.info('could not get text or press column number: {}'.format(index))
        return table

    @staticmethod
    def get_doc(crawler):
        text = None
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/div[2]/div/div[2]')
        if elem is not None:
            text = elem.text  # clean spaces
        return text

    # input - crawler as web driver
    def get_case_details(self, crawler, index):
        case_details_dict = dict()

        crawler.switch_to_default_content()
        self.get_frame(crawler, 'id', 'serviceFram')

        self.scroll_into_view(crawler, index)
        case_details_dict['Doc Info'] = self.get_case(crawler, index)

        if case_details_dict['Doc Info']['שם'] is not None:
            self.fix_page_location(crawler)
            case_details_dict['Doc Details'] = self.get_doc(crawler)
            case_details_dict['Doc Info'].pop('שם', None)  # remove duplicate name before merge dicts
            self.get_frame(crawler, 'xpath', '/html/body/div[2]/div/div/div[2]/div/div[1]/div/div/iframe')
            case_details_dict['Case Details'] = self.get_case_inside_details(crawler)

            crawler.go_back()
        else:
            case_details_dict['Doc Details'] = None
            case_details_dict['Case Details'] = None

        return case_details_dict

    @staticmethod
    def check_for_back_button(crawler):
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/section/div/a[1]')
        return crawler.click_elem(elem)

    @staticmethod
    def fix_page_location(crawler):
        elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/section/div/a[1]')
        crawler.scroll_to_elem(elem)

    def check_case_num(self, crawler, link):
        # pick cases
        n, tries = 500, 3
        page_loaded = crawler.update_page(link)
        while n == 500 and tries > 0:
            n = self.get_num_of_cases(crawler)
            tries -= 1
            self.check_for_back_button(crawler)  # in page got only the same case - happen in old dates
        return n, page_loaded

    # input - crawler as web driver
    # output (disabled) - return all the cases for the page he see as dict[caseName] = [caseFileDict, caseDetailsDict]
    #                                                    caseFileDict as dict['Case File'] = document text
    #                                                    caseDetailsDict as dict['Case Details'] = Case Details
    def get_cases_data(self, crawler, date, link, first, last, case_list):
        n, page_loaded = self.check_case_num(crawler, link)
        case_list = [i + n - last for i in case_list]  # fix case number
        case_list.extend([i for i in range(1, n - last + 1)])  # add new cases
        case_list.sort()
        start, finish, n = self.case_picker(n, first, last)

        if page_loaded is False or n == 500:
            self.logger.info('page not loaded')
            return None

        if finish == 0:
            update_date_in_db(self.db, date, start, finish, True, case_list)
        else:
            case_list = [i for i in range(1, n + 1)] if len(case_list) == 0 else case_list
            self.logger.info(f'page scrape cases {case_list}')
            temp_case_list = case_list.copy()
            for index in case_list:
                try:
                    t1 = time()
                    case_details_dict = self.get_case_details(crawler, index)
                    if case_details_dict['Doc Details'] is not None:
                        name = self.random_name(index)
                        save_data(case_details_dict, name, self.scraped_path)  # save copy for parser
                        save_data(case_details_dict, name, self.backup_path)  # save copy for backup
                    temp_case_list.remove(index)
                    update_date_in_db(self.db, date, index, n, True, temp_case_list)
                    self.logger.info(f'Case: {index} took in seconds: {time() - t1}')
                except WebDriverException as _:
                    raise WebDriverException
                except Exception as err:  # Unknown Exception appear
                    self.logger.exception(f'Case: {index} Failed :: {err}')

    def m_run(self):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.run, range(self.threads))

    def run(self, idx):
        self.logger.info(f'starting thread #{idx}')
        try:
            date, link, first, last, case_list = self.get_link()
            if first <= last or last == -1:
                self.logger.info(f'starting to scrape date: {date}')
                t1 = time()
                self.get_cases_data(self.crawler, date, link, first, last, case_list)
                self.logger.info(f'finished crawling page with the date: {date}, it took {(time() - t1) / 60} minutes')
            else:
                self.logger.info('nothing to crawl here')
        except WebDriverException as err:
            self.logger.exception(f'browser closed or crashed :: {err}')
        except Exception as err:
            self.logger.exception('unknown error' + err)

        self.logger.info(f'finished thread #{idx}')

        if self.crawler is not None:
            self.crawler.close()
        return "crawler is done"

    def start_crawlers(self):
        # callSleep(seconds=index * 5)  # crawlers start in different times to ensure they don't take the same page
        # self.logger.info('crawler attempting to start #' + str(index))
        crawler = None
        can_i_go = self.get_settings('crawler Run')
        self.logger.info('crawler can_i_go:' + str(can_i_go))

        while can_i_go:
            crawler = Crawler(id_=1, delay=2, site=self.site) if crawler is None else crawler
            try:
                date, link, first, last, case_list = self.get_link()
                if first <= last or last == -1:
                    self.logger.info(f'Starting to scrape date: {date}')
                    t1 = time()
                    self.get_cases_data(crawler, date, link, first, last, case_list)
                    message = f'Finished crawling page with the date: {date}, it took {(time() - t1) / 60} minutes'
                else:
                    message = 'Nothing to crawl here'
                self.logger.info(message)

            except WebDriverException as _:
                message = f'browser closed or crashed - restart value is {can_i_go}'
                self.logger.exception(message)
            except Exception as _:
                message = 'unknown error'
                self.logger.exception(message)
            finally:
                can_i_go = self.get_settings('crawler Run')

        if crawler is not None:
            crawler.close()
        return "done" + 1
        # callSleep(minutes=10)
        # self.start_crawlers(index=index)


def main():
    crawler = Crawler()
    if crawler:
        scraper = SupremeCourtScraper(crawler, threads=2)
        if scraper:
            scraper.m_run()
            # scraper.run()
    ##
    # scraper = SupremeCourtScraper()
    # scraper.start_crawlers(1)  # run 1 crawler
    # # scraper.start()  # run N crawlers


if __name__ == "__main__":
    main()
