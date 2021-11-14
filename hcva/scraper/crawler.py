import os
import threading
from platform import system
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    ElementNotVisibleException, ElementNotSelectableException, ElementNotInteractableException, NoAlertPresentException, \
    JavascriptException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from hcva.utils import constants
from hcva.utils.logger import Logger


def get_os_type():
    os_type = constants.OS_TYPE
    if os_type == 'Linux':
        return 'linux'
    elif os_type == 'Darwin':
        return 'macos'
    elif os_type == 'Windows':
        return 'windows'
    return os_type


class Crawler:
    _driver = None  # Web Driver
    _delay = 2  # Timer for finding web element as int
    _url = None  # starting page as string
    _text_query = None  # latest text get as string
    _logger = None  # logging log class

    def __init__(self, url):
        self._logger = Logger(f'crawler_{threading.current_thread().name}.log', constants.LOG_DIR).get_logger()
        self._driver = self.get_browser()
        self._driver.get(url)
        self._logger.info('crawler created')

    def get_browser(self):
        browser = constants.BROWSER_TYPE
        os_type = get_os_type()
        driver_prefix = constants.ROOT_DIR + f'/hcva/scraper/web_drivers/{os_type}'
        driver_postfix = ''
        if os_type == 'windows':
            driver_postfix = '.exe'

        self._logger.debug(f'attempting to open browser: {browser}')
        if browser == 'chrome':
            driver_prefix += '/chromedriver'

            options = webdriver.ChromeOptions()
            if constants.HEADLESS == 'true':
                options.add_argument("--headless")

            return webdriver.Chrome(chrome_options=options, executable_path=driver_prefix+driver_postfix)
        elif browser == 'firefox':
            driver_prefix += '/geckodriver'

            options = webdriver.FirefoxOptions()
            if constants.HEADLESS == 'true':
                options.add_argument("--headless")

            return webdriver.Firefox(firefox_options=options, executable_path=driver_prefix+driver_postfix)
        else:
            self._logger.error(f'browser type is invalid: ${browser}')

    # input - update as boolean
    # output - return string if true, else None
    # do - return the last text that got scraped
    def get_text_query(self, update=True):
        if update:
            return self._text_query
        return None

    # output - return True if successful
    # do - close web driver
    def close(self):
        self._driver.quit()  # close the browser
        self._logger.info('Closing browser')
        return True

    # output - return True if successful
    # do - return to previous page
    def go_back(self):
        self._driver.back()
        self._logger.info('went to previous page')
        return True

    # output - return True if successful
    # do - refresh page loaded on crawler
    def refresh(self):
        self._driver.refresh()
        self._logger.info('Refresh page')
        return True

    # input - frame as web element
    # do
    def switch_frame(self, frame):
        self._driver.switch_to.frame(frame)
        self._logger.info('switch to frame')
        return True

    # do - switch windows handle after case was clicked
    def switch_window_handle(self, index=0):
        window = self._driver.window_handles[index]
        self._driver.switch_to.window(window)
        self._logger.info('switch window handle')
        return True

    # do - switch to default content
    def switch_to_default_content(self):
        self._driver.switch_to.default_content()
        self._logger.info('switch to default content')
        return True

    def get_page_source(self):
        page_source = self._driver.page_source
        self._logger.info('Got page Source')
        return page_source

    # input - elem_type as string, string as string
    # output - return element if found in <delay> seconds, None otherwise
    def find_elem(self, elem_type, string, single_element=True, driver=None, delay=2, raise_error=True):
        driver = self._driver if driver is None else driver
        message = ''
        try:
            elem = None
            message = f'found elem: {string}, type: {elem_type}'
            if single_element:
                if elem_type == 'xpath':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, string)))
                    elem = driver.find_element_by_xpath(string)
                elif elem_type == 'id':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, string)))
                    elem = driver.find_element_by_id(string)
                elif elem_type == 'tag':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.TAG_NAME, string)))
                    elem = driver.find_element_by_tag_name(string)
                elif elem_type == 'name':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, string)))
                    elem = driver.find_element_by_name(string)
                elif elem_type == 'link_text':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, string)))
                    elem = driver.find_element_by_link_text(string)
                elif elem_type == 'partial_link_text':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, string)))
                    elem = driver.find_element_by_partial_link_text(string)
                elif elem_type == 'css':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, string)))
                    elem = driver.find_element_by_css_selector(string)
                elif elem_type == 'class_name':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, string)))
                    elem = driver.find_element_by_class_name(string)
                else:
                    message = f'find_element function do not have: {elem_type}'
            else:
                if elem_type == 'xpath':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, string)))
                    elem = driver.find_elements_by_xpath(string)
                elif elem_type == 'id':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, string)))
                    elem = driver.find_elements_by_id(string)
                elif elem_type == 'tag':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.TAG_NAME, string)))
                    elem = driver.find_elements_by_tag_name(string)
                elif elem_type == 'name':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, string)))
                    elem = driver.find_elements_by_name(string)
                elif elem_type == 'link_text':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, string)))
                    elem = driver.find_elements_by_link_text(string)
                elif elem_type == 'partial_link_text':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, string)))
                    elem = driver.find_elements_by_partial_link_text(string)
                elif elem_type == 'css':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, string)))
                    elem = driver.find_elements_by_css_selector(string)
                elif elem_type == 'class_name':
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, string)))
                    elem = driver.find_elements_by_class_name(string)
                else:
                    message = f'find_element function do not have: {elem_type}'
            self._logger.info(message)
            return elem

        except TimeoutException as te:  # did not found elem in time
            if raise_error:
                self._logger.error(f'Did not find elem: {string}, type: {elem_type}, delay: {delay} in time', te)
            return None

        except ElementNotVisibleException as enve:  # did not found elem
            if raise_error:
                self._logger.error(f'Elem is not visible: {string}, type: {elem_type}', enve)
            return None

        except NoSuchElementException as nse:  # did not found elem
            if raise_error:
                self._logger.error(f'No Such elem: {string}, type: {elem_type}', nse)
            return None
        finally:
            if raise_error is False:
                self._logger.info(message)

    # input - driver as web driver, elem as web element
    # output - return True if successful, otherwise False
    # do - hover the elem
    def hover_elem(self, driver, elem):
        try:
            hover = ActionChains(driver).move_to_element(elem)
            hover.perform()
            self._logger.info('elem got hovered')
            return True

        except Exception as e:
            self._logger.error('Could not hover that', e)
            return False

    # input - elem as web element, value as string, msg as string
    # output - return True if successful, otherwise False
    # do - select the option in elem
    def select_elem(self, elem, option):
        message = None
        if type(option) is not str:  # if value is not string
            message = f'option should be string and not {type(option)}'
        try:
            select = Select(elem)  # select the elem
            select.select_by_visible_text(option)  # select by text
            message = 'elem got selected'
            self._logger.info(message)
            return True

        except ElementNotSelectableException as e:
            self._logger.error('error selecting element', e)
            return False

    # input - elem as web element, msg as string
    # output - return True if successful, otherwise False
    def click_elem(self, elem):
        try:
            if elem is not None:
                elem.click()  # click the elem
                message = 'element got clicked'
            else:
                message = 'didnt got element to click - got None instead'
            self._logger.info(message)
            return True

        except ElementClickInterceptedException as ecie:
            self._logger.error('Element Click Intercepted', ecie)
            return False

        except ElementNotInteractableException as enie:
            self._logger.error('Element Not Interactable', enie)
            return False

    # input - elem as web element, data as string
    # output - return True if successful, otherwise False
    # do - send the text box elem string
    def send_data_to_elem(self, elem, data, to_clear=True):
        try:
            message = ''
            if to_clear:
                elem.clear()  # clear text box
                message = 'text box got cleared'
            elem.send_keys(data)  # type sting into text box
            message += ', element got the data'
            self._logger.info(message)
            return True

        except Exception as e:
            self._logger.error('Could not send elem this data', e)
            return False

    # input - elem as web element
    # output - return True if successful, otherwise False
    # do - get the elem text
    def read_elem_text(self, elem):
        try:
            text = elem.text  # get elem text
            self._text_query = text
            self._logger.info(f'Got text from elem: {text}')
            return True

        except AttributeError as e:
            self._text_query = None
            self._logger.error('Could not get elem text, error: ', e)
            return False

    # input - driver as web driver, N is the index we want to reach as int
    # do - put in view the item we want
    @staticmethod
    def scroll_to_elem(elem):
        if elem is not None:
            elem.location_once_scrolled_into_view  # don't put ()
            return True
        return False

    # input - driver as web driver, elem as web element, string as string
    # output - return True if successful, False as stop flag, massage as string
    # do - execute script on element
    def exec_script(self, driver, elem, string):
        try:
            driver.execute_script(string, elem)
            self._logger.info('Script executed')
            return True

        except JavascriptException as je:
            self._logger.error('Could not execute script', je)
            return False

    # input - result as string
    # output - return True if successful
    # do - return massage if result none, accept alert if result accept so accept, if result dismiss so dismiss
    def alert_handle(self, driver=None, result=None):
        driver = self._driver if driver is None else driver
        try:
            obj = driver.switch_to.alert  # driver focus on alert window
            text = f'alert massage says: {obj.text}'  # take alert window massage

            if result is not None:
                if result == 'accept':
                    obj.accept()  # accept alert window
                elif result == 'dismiss':
                    obj.dismiss()  # dismiss alert window

            driver.switch_to.default_content()  # return to main window

            self._text_query = text
            self._logger.info(f'Alert say: {text}')
            return True

        except NoAlertPresentException as nape:
            self._logger.error('Did not find any alert', nape)
            return False
