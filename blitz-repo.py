#!/usr/bin/env python
import sys
import json
import os

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
        if os.path.isdir(self.folder):
            os.system('cd "%s" && git pull' % (self.folder))
        else:
            os.system('git clone "%s" "%s"' % (source, self.folder))

        if os.path.isdir(self.folder): 
            if fetcher['branch']:
                os.system('cd "%s" && git checkout "%s"' % (self.folder, fetcher['branch']))
            if fetcher['commit']:
                os.system('cd "%s" && git checkout "%s"' % (self.folder, fetcher['commit']))

    def fetch_get(self, fetcher, source):
        check_dir(self.folder)

        # FIXME Utilize python
        if type(source) == list:
            for src in source:
                os.system('cd "%s" && wget -c %s' % (self.folder, self.replace_source(src)))
        else:
            os.system('cd "%s" && wget -c %s' % (self.folder, self.replace_source(source)))

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

    def build(self):
        print ('*** Building %s' % (self.name))
        if type(self._build) == list:
            raise ValueError('Build commands not supported')
        elif self._build == '':
            pass
        elif self._build == 'cmake':
            self.build_make()
        elif self._build == 'make':
            self.build_make()
        else:
            raise ValueError('Unknown build system: %s' % (self.data))

def handle_project(name, data, dir_name):
    fetcher = DataFetcher(name, data, dir_name)
    fetcher.fetch()
    builder = Builder(name, data, dir_name)
    builder.configure()
    builder.build()

def init_project(name, proj, build_dir):
    for item in proj:
        print ('** Subproject: %s' % item)
        handle_project(item, proj[item], build_dir + '/' + item)

def init(config, extra_dir=''):
    build_dir = os.getcwd()
    if extra_dir:
        build_dir = os.path.join(build_dir, extra_dir)

    for item in config:
        print ('* Initializing: %s' % item)
        check_dir(build_dir + '/' + item)
        if 'source' in config[item]:
            handle_project(item, config[item], build_dir + '/' + item)
        else:
            init_project(item, config[item], build_dir + '/' + item)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage(sys.argv[0])
        sys.exit(1)

    extra = ''
    if len(sys.argv) >= 3:
        extra = sys.argv[2]

    res = parse(sys.argv[1])
    init(res, extra)
