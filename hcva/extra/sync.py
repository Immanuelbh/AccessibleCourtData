from hcva.extra.db import DB
from hcva.extra.logger import Logger
from hcva.extra.time import callSleep
from hcva.extra.json import readData, saveData
from hcva.extra.path import getPath, sep, getFiles, createDir, changeDir


handledFolder = getPath(N=0) + f'products{sep}handled_json_products{sep}'
unhandledFolder = getPath(N=0) + f'products{sep}unhandled_json_products{sep}'
backupFolder = getPath(N=0) + f'products{sep}backup_json_products{sep}'
unBackupFolder = getPath(N=0) + f'products{sep}unBackup_json_products{sep}'
elasticFolder = getPath(N=0) + f'products{sep}upload_json_to_elastic{sep}'

# key = source, value = destination
uploadFolders = {handledFolder: handledFolder,
                 unhandledFolder: unhandledFolder,
                 backupFolder: backupFolder,
                 unBackupFolder: backupFolder,
                 elasticFolder: elasticFolder}
downloadFolders = [handledFolder, backupFolder]


for f in [handledFolder, unhandledFolder, backupFolder, unBackupFolder, elasticFolder]:
    createDir(f)


def getFolderName(folder):
    return folder.split(sep)[-2]


def fixData(name, data):
    if "ת.החלטה" in str(data):
        for item in data["Case Details"]["תיק דלמטה"]:
            item["תאריך החלטה"] = item.pop("ת.החלטה")
        saveData(data, name, "")


def uploadSync(loop=True):
    _logger = Logger('uploadSync.log', getPath(N=0) + f'logs{sep}').getLogger()
    while True:
        total = 0
        uCounter = 0
        sCounter = 0
        db = DB().getDB('SupremeCourt')

        for folder in uploadFolders.keys():
            connection = db.get_collection(getFolderName(folder))
            cursor = list(connection.find({}))
            backupFileList = [file['name'] for file in cursor]
            listOfFiles = getFiles(folderPath=folder)
            total += len(listOfFiles)
            _logger.info(f"Got {len(listOfFiles)} files to upload in folder {folder}...")
            if len(listOfFiles) > 0:
                index = 0
                for fileName in listOfFiles:
                    index += 1
                    _logger.info(f"Starting to upload file {index} of {len(listOfFiles)}... ")
                    data = readData(fileName, '')
                    fixData(fileName, data)
                    fullFilePath = fileName
                    fileName = fileName.replace(folder, '')  # extract file name
                    if fileName not in backupFileList:
                        try:
                            connection.insert_one({"name": fileName, "data": data})
                            uCounter += 1
                            _logger.info(f"Succeed to upload file {fileName}")
                            if folder != uploadFolders[folder]:  # move file if folders are different
                                changeDir(fullFilePath, uploadFolders[folder], deleteSourceIfDestinationFileExist=True)
                        except Exception as e:  # TODO better Exception
                            _logger.info(f"Failed to upload file {fullFilePath}")
                            _logger.info(e)
                    else:
                        _logger.info("Skipped")
                        sCounter += 1

        _logger.info(f"{uCounter} files Uploaded...\n{sCounter} files Skipped...\n{total - uCounter - sCounter} Failed...\nTotal {total} files")
        if loop is False:
            break
        callSleep(logger=_logger, minutes=10)


def downloadSync(loop=True):
    _logger = Logger('downloadSync.log', getPath(N=0) + f'logs{sep}').getLogger()
    while True:
        total = 0
        db = DB().getDB('SupremeCourt')
        for folder in downloadFolders:
            counter = 0
            connection = db.get_collection(getFolderName(folder))
            cursor = list(connection.find({}))
            fileList = [file.replace(folder, '') for file in getFiles(folderPath=folder)]  # extract file name
            for file in cursor:
                if file['name'] not in fileList:
                    saveData(file['data'], file['name'], folder)
                    counter += 1
            total += counter
            _logger.info(f"Total {counter} files ware downloaded into {folder}")
        _logger.info(f"Total {total} files ware downloaded")
        if loop is False:
            break
        callSleep(logger=_logger, hours=1)
