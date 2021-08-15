from glob import glob
from pathlib import Path
from platform import system
from os import path, mkdir


# do - return current path if didn't got oldPath and remove N folders from the end
def get_path(old_path=None, n=0, end_sep=True):
    curr_path = Path().parent.absolute() if old_path is None else old_path  # get curr path in not provided
    split_path = str(curr_path).split('/')  # split path to folders
    n = -n if n > 0 else len(split_path)  # fix N for proper slice
    new_path = f"/".join(split_path[:n])  # rejoin wanted folders into path
    return new_path + '/' if end_sep else new_path  # path + sep if true else path


def get_all_files(folder_name):
    return [f for f in glob(folder_name + "/*.json")]


# input - if dirName is string create folder at current path else create all the path
def create_dir(dir_name):
    try:
        if not path.exists(dir_name):  # Create target Directory if don't exist
            mkdir(dir_name)
    except FileNotFoundError as _:
        n = 1 if system() == 'Windows' else 2  # in case system is not windows - splitPath will have sep at the end
        create_dir(get_path(dir_name, n=n))  # create parent target folder
        create_dir(dir_name)  # create target folder
