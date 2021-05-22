from hcva.utils.database import Database
from hcva.utils.logger import Logger
from hcva.utils.time import call_sleep
from hcva.utils.json import read_data, save_data
from hcva.utils.path import get_path, sep, get_files, create_dir, change_dir


handledFolder = get_path(n=0) + f'products{sep}handled_json_products{sep}'
unhandledFolder = get_path(n=0) + f'products{sep}unhandled_json_products{sep}'
backupFolder = get_path(n=0) + f'products{sep}backup_json_products{sep}'
unBackupFolder = get_path(n=0) + f'products{sep}unBackup_json_products{sep}'
elasticFolder = get_path(n=0) + f'products{sep}upload_json_to_elastic{sep}'

# key = source, value = destination
uploadFolders = {handledFolder: handledFolder,
                 unhandledFolder: unhandledFolder,
                 backupFolder: backupFolder,
                 unBackupFolder: backupFolder,
                 elasticFolder: elasticFolder}
downloadFolders = [handledFolder, backupFolder]


for f in [handledFolder, unhandledFolder, backupFolder, unBackupFolder, elasticFolder]:
    create_dir(f)


def get_folder_name(folder):
    return folder.split(sep)[-2]


def fix_data(name, data):
    if "ת.החלטה" in str(data):
        for item in data["Case Details"]["תיק דלמטה"]:
            item["תאריך החלטה"] = item.pop("ת.החלטה")
        save_data(data, name, "")


def upload_sync(loop=True):
    _logger = Logger('upload_sync.log', get_path(n=0) + f'logs{sep}').get_logger()
    while True:
        total = 0
        u_counter = 0
        s_counter = 0
        db = Database().get_db('SupremeCourt')

        for folder in uploadFolders.keys():
            connection = db.get_collection(get_folder_name(folder))
            cursor = list(connection.find({}))
            backup_file_list = [file['name'] for file in cursor]
            list_of_files = get_files(folder_path=folder)
            total += len(list_of_files)
            _logger.info(f"Got {len(list_of_files)} files to upload in folder {folder}...")
            if len(list_of_files) > 0:
                index = 0
                for fileName in list_of_files:
                    index += 1
                    _logger.info(f"Starting to upload file {index} of {len(list_of_files)}... ")
                    data = read_data(fileName, '')
                    fix_data(fileName, data)
                    fullFilePath = fileName
                    fileName = fileName.replace(folder, '')  # extract file name
                    if fileName not in backup_file_list:
                        try:
                            connection.insert_one({"name": fileName, "data": data})
                            u_counter += 1
                            _logger.info(f"Succeed to upload file {fileName}")
                            if folder != uploadFolders[folder]:  # move file if folders are different
                                change_dir(fullFilePath, uploadFolders[folder], delete_source_if_destination_file_exist=True)
                        except Exception as e:  # TODO better Exception
                            _logger.info(f"Failed to upload file {fullFilePath}")
                            _logger.info(e)
                    else:
                        _logger.info("Skipped")
                        s_counter += 1

        _logger.info(f"{u_counter} files Uploaded...\n{s_counter} files Skipped...\n{total - u_counter - s_counter} Failed...\nTotal {total} files")
        if loop is False:
            break
        call_sleep(logger=_logger, minutes=10)


def download_sync(loop=True):
    _logger = Logger('download_sync.log', get_path(n=0) + f'logs{sep}').get_logger()
    while True:
        total = 0
        db = Database().get_db('SupremeCourt')
        for folder in downloadFolders:
            counter = 0
            connection = db.get_collection(get_folder_name(folder))
            cursor = list(connection.find({}))
            file_list = [file.replace(folder, '') for file in get_files(folder_path=folder)]  # extract file name
            for file in cursor:
                if file['name'] not in file_list:
                    save_data(file['data'], file['name'], folder)
                    counter += 1
            total += counter
            _logger.info(f"Total {counter} files ware downloaded into {folder}")
        _logger.info(f"Total {total} files ware downloaded")
        if loop is False:
            break
        call_sleep(logger=_logger, hours=1)
