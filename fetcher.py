import os
import shutil
import utils

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

    def fetch_git(self, fetcher, source):
        source = utils.replace_entries(source, self.data)
        update = False
        if os.path.isdir(self.folder + '/.git'):
            if fetcher['branch']:
                os.system('cd "%s" && git checkout "%s"' % (self.folder, fetcher['branch']))
            os.system('cd "%s" && git pull' % (self.folder))
            update = True
        else:
            res = -1
            tries = 3
            while res != 0 and tries > 0:
                res = os.system('git clone "%s" "%s"' % (source, self.folder))
                if res != 0 and os.path.isdir(self.folder):
                    shutil.rmtree(self.folder, ignore_errors=True)
                tries -= 1

        if not update and os.path.isdir(self.folder):
            if fetcher['branch']:
                os.system('cd "%s" && git checkout -b "%s" "%s"' % (self.folder, os.path.basename(fetcher['branch']), fetcher['branch']))
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
                cmd = utils.replace_entries(cmd, self.data)
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
            cmd = utils.replace_entries(self.unpack, self.data)
            os.system('cd "%s" && "%s"' % (folder, cmd))

    def fetch_get(self, fetcher, source):
        utils.check_dir(self.folder)

        strip = 1
        # FIXME Utilize python
        if type(source) == list:
            for src in source:
                src = utils.replace_entries(src, self.data)
                os.system('cd "%s" && wget -c %s' % (self.folder, src))
                self.unpack_source(src, self.folder, strip)
                strip = 0
        else:
            src = utils.replace_entries(source, self.data)
            os.system('cd "%s" && wget -c %s' % (self.folder, src))
            self.unpack_source(src, self.folder, strip)

    def fetch_commands(self, fetcher):
        utils.check_dir(self.folder)
        for cmd in fetcher.commands:
            os.system('cd "%s" && %s' % (self.folder, cmd))

    def fetch(self):
        print ('*** Fetching %s' % (self.name))

        fetcher = self.parse_method()
        if fetcher['backend'] == 'git' or fetcher['backend'] == '':
            self.fetch_git(fetcher, self.source)
        elif fetcher['backend'] == 'get':
            self.fetch_get(fetcher, self.source)
        elif fetcher['commands']:
            self.fetch_commands(fetcher)
        else:
            raise ValueError('Unknown fetcher: %s' % (fetcher))

