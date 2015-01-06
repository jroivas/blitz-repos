#!/usr/bin/env python
import argparse
import json
import os
import shutil
import sys

def usage(name):
    print ('Usage: %s config.json [build_folder]' % (name))


def parse(config_file):
    with open(config_file, 'r') as fd:
        return json.loads(fd.read())

    return None

def check_dir(dir_name):
    if os.path.isdir(dir_name):
        return
    os.makedirs(dir_name)


class DataFetcher(object):
    def __init__(self, name, data, folder):
        self.name = name
        self.data = data
        self.folder = folder
        self.source = data.get('source', '')
        self.method = data.get('method', '')
        self.unpack = data.get('unpack', '')

    def parse_method(self):
        res = {
            'backend': '',
            'branch': '',
            'commit': '',
            'commands': []
        }
        if type(self.method) == dict:
            res.update(self.method)
        elif type(self.method) == list:
            res['commands'] = self.method
        else:
            res['backend'] = self.method

        return res

    def replace_source(self, source):
        for item in self.data:
            if type(self.data[item]) == str or type(self.data[item]) == unicode:
                source = source.replace('%%%s%%' % (item), self.data[item])
        return source

    def fetch_git(self, fetcher, source):
        source = self.replace_source(source)
        print (source)
        if os.path.isdir(self.folder + '/.git'):
            os.system('cd "%s" && git pull' % (self.folder))
        else:
            res = -1
            tries = 3
            while res != 0 and tries > 0:
                res = os.system('git clone "%s" "%s"' % (source, self.folder))
                if res != 0 and os.path.isdir(self.folder):
                    shutil.rmtree(self.folder, ignore_errors=True)
                tries -= 1

        if os.path.isdir(self.folder): 
            if fetcher['branch']:
                os.system('cd "%s" && git checkout "%s"' % (self.folder, fetcher['branch']))
            if fetcher['commit']:
                os.system('cd "%s" && git checkout "%s"' % (self.folder, fetcher['commit']))

    def unpack_untar(self, srcfile, folder, strip=0):
        extra = ''
        if strip > 0:
            extra =' --strip-components=%s' % (strip)
        print ("** Untarring...")
        os.system('cd "%s" && tar xf "%s"%s ' % (folder, srcfile, extra))

    def unpack_source(self, source, folder, strip=0):
        if type(self.unpack) == list:
            for cmd in self.unpack:
                cmd = self.replace_source(cmd)
                os.system('cd "%s" && "%s"' % (folder, cmd))
        elif self.unpack == '':
            #detect
            name = os.path.basename(source)
            srcfile = folder + '/' + name
            if os.path.isfile(srcfile):
                print ("*** Unpack %s" % (srcfile))
                if '.tar' in srcfile or '.tgz' in srcfile:
                    self.unpack_untar(srcfile, folder, strip=strip)
        else:
            cmd = self.replace_source(self.unpack)
            os.system('cd "%s" && "%s"' % (folder, cmd))

    def fetch_get(self, fetcher, source):
        check_dir(self.folder)

        strip = 1
        # FIXME Utilize python
        if type(source) == list:
            for src in source:
                src = self.replace_source(src)
                os.system('cd "%s" && wget -c %s' % (self.folder, src))
                self.unpack_source(src, self.folder, strip)
                strip = 0
        else:
            src =self.replace_source(source)
            os.system('cd "%s" && wget -c %s' % (self.folder, src))
            self.unpack_source(src, self.folder, strip)

    def fetch_commands(self, fetcher):
        check_dir(self.folder)
        for cmd in fetcher.commands:
            os.system('cd "%s" && %s' % (self.folder, cmd))

    def fetch(self):
        print ('*** Fetching %s' % (self.name))

        fetcher = self.parse_method()
        if fetcher['backend'] == 'git':
            self.fetch_git(fetcher, self.source)
        elif fetcher['backend'] == 'get':
            self.fetch_get(fetcher, self.source)
        elif fetcher['commands']:
            self.fetch_commands(fetcher)
        else:
            raise ValueError('Unknown fetcher: %s' % (fethcer))

class Builder(object):
    def __init__(self, name, data, folder):
        self.name = name
        self.data = data
        self.folder = folder
        self.build_dir = folder
        self.data = data
        self._build = data.get('build', '')
        self._configure = data.get('configure', '')

    def configure_cmake(self):
        # FIXME
        self.build_dir = self.folder + '/build'
        check_dir(self.build_dir)
        os.system('cd "%s" && cmake "%s"' % (self.build_dir, self.folder))

    def build_make(self):
        os.system('cd "%s" && make' % (self.build_dir))

    def configure(self):
        print ('*** Configuring %s' % (self.name))
        if not os.path.isdir(self.folder):
            print('ERROR: Build folder not found, need to initialize?')
            return False

        if self._configure == '' and self._build == 'cmake':
            self._configure = 'cmake'
            self._build = 'make'

        if self._configure == '':
            return
        elif self._configure == 'cmake':
            self.configure_cmake()
        elif type(self._configure) == list:
            for conf in self._configure:
                os.system('cd "%s" && %s' % (self.folder, conf))
        else:
            os.system('cd "%s" && %s' % (self.folder, self._configure))
        return True

    def build(self):
        print ('*** Building %s' % (self.name))
        if not os.path.isdir(self.folder):
            print('ERROR: Build folder not found, need to initialize?')
            return False

        if type(self._build) == list:
            for cmd in self._build:
                os.system('cd "%s" && %s' % (self.folder, cmd))
        elif self._build == '':
            pass
        elif self._build == 'cmake':
            self.build_make()
        elif self._build == 'make':
            self.build_make()
        else:
            raise ValueError('Unknown build system: %s' % (self.data))

        return True

def handle_project(name, data, dir_name, args):
    print ('* Project: %s' % name)
    actions = 0
    if args['all'] or args['init']:
        fetcher = DataFetcher(name, data, dir_name)
        fetcher.fetch()
        actions += 1
    if args['all'] or args['build'] or args['configure']:
        builder = Builder(name, data, dir_name)
        if args['all'] or args['configure']:
            if not builder.configure():
                return False
            actions += 1
        if args['all'] or args['build']:
            if not builder.build():
                return False
            actions += 1

    if actions == 0:
        print ('ERROR: No actions defined')
        return False

    return True

def init_project(name, proj, build_dir, args):
    for item in proj:
        if not handle_project(item, proj[item], build_dir + '/' + item, args):
            print ('ERROR: Problem while handling %s' % (item))

def init(config, args):
    build_dir = os.getcwd()
    if 'folder' in args:
        build_dir = os.path.join(build_dir, args['folder'])

    for item in config:
        if 'source' in config[item]:
            if not handle_project(item, config[item], build_dir + '/' + item, args):
                print ('ERROR: Problem while handling %s' % (item))
        else:
            init_project(item, config[item], build_dir + '/' + item, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Blitz repo')
    parser.add_argument('config', type=argparse.FileType('r'), help='Config file as JSON')
    parser.add_argument('-f', '--folder', default='', help='Output folder')
    parser.add_argument('-i', '--init', action='store_true', help='Initialize only, download sources')
    parser.add_argument('-b', '--build', action='store_true', help='Build sources')
    parser.add_argument('-c', '--configure', action='store_true', help='Build sources')
    parser.add_argument('-a', '--all', action='store_true', help='Perform all actions')

    res = parser.parse_args()

    args = vars(res)

    config = json.loads(args['config'].read())
    args['config'].close()

    init(config, args)
