import os
import sshserver
import stat
import utils


class RepoServer(sshserver.SSHServer):
    def check_auth_publickey(self, username, key):
        if not self.key_handler.auth_file:
            # If not auth file always accept access
            self.username = username
            self.key = key
            return self.auth_success()

        return super(RepoServer, self).check_auth_publickey(username, key)


class RepoHandler(sshserver.SSHThread):
    def __init__(self, conn, key_handler, master):
        super(RepoHandler, self).__init__(conn, key_handler, master)
        self.server_class = RepoServer
        self.args = master.args
        self.build_dir = os.path.realpath(utils.solve_folder(self.args))

    def _validate_path(self, path):
        return not ('..' in path or not path.startswith(self.build_dir) or not os.path.exists(path))

    def sanitize(self, _path):
        path = os.path.realpath(_path)
        if not self._validate_path(path):
            path2 = os.path.realpath(self.build_dir + '/' + path)
            if not self._validate_path(path2):
                path3 = os.path.realpath(self.build_dir + '/' + _path)
                if not self._validate_path(path3):
                    return None

                return path3

            return path2

        return path

    def send(self, msg):
        self._channel.send('%s\r\n' % (msg))

    def list(self, paths):
        if not paths:
            paths.append(self.build_dir)

        for p in paths:
            sp = self.sanitize(p)
            if sp is None or not os.path.isdir(sp):
                self.send('ERROR: Invalid path: %s' % (p))
                return

            base = sp[len(self.build_dir):]
            for fn in [x for x in os.listdir(sp) if not x.startswith('.')]:
                self.send('%s/%s' % (base, fn))

    def send_file(self, fname):
        base = fname[len(self.build_dir):]
        self.send('File: %s' % (base))
        self.send('Size: %s' % (os.stat(fname).st_size))
        blocksize = 1024
        with open(fname, 'r') as fd:
            for chunk in iter(lambda: fd.read(blocksize), ''):
                self._channel.send(chunk)

    def stat_entry(self, fname):
        base = fname[len(self.build_dir):]
        data = os.stat(fname)

        typestr = 'ERR'
        if stat.S_ISDIR(data.st_mode):
            typestr = 'DIR'
        elif stat.S_ISLNK(data.st_mode):
            typestr = 'LINK'
        elif stat.S_ISREG(data.st_mode):
            typestr = 'FILE'
        elif stat.S_ISCHR(data.st_mode):
            typestr = 'CHAR'
        elif stat.S_ISBLK(data.st_mode):
            typestr = 'BLOCK'
        elif stat.S_ISFIFO(data.st_mode):
            typestr = 'FIFO'
        elif stat.S_ISSOCK(data.st_mode):
            typestr = 'SOCK'

        self.send('%s %s %s' % (typestr, data.st_size, base))

    def get(self, fname):
        for f in fname:
            sf = self.sanitize(f)
            if sf is None or not os.path.isfile(sf):
                self.send('ERROR: Invalid file: %s' % (f))
                return

            self.send_file(sf)

    def stat(self, fname):
        for f in fname:
            sf = self.sanitize(f)
            if sf is None or not os.path.exists(sf):
                self.send('ERROR: Invalid entry: %s' % (f))
                return

            self.stat_entry(sf)

    def ok(self):
        self.send('OK')

    def commands(self, cmd):
        parts = cmd.split(' ')
        if not parts:
            return

        if parts[0].lower() == '':
            return
        elif parts[0].lower() == 'list':
            self.ok()
            self.list(parts[1:])
        elif parts[0].lower() == 'get':
            self.ok()
            self.get(parts[1:])
        elif parts[0].lower() == 'stat':
            self.ok()
            self.stat(parts[1:])
        elif parts[0].lower() == 'exit':
            self.ok()
            self.running = False
        elif parts[0].lower() == 'help':
            self.ok()
            self.send('Commands:')
            self.send('   EXIT          Close connection')
            self.send('   HELP          This help')
            self.send('   LIST [dir]    List directory')
            self.send('   GET file      Get file contents')
        else:
            self.send('ERROR')

    def prompt(self):
        self._channel.send('> ')

    def handler(self):
        self.send('Blitz-repo')
        fd = self._channel.makefile('rU')

        self.prompt()
        data = ''
        while self.running:
            tmp = fd.read(1)
            if not tmp:
                self.running = False
                break
            if ord(tmp) == 4:
                self.running = False
            elif ord(tmp) == 127:  # Special backspace
                if data:
                    data = data[:-1]
                    self._channel.send('\b \b')
            elif tmp == '\n' or tmp == '\r':
                self._channel.send('\r\n')
                self.commands(data.strip())
                self.prompt()
                data = ''
            else:
                data += tmp
                self._channel.send(tmp)


def serve(config, args):
    key_handler = sshserver.SSHKeyHandler(auth_file=args['serve_auth'], host_key='~/.ssh/id_rsa')
    server = sshserver.ThreadedSSHServer(RepoHandler, key_handler, verbose=True, port=int(args['serve_port']))
    server.args = args
    server.start()
    server.join()
