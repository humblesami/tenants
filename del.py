import os
import glob
from os import path
from pathlib import Path
dir_path = str(path.dirname(path.realpath(__file__)))


def remove_folders(folder_name):
    res = glob.glob(dir_path+'/**/'+folder_name+'/*', recursive=True)
    skips = [str(dir_path) +'/django/']
    for file_path in res:
        for pth in skips:
            if file_path.startswith(pth):
                continue
        if file_path.endswith('__pycache__'):
            file_path = file_path+'/*'
            sub_res = glob.glob(file_path)
            for file_path1 in sub_res:
                os.remove(file_path1)
        elif not file_path.endswith('__init__.py'):
            if path.isfile(file_path):
                os.remove(file_path)
    print('Folders removed')


def remove_file_by_extension(ext):
    cnt = 0
    files = Path(dir_path).rglob('*.'+ext)
    for path in files:
        os.remove(str(path))
        cnt += 1
    print(str(cnt) + ' ' + ext + ' files removed')


def remove_files(file_name):
    cnt = 0
    files = Path(dir_path).rglob(file_name)
    for path in files:
        os.remove(str(path))
        cnt += 1
    print(str(cnt) + ' ' + file_name + ' files removed')

def remove_migrations():
    remove_folders('migrations')
    if path.exists('db.sqlite3'):
        os.remove('db.sqlite3')

remove_migrations()
remove_folders('tests')
remove_files('tests.py')
remove_file_by_extension('pyc')
remove_file_by_extension('po')
print('done')

