from hcva.utils.json import read_data, save_data
from hcva.utils.path import get_path, sep, get_all_files, remove

read_folder = get_path(n=0) + f'products{sep}handled_json_products{sep}'
write_folder = get_path(n=0) + f'products{sep}unhandled_json_products{sep}'


def fix_schema(doc):
    for key in doc['Doc Info']:
        doc['Doc Details'][key] = doc['Doc Info'][key] if key != 'עמודים' \
            else [int(s) for s in doc['Doc Info'][key].split() if s.isdigit()][0]
    doc.pop('Doc Info', None)
    return doc


def move_file(data, file_name, source_folder, dest_folder):
    remove(file_name)  # delete old copy
    file_name = file_name.replace(source_folder, '')  # extract file name
    save_data(data, file_name, dest_folder)  # save new copy


def run():
    list_of_files = get_all_files(read_folder)
    for file_name in list_of_files:
        doc = read_data('', file_name)  # fileName include path and os.sep not needed
        if 'לפני' in doc['Doc Details'].keys():
            doc = fix_schema(doc)
            move_file(doc, file_name, read_folder, write_folder)


run()

# TODO add function in new parser flow
