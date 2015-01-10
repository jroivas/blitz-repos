import json
import os


def parse(config_file):
    if type(config_file) == file:
        return json.loads(config_file.read())

    with open(config_file, 'r') as fd:
        return json.loads(fd.read())

    return None

def check_dir(dir_name):
    if os.path.isdir(dir_name):
        return
    os.makedirs(dir_name)

def replace_entries(line, items):
    for item in items:
        if type(items[item]) == str or type(items[item]) == unicode:
            line = line.replace('%%%s%%' % (item), items[item])
    return line

def solve_folder(args):
    build_dir = os.getcwd()
    if 'folder' in args:
        build_dir = os.path.join(build_dir, args['folder'])

    return build_dir
