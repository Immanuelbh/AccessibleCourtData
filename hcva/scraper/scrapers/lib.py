def scrape(self, date):
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