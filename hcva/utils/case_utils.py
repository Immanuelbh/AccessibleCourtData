from glob import glob


def get_names(files):
    names = []
    for file in files:
        s = file.split("/")
        n = s[len(s)-1]
        names.append(n)
    return names


def get_all_files(folder_name):
    return [f for f in glob(folder_name + "/*.json")]


def get_cases(path_):
    files = get_all_files(path_)
    return get_names(files)


def get_dates(files):
    dates = set()
    for file in files:
        s1 = file.split("/")
        n = s1[len(s1)-1]
        s2 = n.split("__")
        d = s2[0]
        dates.add(d)
    return dates


def get_case_dates(path_):
    files = get_all_files(path_)
    return get_dates(files)


