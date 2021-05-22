import json
from json.decoder import JSONDecodeError
from hcva.utils.path import get_path


def save_data(data, file_name=None, file_path=None):
    with open(file_path + file_name, 'w') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=True)


def read_data(file_name, file_path=None):
    try:
        file_path = get_path() if file_path is None else file_path
        with open(file_path + file_name, encoding='utf8') as json_file:
            data = json.load(json_file)
        return data
    except JSONDecodeError as e:
        print(f'Error in decoding this file: {file_name}')
        print(e)
        return ''
