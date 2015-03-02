#!/usr/bin/env python
import argparse
import build
import fetcher
import os
import sys
import threading
import time
import utils


def handle_project(name, data, dir_name, args):
    utils.print_verb('* Project: %s' % name)
    actions = 0
    if args['all'] or args['init']:
        fetch = fetcher.DataFetcher(name, data, dir_name)
        fetch.fetch()
        actions += 1

    builder = build.Builder(name, data, dir_name)
    if args['all'] or args['configure']:
        if not builder.configure():
            return False
        actions += 1
    else:
        if not builder.configure(real_run=False):
            return False

    if args['all'] or args['build']:
        if not builder.build():
            return False
        actions += 1
    if args['all'] or args['test']:
        if not builder.test():
            return False
        actions += 1

    if actions == 0:
        print ('ERROR: No actions defined')
        return False

    return True


def init_project(name, proj, build_dir, args):
    res = True
    for item in proj:
        if not handle_project(item, proj[item], build_dir + '/' + item, args):
            print ('ERROR: Problem while handling %s' % (item))
            res = False

    return res


def init(config, args):
    build_dir = utils.solve_folder(args)

    res = True

    for item in config:
        if 'source' in config[item]:
            if not handle_project(item, config[item], build_dir + '/' + item, args):
                print ('ERROR: Problem while handling %s' % (item))
                res = False
        else:
            if not init_project(item, config[item], build_dir + '/' + item, args):
                res = False

    return res


def updater(config, args):
    while True:
        time.sleep(args['interval'])
        try:
            init(config, args)
        except:
            time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Blitz repos')
    parser.add_argument('config', type=argparse.FileType('r'), help='Config file as JSON')
    parser.add_argument('-f', '--folder', default='', help='Output folder')
    parser.add_argument('-i', '--init', action='store_true', help='Initialize only, download sources')
    parser.add_argument('-b', '--build', action='store_true', help='Build sources')
    parser.add_argument('-c', '--configure', action='store_true', help='Build sources')
    parser.add_argument('-t', '--test', action='store_true', help='Run tests')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval in seconds between updates')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose')
    parser.add_argument('-a', '--all', action='store_true', help='Perform all actions')

    basedir = os.path.dirname(os.path.realpath(__file__))
    if os.path.isfile(basedir + '/python-sshserver/sshserver.py'):
        parser.add_argument('-s', '--serve', action='store_true', help='Serve over SSH')
        parser.add_argument('--serve-port', default=2242, help='SSH server port')
        parser.add_argument('--serve-auth', default='', help='SSH auth file')
        sys.path.append(basedir + '/python-sshserver')

    res = parser.parse_args()

    args = vars(res)

    config = utils.parse(args['config'])
    args['config'].close()

    utils.set_print_verb(args['verbose'])

    if not init(config, args):
        sys.exit(1)

    if 'serve' in args and args['serve']:
        import serve
        upd = threading.Thread(target=updater, args=(config, args))
        upd.start()

        serve.serve(config, args)
