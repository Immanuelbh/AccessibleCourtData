from hcva.parser.new_schema import add_new_schema
from hcva.utils import constants
from hcva.utils.logger import Logger
from hcva.utils.json import read_data, save_data
from hcva.utils.path import create_dir, remove, get_all_files
from hcva.utils.time import call_sleep


def clean_spaces(text):
    if type(text) is str:  # if text is a string
        if '\n' in text:  # if there is more than one line
            return clean_spaces(text.splitlines())  # resend it as list
    else:  # if text is a list
        for index in range(len(text)):  # for each line in the list
            text[index] = clean_spaces(text[index])  # resend one line
        return text

    temp_list = list()  # the return list of characters
    space = ' '
    for index in range(len(text)):
        if text[index] == space:  # if this a space
            if index != 0:  # if we not on the first index
                if text[index - 1] == space:  # if we saw a space don't add this one
                    continue
                else:  # in this case we do want to add
                    pass
            else:
                continue
        temp_list.append(text[index])

    if len(temp_list) > 0:  # make sure we don't got empty list
        while temp_list[0] == space:  # clean spaces at the start
            temp_list.pop(0)
        while temp_list[-1] == space:  # clean spaces at the end
            temp_list.pop(-1)

    return "".join(temp_list)  # rejoin the set of characters


def make_sure_no_number(line, minimum=1, maximum=200):
    for number in range(minimum, maximum):
        if str(number) in line:
            line = line.replace(str(number), '')
    return clean_spaces(line)


def drop_extra_info(text, minimum=1, maximum=5):
    product = list()
    eof_sign = '__'
    start_word = 'לפני'
    key_in_line_sign = ':'
    banned_words = ['נגד', 'נ ג ד', 'ש ו פ ט ת', 'ש ו פ ט', 'ר ש ם', 'ר ש מ ת', 'ה נ ש י א ה', 'ה נ ש י א']
    temp = clean_spaces(text)
    for index in range(len(temp)):
        if eof_sign in temp[index]:  # we got all we want lets pack it and go back
            return "\n".join(product)
        elif key_in_line_sign in temp[index] or start_word in temp[index]:  # In case we have more rows between row 0 to judges names
            maximum = index

        if index not in range(minimum, maximum):  # Include all but unnecessary information
            do_break = False
            for word in banned_words:
                if word in temp[index]:
                    do_break = True
                    break
            if do_break:
                continue
            product.append(temp[index])
    return '\n'.join(product)  # rejoin all the line of the text


def remove_words(values):
    remove_word = ['כבוד', 'השופטת', 'השופט', 'הרשמת', 'הרשם', 'המשנה לנשיאה', 'המשנה לנשיא', 'הנשיאה', 'הנשיא']
    for word in remove_word:
        if type(values) is list:
            for index in range(len(values)):
                values[index] = values[index].replace(word, '')
                values[index] = clean_spaces(values[index])
        else:
            values = clean_spaces(values.replace(word, ''))
    return values


def is_there_more(line, old_values=None, key=';'):
    old_values = list() if old_values is None else old_values
    if key in line:
        values = line.split(key)
        for index in range(len(values)):
            values[index] = clean_spaces(values[index])
        old_values.extend(remove_words(values))
    else:
        old_values.append(remove_words(line))
    return old_values


