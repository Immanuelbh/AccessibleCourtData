from hcva.utils.json import read_data, save_data
from hcva.utils.path import get_path, sep, get_files, remove

readFolder = get_path(n=0) + f'products{sep}handled_json_products{sep}'
writeFolder = get_path(n=0) + f'products{sep}unhandled_json_products{sep}'


def fixSchema(doc):
    for key in doc['Doc Info']:
        doc['Doc Details'][key] = doc['Doc Info'][key] if key != 'עמודים' \
            else [int(s) for s in doc['Doc Info'][key].split() if s.isdigit()][0]
    doc.pop('Doc Info', None)
    return doc


def moveFile(data, fileName, sourceFolder, destFolder):
    remove(fileName)  # delete old copy
    fileName = fileName.replace(sourceFolder, '')  # extract file name
    save_data(data, fileName, destFolder)  # save new copy


def run():
    listOfFiles = get_files(folder_path=readFolder)
    for fileName in listOfFiles:
        doc = read_data('', fileName)  # fileName include path and os.sep not needed
        if 'לפני' in doc['Doc Details'].keys():
            doc = fixSchema(doc)
            moveFile(doc, fileName, readFolder, writeFolder)


run()