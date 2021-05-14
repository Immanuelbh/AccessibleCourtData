import json
from json.decoder import JSONDecodeError
from hcva.utils.path import get_path
from hcva.utils.time import currTime


def saveData(data, fileName=None, filePath=None):
    fileName = f"dataFromScraper_{currTime()}" if fileName is None else fileName
    filePath = get_path() if filePath is None else filePath
    with open(filePath + fileName, 'w') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=True)


def readData(fileName, filePath=None):
    try:
        filePath = get_path() if filePath is None else filePath
        with open(filePath + fileName, encoding='utf8') as json_file:
            data = json.load(json_file)
        return data
    except JSONDecodeError as e:
        print(f'Error in decoding this file: {fileName}')
        print(e)
        return ''