def get_key(temp_key):
    temp_key = make_sure_no_number(temp_key)
    temp_dict = {
        'לפני': ['לפני', 'בפני'],
        'בשם העותר': ['בשם המערערים', 'בשם המערער', 'בשם המערערת', 'בשם המערערות',
                      'בשם העותר', 'בשם העותרת', 'בשם העותרים', 'בשם העותרות',
                      'בשם המבקש', 'בשם המבקשת', 'בשם המבקשים', 'בשם המבקשות',
                      'בשם העורר', 'בשם העוררת', 'בשם העוררים', 'בשם העוררות',
                      'בשם המאשים', 'בשם המאשימה', 'בשם המאשימים', 'בשם המאשימות',
                      'בשם התובע', 'בשם התובעת', 'בשם התובעים', 'בשם התובעות'],

        'בשם המשיב': ['בשם המשיבים', 'בשם המשיב', 'בשם המשיבות', 'בשם המשיבה',
                      'בשם הנאשמים', 'בשם הנאשם', 'בשם הנאשמות', 'בשם הנאשמת',
                      'בשם הנתבעים', 'בשם הנתבע', 'בשם הנתבעות', 'בשם הנתבעת'],

        'העותר': ['המערערים', 'המערער', 'המערערת', 'המערערות',
                  'העותר', 'העותרת', 'העותרים', 'העותרות',
                  'המבקש', 'המבקשת', 'המבקשים', 'המבקשות',
                  'המאשים', 'המאשימים', 'המאשימה', 'המאשימות',
                  'העורר', 'העוררת', 'העוררים', 'העוררות',
                  'התובע', 'התובעת', 'התובעים', 'התובעות'],

        'המשיב': ['המשיבים', 'המשיב', 'המשיבות', 'המשיבה',
                  'הנאשם', 'הנאשמת', 'הנאשמים', 'הנאשמות',
                  'הנתבעים', 'הנתבעת', 'הנתבעות', 'הנתבע'],
    }

    for key, item in temp_dict.items():
        if temp_key in item:
            return key
    for key, item in temp_dict.items():
        for possible_key in item:
            if possible_key in temp_key:
                return key

    return None  # if it get here we missing some keys or No key in given tempKey


def got_verdict(line):
    verdict_key_list = ['החלטה', 'פסק-דין', 'פסק דין', 'צו-על-תנאי']
    for key in verdict_key_list:
        if key in line:
            return True, key
    return False, None


def got_extra_information(line):
    extra_information_keys = ['בקשה', 'ערעור', 'העברת מקום דיון', 'הגשת עיקרי טיעון', 'צו על תנאי']
    for key in extra_information_keys:
        if key in line:
            return True
    return False


def get_key_list(must_have=True):
    if must_have:
        return ['לפני', 'העותר', 'המשיב', 'מספר הליך', 'סוג מסמך', 'סיכום']
    return ['מידע נוסף', 'בשם העותר', 'בשם המשיב']


def i_got_it_all(temp_dict, key_list):
    for key in key_list:
        if key in temp_dict.keys():
            if temp_dict[key] is None:
                return False
        else:
            return False
    return True


def parser(case_text):
    doc_dict = dict()
    add_token, temp_key, values_list, num_of_values, lines_to_skip = False, None, None, 1, []
    case_text = drop_extra_info(case_text)
    verdict_lines = case_text.splitlines()
    doc_dict['מספר הליך'] = verdict_lines[0]
    n = len(verdict_lines)
    for index in range(1, n):
        if index in lines_to_skip:
            continue
        elif ':' in verdict_lines[index] or get_key(verdict_lines[index]) is not None:  # we got a key
            if add_token:  # finished getting values for previous key
                key = get_key(temp_key)
                if key not in doc_dict.keys():
                    doc_dict[key] = values_list
                else:
                    doc_dict[key].extend(values_list)
                num_of_values = 1
            values_list = list()  # start gather values for found key
            temp_list = verdict_lines[index].split(':')
            temp_key = temp_list[0]
            add_token = True
            if len(temp_list) > 1:
                if len(temp_list[1]) > 0:
                    values_list.append(temp_list[1])
        elif got_verdict(verdict_lines[index])[0]:  # what remain is verdict text
            key = get_key(temp_key)
            doc_dict[key] = values_list
            doc_dict['סוג מסמך'] = got_verdict(verdict_lines[index])[1]
            doc_dict['סיכום'] = "\n".join(verdict_lines[index + 1:])
            break
        else:  # get another values for key or get extra text pre verdict
            str_value = f"{num_of_values}. "  # string to replace in ordered values
            if str_value in verdict_lines[index]:  # if we got another value to add
                num_of_values += 1  # increment value for next in order
                values_list.append(verdict_lines[index].replace(str_value, ''))  # remove the number + dot + space from the new value
            elif got_extra_information(verdict_lines[index]):  # if we got extra info
                extra_info_values = verdict_lines[index]
                while index + 1 < n:  # start gather all extra info in coming rows
                    if ":" in verdict_lines[index + 1]: # if we finished with extra info
                        if "תאריך הישיבה:" not in verdict_lines[index + 1]:  # private case of extra info
                            if get_key(verdict_lines[index + 1].split(':')[0]) is not None:
                                break
                    elif got_verdict(verdict_lines[index + 1])[0]:
                        break

                    index += 1
                    lines_to_skip.append(index)  # make list of lines we added
                    extra_info_values += f";{verdict_lines[index]}"  # concatenate value to string
                doc_dict['מידע נוסף'] = is_there_more(extra_info_values)  # get list from the string we built
            else:  # add new value\s to the list
                values_list = is_there_more(verdict_lines[index], values_list)

    if i_got_it_all(doc_dict, get_key_list()):
        for key in get_key_list(must_have=False):
            if key not in doc_dict.keys():
                doc_dict[key] = list()
            if None in doc_dict.keys():
                return case_text, False
        return doc_dict, True
    return case_text, False


