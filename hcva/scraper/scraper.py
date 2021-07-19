import time
from hcva.scraper.crawler import Crawler
from hcva.utils import constants
from hcva.utils.json import save_data
from hcva.utils.time import call_sleep
from hcva.utils.logger import Logger

logger = Logger('scraper.log', constants.LOG_DIR).get_logger()
BASE_URL = 'https://supreme.court.gov.il/Pages/SearchJudgments.aspx?&DateType=2&freeText=null&CaseNumber=null'


def build_url(date):
    return f'{BASE_URL}&COpenDate={date}&CEndDate={date}'


def get_frame(crawler, elem_type, string):
    frame = crawler.find_elem(elem_type, string)
    if frame is not None:
        return crawler.switch_frame(frame)

    print(f'could not switch to frame: {string}')
    return False


def get_num_cases(crawler):
    case_num_loc = ['/html/body/div[2]/div/form/section/div/div']
    crawler.switch_to_default_content()
    get_frame(crawler, 'id', 'serviceFram')
    for location in case_num_loc:
        elem = crawler.find_elem('xpath', location, delay=8)
        if elem is not None:
            update = crawler.read_elem_text(elem)
            text = crawler.get_text_query(update)
            if text is not None and len(text) > 0:
                count_cases = [int(s) for s in text.split() if s.isdigit()][0]
                print(f'this page got {count_cases} cases')
                return count_cases
    print('could not get this page amount of cases')
    return 0

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


def get_elem(crawler, xpath, index):
    string = get_string_by_index(xpath, index)
    return crawler.find_elem('xpath', string, raise_error=False)


def scroll_into_view(crawler, num):
    result = True
    if num > 90:
        for index in range(84, num - 5):
            elem = get_elem(crawler, 'שם', index)
            result = crawler.scroll_to_elem(elem)
        if result:
            print('scrolled to elem')
        else:
            print('could not scrolled to case')


def get_case(crawler, index):
    res = dict()
    xpath_keys = ['תאריך', 'עמודים', 'שם']
    for key in xpath_keys:
        elem = get_elem(crawler, key, index)
        if elem is not None:
            update = crawler.read_elem_text(elem)
            res[key] = crawler.get_text_query(update)
            print(f'got {key}: {res[key]}')
            if key == 'שם':
                crawler.click_elem(elem)
        else:
            print(f'did not found {key}')
    return res


def fix_page_location(crawler):
    elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/section/div/a[1]')
    crawler.scroll_to_elem(elem)


def get_doc(crawler):
    text = None
    elem = crawler.find_elem('xpath', '/html/body/div[2]/div/div/div[2]/div/div[2]')
    if elem is not None:
        text = elem.text  # clean spaces
    return text


def is_blocked_case(crawler):
    elem = crawler.find_elem('xpath', '/html/body/table/tbody/tr[1]/td/b', raise_error=False)
    if elem is not None:
        print('this case in a private !!!')
        result = False
    else:
        print('this case in not private - we can get more info')
        result = True
    return result

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


def get_general_details(crawler, index):
    m_dict = dict()
    title = get_titles(index)
    for col in range(len(title)):
        for row in range(len(title[col])):
            string = '/html/body/div/div[2]/div[1]/div[' + str(col + 1) + ']/div[' + str(row + 1) + ']/span[2]'
            elem = crawler.find_elem('xpath', string)
            update = crawler.read_elem_text(elem)
            m_dict[title[col][row]] = crawler.get_text_query(update)
    return m_dict


def get_other_case_details(crawler, index):
    m_list = list()
    title = get_titles(index)
    row = 0
    keep_going = True

    elem = get_elem(crawler, 'many rows', index)
    multi_row = crawler.read_elem_text(elem)

    while keep_going is True:
        row += 1
        m_dict = dict()
        for col in range(len(title)):
            if multi_row:
                xpath = '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr[' + str(
                    row) + ']/td[' + str(col + 1) + ']'
            else:
                xpath = '/html/body/div/div[2]/div[' + str(index) + ']/table/tbody/tr/td[' + str(col) + ']'

            elem = crawler.find_elem('xpath', xpath, raise_error=False)
            update = crawler.read_elem_text(elem)
            text = crawler.get_text_query(update)

            if update:
                m_dict[title[col]] = text
            else:  # No more info to get here
                keep_going = False
                break

        if keep_going is True:
            m_list.append(m_dict)
            if multi_row is False:
                break
    return m_list


def get_column_text(crawler, index):
    string = get_string_by_index('no info column', index)
    elem = crawler.find_elem('xpath', string, raise_error=False)
    update = crawler.read_elem_text(elem)
    if update is True:  # No info here
        return None

    string = get_string_by_index('inside column', index)
    elem = crawler.find_elem('xpath', string)
    call_sleep(seconds=1)

    if index == 1:
        func = get_general_details
    else:
        func = get_other_case_details

    if elem is not None:
        return func(crawler, index)
    return None


def get_case_inside_details(crawler):
    table = dict()
    if is_blocked_case(crawler):
        start, finish = 1, 8  # make more loops for more columns
        for index in range(start, finish):
            elem = get_elem(crawler, 'column', index)
            if elem is not None:
                update = crawler.read_elem_text(elem)
                headline = crawler.get_text_query(update)
                crawler.click_elem(elem)
                table[headline] = get_column_text(crawler, index)
                print('got info from column number: {}'.format(index))
            else:
                print('could not get text or press column number: {}'.format(index))
    return table


def get_case_details(crawler, index):
    case_details_dict = dict()

    crawler.switch_to_default_content()
    get_frame(crawler, 'id', 'serviceFram')

    scroll_into_view(crawler, index)
    case_details_dict['Doc Info'] = get_case(crawler, index)

    if case_details_dict['Doc Info']['שם'] is not None:
        fix_page_location(crawler)
        case_details_dict['Doc Details'] = get_doc(crawler)
        case_details_dict['Doc Info'].pop('שם', None)  # remove duplicate name before merge dicts
        get_frame(crawler, 'xpath', '/html/body/div[2]/div/div/div[2]/div/div[1]/div/div/iframe')
        case_details_dict['Case Details'] = get_case_inside_details(crawler)

        crawler.go_back()
    else:
        case_details_dict['Doc Details'] = None
        case_details_dict['Case Details'] = None

    return case_details_dict


def get(date):
    logger.info(f'scraping date: {date}')
    url = build_url(date)
    crawler = Crawler(url=url)
    time.sleep(5)
    try:
        num_cases = get_num_cases(crawler)
        for i in range(num_cases, 0, -1):  # get from last to first
            cd = get_case_details(crawler, i)
            save_case(cd, date, i)
    except Exception as e:
        logger.info(f'failed to scrape date: {date}, reason: {e}')
        crawler.close()

    crawler.close()


def save_case(cd, date, i):
    name = f'{date}__{i}.json'
    save_data(cd, name, constants.SCRAPED_DIR)
    logger.info(f'saved {name}')
