from glob import glob
from shutil import move, Error as fileExistError
from pathlib import Path
from platform import system
from os import sep, path, mkdir, remove


# do - return current path if didn't got oldPath and remove N folders from the end
def get_path(old_path=None, n=0, end_sep=True):
    curr_path = Path().parent.absolute() if old_path is None else old_path  # get curr path in not provided
    split_path = str(curr_path).split(sep)  # split path to folders
    n = -n if n > 0 else len(split_path)  # fix N for proper slice
    new_path = f"{sep}".join(split_path[:n])  # rejoin wanted folders into path
    return new_path + sep if end_sep else new_path  # path + sep if true else path


def get_all_files(folder_name):
    return [f for f in glob(folder_name + "/*.json")]


# input - if dirName is string create folder at current path else create all the path
def create_dir(dir_name):
    try:
        if not path.exists(dir_name):  # Create target Directory if don't exist
            mkdir(dir_name)
            # logger.info(f"Creating dir with the name: {dir_name}")
    except FileNotFoundError as _:
        n = 1 if system() == 'Windows' else 2  # in case system is not windows - splitPath will have sep at the end
        create_dir(get_path(dir_name, n=n))  # create parent target folder
        create_dir(dir_name)  # create target folder


# move file\folder from oldPath to newPath, fileName can be inside oldPath
def change_dir(src, dest, file_name=None, delete_src_if_dest_exist=False, delete_dest_if_dest_exist=False):
    try:
        move(src, dest) if file_name is None else move(src + file_name, dest)
    except fileExistError as _:  # handle a duplicate file
        print("file already exist in new path - ", end='')
        if delete_src_if_dest_exist:
            remove(src) if file_name is None else remove(src + file_name)
            print("file deleted in source path")
        elif delete_dest_if_dest_exist:
            n = 1 if system() == 'Windows' else 2
            file_path = dest + file_name if file_name is not None else dest + src.split(sep)[-n]
            remove(file_path)
            print("file deleted in destination path")
            change_dir(src, dest, file_name, delete_src_if_dest_exist, False)
        else:
            print("no delete permission was given")