def move_file(data, file_name, source_folder, dest_folder):
    remove(file_name)  # delete old copy
    file_name = file_name.replace(source_folder, '')  # extract file name
    save_data(data, file_name, dest_folder)  # save new copy


def parse(case):
    case['Doc Details'], success = parser(case['Doc Details'])  # if succeed Dict, else text
    if success:
        case['Doc Info'].pop('עמודים')
        case['Doc Details'] = {**case['Doc Details'], **case['Doc Info']}
        case.pop('Doc Info')
        # for key in case['Doc Info']:
        #     case['Doc Details'][key] = case['Doc Info'][key] if key != 'עמודים' \
        #         else [int(s) for s in case['Doc Info'][key].split() if s.isdigit()][0]
        # case.pop('Doc Info', None)
        return case

    return None


def is_valid(logger, case):
    if len(case) < 1:
        logger.error('length is 0')
        return False
    elif not case['Doc Details']:
        logger.error('missing "Doc Details"')
        return False
    elif 'פני:' not in str(case['Doc Details']):
        logger.error('missing "פני"')
        return False

    return True


def parser_flow(parsed):
    p = add_new_schema(parsed)
    return p


def run(logger, cases):
    if not cases:
        logger.info('no cases to parse')
        return

    logger.info(f'parsing {len(cases)} cases')
    for case in cases:
        logger.info(f'trying to parse {case}...')
        c = read_data(case, constants.SCRAPED_DIR)
        if c and is_valid(logger, c):
            logger.info(f'read {case} successfully')
            p = parse(c)
            if p:
                logger.info(f'stage 1 - parsed successfully: {case}')
                p = parser_flow(p)
                logger.info(f'stage 2 - parser_flow finished successfully: {case}')
                save_data(p, case, constants.PARSED_SUCCESS_DIR)
                logger.info(f'saved {case} to {constants.PARSED_SUCCESS_DIR}')
            else:
                logger.info(f'failed to parse {case}')
                save_data(c, case, constants.PARSED_FAILED_DIR)
        else:
            logger.info(f'failed to read {case}: case not valid')
            save_data(c, case, constants.PARSED_FAILED_VALIDATION_DIR)
    # TODO remove file from scraped?
    logger.info(f'finished parsing {len(cases)} cases')


def get_names(files):
    names = []
    for file in files:
        s = file.split("/")
        n = s[len(s)-1]
        names.append(n)
    return names


def get_cases(path_):
    files = get_all_files(path_)
    return get_names(files)


def main():
    logger = Logger('parser.log', constants.LOG_DIR).get_logger()
    logger.info("parser is starting")
    create_dir(constants.PARSED_SUCCESS_DIR)
    create_dir(constants.PARSED_FAILED_DIR)
    create_dir(constants.PARSED_FAILED_VALIDATION_DIR)
    while True:
        cases = get_cases(constants.SCRAPED_DIR)
        run(logger, cases)
        call_sleep(logger=logger, minutes=10)


if __name__ == '__main__':
    main()
