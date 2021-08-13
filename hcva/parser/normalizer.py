import string


def normalize(parsed):
    # verdict_json = json.load(json_file)

    petitioners = parsed["Doc Details"]["העותר"]
    defense = parsed["Doc Details"]["המשיב"]
    judges = parsed["Doc Details"]["לפני"]
    petitioner_attorneys = parsed["Doc Details"]["בשם העותר"]
    defense_attorneys = parsed["Doc Details"]["בשם המשיב"]

    cleaned_petitioners = pre_process_not_legal(petitioners)
    cleaned_defense = pre_process_not_legal(defense)
    cleaned_judges = pre_process_legal(judges)
    cleaned_petitioners_attorneys = pre_process_legal(petitioner_attorneys)
    cleaned_defense_attorneys = pre_process_legal(defense_attorneys)

    # self.write_normalized_values_to_json(input_joined_path, cleaned_petitioners, 'העותר מנורמל')
    # self.write_normalized_values_to_json(input_joined_path, cleaned_defense, 'המשיב מנורמל')
    # self.write_normalized_values_to_json(input_joined_path, cleaned_judges, 'לפני מנורמל')
    # self.write_normalized_values_to_json(input_joined_path, cleaned_petitioners_attorneys, 'בשם העותר מנורמל')
    # self.write_normalized_values_to_json(input_joined_path, cleaned_defense_attorneys, 'בשם המשיב מנורמל')


def pre_process_not_legal(names: list[str]):
    processed_names = eliiminate_unwanted_chars_multi(names)
    return processed_names


def eliiminate_unwanted_chars_multi(list_of_names:list[str]):
    """
    That method is in charge of some of the pre-process precedures:
    1. eliminates pharenthesis
    2. eliminate id numbers
    3. minimize spaces on last names
    :param list_of_names - a list that contain the string we work on
    :returns new list after the process.
    """
    new_list = list()

    for name in list_of_names:
        new_name = eliiminate_unwanted_chars_single(name)
        new_list.append(new_name)

    return new_list


def eliiminate_unwanted_chars_single(text: str):
    """
    That method is in charge of some of the pre-process procedures:
    1. eliminates parenthesis
    2. eliminate id numbers
    3. minimize spaces on last names
    :param text - the string we work on
    :returns the text after the process.
    """
    for word in str(text).split(' '):
        if word.find("(") != -1 or word.find(")") != -1:
            text = text.replace(word, "")
        if word.find('.') != -1:
            for char in word:
                if char in string.digits:
                    text = text.replace(word, "")
                    break

    text = '-'.join(text.split(' - '))
    text = ' '.join([word for word in text.split() if word != ' '])
    return text


def pre_process_legal(names: list[str]):
    names_after_eliminating_unwanted_chars = eliiminate_unwanted_chars_multi(names)

    names_after_first_split = split_by_char(names_after_eliminating_unwanted_chars, ';')
    names_after_second_split = split_by_char(names_after_first_split, ',')

    naming_path = 'naming_stopwords.csv'
    stopwords_path = 'stopwordsafterfilter.csv'

    names_after_naming = eliminate_naming_multi(names_after_second_split, naming_path)
    names_after_stopwords = eliminate_naming_multi(names_after_naming, stopwords_path)

    names_ready_for_for_first_and_last_name = organize_name(names_after_stopwords)
    after_single_clean_list = clean_single_name_multi(names_ready_for_for_first_and_last_name)

    return after_single_clean_list


def split_by_char(names: list[str], char: str):
    splitted = list()

    for name in names:
        flag = False
        name_one = str()
        name_two = str()

        if name.find(char) != -1:
            name_one = ' '.join(name.split(char)[0].split())
            name_two = ' '.join(name.split(char)[1].split())
            flag = True
        if flag:
            splitted.append(name_one)
            splitted.append(name_two)
        else:
            splitted.append(name)

    return splitted


def eliminate_naming_multi(input_names: list, path: str):
    """
    Eliminates all names match that has been on the csv file
    :param input_names - a list containing the strings to work on
    :param path - the csv file path
    :returns the new list after eliminating all matched words from the original strings
    """
    new_list = list()
    with open(path, "r", encoding="utf-8") as csv_name:
        # csv_names = csv.reader(csv_name, delimiter=',')
        # names = [row[0] for row in csv_names]
        for name in input_names:
            after_names = ' '.join([word for word in str(name).split() if word not in names])
            if after_names != '':
                new_list.append(after_names)

    return new_list


def organize_name(names: list[str]):
    new_values = list()
    for name in names:
        values = ' '.join(name.split()).split()
        flag = False
        if len(values) == 3:
            first_name = values[0]
            values.remove(values[0])
            last_name = '-'.join(values)
            full_name = str.format('{0} {1}', first_name, last_name)
            new_values.append(full_name)
            flag = True

        elif len(values) > 2 and len(values) % 2 == 0:
            for idx in range(int(len(values) // 2)):
                splitted = str.format("{0} {1}", values[2 * idx], values[(2 * idx) + 1])
                new_values.append(splitted)
            flag = True

        if not flag:
            new_values = names

        new_values = [determine_order(name) for name in new_values]

    return new_values


def determine_order(full_name: str):
    """
    determines if specified full name is in the correct order: (first name) (last_name)
    full_name - string to be evaluated
    returns the string after order is set
    """
    # split the string
    values = full_name.split()
    first = values[0]
    last = values[1]

    # check if the first name contains '-' - that means it is last name in thw rong position
    if first.find('-') != -1:
        new_str = f'{last} {first}'
    else:
        new_str = f'{first} {last}'

    return new_str


def clean_single_name_multi(names: list[str]):
    """
    clean names when multiple '-' character is present.
    that issue may be solved adjusting the parser's work
    :param names: a list of strings that represents the names to clean
    :return: the list with the cleaned names
    """
    new_names = list()

    for name in names:
        new_names.append(clean_single_name_single(name))

    return new_names


def clean_single_name_single(name: str):
    """
    clean names when multiple '-' character is present.
    that issue may be solved adjusting the parser's work
    :param name: a string represents the name to clean
    :return: cleaned string
    """
    new_name = str()

    if str(name).find('-') != -1:
        count = 0
        for char in name:
            if char == '-':
                count += 1

        if count != 1:
            left = str()
            right = str()
            left = name.split('-')[0]
            right = name.split('-')[1]
            left = ''.join([char for char in str(left) if char not in string.punctuation])
            right = ''.join([char for char in str(right) if char not in string.punctuation])
            new_name = str.format('{0}-{1}', left, right)
    else:
        new_name = ''.join([char for char in str(name) if char not in string.punctuation])

    return new_name


# def write_normalized_values_to_json(verdict_path: str, input_list: list[str], new_role_key: str):
#     """
#     adds the normalized key with the new values to the json and write it to destination
#     verdict_path - the string of the verdict path
#     dest_path - the string of the destination directory
#     input_list - the normalized values strings in a list
#     new_role_key - the key string that will be added to the json
#     """
#     verdict_id = get_verdict_id(verdict_path)
#     if os.path.exists(output_path + '/' + verdict_id + '.json'):
#         path = output_path + '/' + verdict_id + '.json'
#     else:
#         path = input_path + '/' + verdict_id + '.json'
#
#     with open(path,'r',encoding='utf-8') as json_to_read:
#         verdict = json.load(json_to_read)
#         verdict['_source']['doc']['Doc Details'][new_role_key] = input_list
#     with open(path,'w',encoding='utf-8') as json_to_write:
#         json.dump(verdict,json_to_write,ensure_ascii=False)