import os
import shutil
import datetime

CATEGORIES = {'images': ('JPEG', 'PNG', 'JPG', 'SVG'), 'documents': ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
              'audio': ('MP3', 'OGG', 'WAV', 'AMR'), 'video': ('AVI', 'MP4', 'MOV', 'MKV'), 'archives': ('ZIP', 'GZ', 'TAR')}

file_log = []

def folder_path(path):
    if os.path.exists(path):
        global base_path
        base_path = path
        return sort_files(base_path)
    else:
        print('Wrong path!')

def rename_exists_files(name):
    return name + '_edit_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')

def log():
    final_dict = {}
    for i in file_log:
        for k, v in i.items():
            final_dict.setdefault(k, []).append(v)
    for k, v in final_dict.items():
        print(f'---{k}---')
        print(', '.join(v))
    print(f"Sorting in the {base_path} catalog has been completed successfully.")

def ignore_list():
    ignore = []
    for k in CATEGORIES.keys():
        ignore.append(k)
    return ignore

def remove_folders(path):
    folders = list(os.walk(path))
    for path, _, _ in folders[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)

def move_files(file_path):
    dirname, fname = os.path.split(file_path)
    extension = os.path.splitext(fname)[1].upper().replace('.', '')
    for k, v in CATEGORIES.items():
        if extension in v:
            os.makedirs(base_path + '/' + k, exist_ok=True)
            if os.path.exists(os.path.join(base_path + '/' + k, fname)):
                new_f_renamed = rename_exists_files(os.path.splitext(fname)[0]) + os.path.splitext(fname)[1]
                shutil.move(os.path.join(file_path), os.path.join(base_path + '/' + k, new_f_renamed))
                file_log.append({k: new_f_renamed})
            else:
                shutil.move(os.path.join(file_path), os.path.join(base_path + '/' + k, fname))
                file_log.append({k: fname})

def sort_files(path):
    subfolders = []
    files = []
    ignore = ignore_list()
    for i in os.scandir(path):
        if i.is_dir():
            if i.name not in ignore:
                old_path = os.path.dirname(i.path)
                os.rename(os.path.join(old_path, i.name), os.path.join(old_path, i.name))
                subfolders.append(os.path.join(old_path, i.name))
        if i.is_file():
            old_path = os.path.dirname(i.path)
            os.rename(os.path.join(old_path, i.name), os.path.join(old_path, i.name))
            files.append(os.path.join(old_path, i.name))
            move_files(os.path.join(old_path, i.name))
    for dir in list(subfolders):
        sf, i = sort_files(dir)
        subfolders.extend(sf)
        files.extend(i)

    return subfolders, files

def sort_files_entry_point(path):
    folder_path(path)
    remove_folders(base_path)
    log()