import os
import utils

class Builder(object):
    def __init__(self, name, data, folder):
        self.name = name
        self.data = data
        self.folder = folder
        self.build_dir = folder
        self.data = data
        self._build = data.get('build', '')
        self._configure = data.get('configure', '')
        self._test = data.get('test', '')

    def configure_cmake(self, real_run):
        # FIXME
        self.build_dir = self.folder + '/build'
        utils.check_dir(self.build_dir)
        if real_run:
            self.execute_list(['cmake %s' % (self.folder)], self.build_dir)

    def build_make(self):
        self.execute_list(['make'], self.build_dir)

    def execute_list(self, cmds, folder):
        for cmd in cmds:
            cmd = utils.replace_entries(cmd, self.data)
            print('cd "%s" && %s' % (folder, cmd))
            os.system('cd "%s" && %s' % (folder, cmd))

    def configure(self, real_run=True):
        print ('*** Configuring %s' % (self.name))
        if not os.path.isdir(self.folder):
            print('ERROR: Build folder not found, need to initialize?')
            return False

        if self._configure == '' and self._build == 'cmake':
            self._configure = 'cmake'
            if not self._build:
                self._build = 'make'
            if not self._test:
                self._test = 'make test'

        if self._configure == '':
            return True
        elif self._configure == 'cmake':
            self.configure_cmake(real_run=real_run)
        elif real_run and type(self._configure) == list:
            self.execute_list(self._configure, self.folder)
        elif real_run:
            self.execute_list([self._configure], self.folder)

        return True

    def build(self):
        print ('*** Building %s' % (self.name))
        if not os.path.isdir(self.folder):
            print('ERROR: Build folder not found, need to initialize?')
            return False

        if type(self._build) == list:
            self.execute_list(self._build, self.folder)
        elif self._build == '':
            pass
        elif self._build == 'cmake':
            self.build_make()
        elif self._build == 'make':
            self.build_make()
        else:
            raise ValueError('Unknown build system: %s' % (self.data))

        return True

    def test(self):
        print ('*** Testing %s' % (self.name))
        if not os.path.isdir(self.folder):
            print('ERROR: Build folder not found, need to initialize?')
            return False

        if self._test == '':
            pass
        elif type(self._test) == list:
            self.execute_list(self._test, self.build_dir)
        else:
            self.execute_list([self._test], self.build_dir)

        return True
