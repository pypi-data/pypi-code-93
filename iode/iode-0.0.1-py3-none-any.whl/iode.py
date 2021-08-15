import os
import shutil
import argparse
import configparser

version = '0.0.1'
# default path

iode = {}

def listIode(args):
    global iode
    if args.iode_dir:
        if not os.path.exists(args.iode_dir):
            print(f'ERROR: Oops..! {args.iode_dir} is not found.')
            return -1
        iode['dir'] = args.iode_dir

    if not len(os.listdir(iode['dir'])):
        print(f'ERROR: Oops..! Directory is empty.')
        return -1

    for i in os.listdir(iode['dir']):
        codeDir = os.path.join(iode['dir'], i)
        userdataDir = os.path.join(codeDir, 'userdata')
        extensionsDir = os.path.join(codeDir, 'extensions')
        if os.path.exists(userdataDir) or os.path.exists(extensionsDir):
            print(i)
    return 0

def addIode(args):
    global iode
    if args.iode_dir:
        if not os.path.exists(args.iode_dir):
            print(f'ERROR: Oops..! {args.iode_dir} is not found.')
            return -1
        iode['dir'] = args.iode_dir

    codeDir = os.path.join(iode['dir'], args.env)
    userdataDir = os.path.join(codeDir, 'userdata')
    extensionsDir = os.path.join(codeDir, 'extensions')

    if not os.path.exists(iode['dir']):
        try:
            os.makedirs(iode['dir'])
        except OSError:
            print(f'ERROR: Oops..! Can not create iode directory.')
            return -1

    if os.path.exists(codeDir):
        print(f'ERROR: Oops..! {args.env} exists.')
        return -1

    try:
        os.makedirs(codeDir)
        os.makedirs(userdataDir)
        os.makedirs(extensionsDir)
    except OSError:
        print(f'ERROR: Oops..! Can not create {args.env}.')
        return -1

    print(f'SUCCESS: {args.env} is created!')
    return 0

def delIode(args):
    global iode

    if args.iode_dir:
        if not os.path.exists(args.iode_dir):
            print(f'ERROR: Oops..! {args.iode_dir} is not found.')
            return -1
        iode['dir'] = args.iode_dir
        
    codeDir = os.path.join(iode_dir, args.env)
    userdataDir = os.path.join(codeDir, 'userdata')
    extensionsDir = os.path.join(codeDir, 'extensions')

    if not os.path.exists(codeDir):
        print(f'ERROR: Oops..! {args.env} is not found.')
        return -1
    
    if not (os.path.exists(userdataDir) or os.path.exists(extensionsDir)):
        print(f'ERROR: Oops..! {args.env} is not iode-env.')
        return -1

    try:
        shutil.rmtree(codeDir)
    except OSError:
        print(f'ERROR: Oops..! Can not delete {args.env}.')
        return -1

    print(f'SUCCESS: {args.env} is deleted!')
    return 0

def runIode(args):
    global iode

    if args.iode_dir:
        if not os.path.exists(args.iode_dir):
            print(f'ERROR: Oops..! {args.iode_dir} is not found.')
            return -1
        iode['dir'] = args.iode_dir
        
    codeDir = os.path.join(iode['dir'], args.env)
    userdataDir = os.path.join(codeDir, 'userdata')
    extensionsDir = os.path.join(codeDir, 'extensions')

    if not os.path.exists(codeDir):
        print(f'ERROR: Oops..! {args.env} is not found.')
        return -1
    
    if not (os.path.exists(userdataDir) or os.path.exists(extensionsDir)):
        print(f'ERROR: Oops..! {args.env} is not iode-env.')
        return -1

    try:
        cmd = f'{iode["run"]} --user-data-dir {userdataDir} --extensions-dir {extensionsDir} {args.path}'
        os.system(cmd)
    except OSError:
        print(f'ERROR: Oops..! Can not delete {args.env}.')
        return -1

def parseConfig(iode):
    if os.path.exists(iode['conf']):
        config = configparser.ConfigParser()
        config.read(iode['conf'])
        try:
            iode['dir'] = config['default']['iode_dir']
        except KeyError:
            pass
        try:
            iode['run'] = config['default']['iode_run']
        except KeyError:
            pass
        return 0
    else:
        return -1

def main():
    global iode

    iode['run'] = 'code'
    iode['dir'] = os.path.join(os.path.expanduser('~'), 'iode')
    iode['conf'] = os.path.join(os.path.expanduser('~'), '.iode.conf')

    parseConfig(iode)

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=f'{version}')
    subparsers = parser.add_subparsers()

    cmd_add = subparsers.add_parser('add', aliases=['a'], help='Add environment.')
    cmd_add.add_argument('--iode-dir', '-d', help='set iode directory')
    cmd_add.add_argument('env')
    cmd_add.set_defaults(func=addIode)

    cmd_del = subparsers.add_parser('del', aliases=['d'], help='Delete environment.')
    cmd_del.add_argument('--iode-dir', '-d', help='set specified root dir')
    cmd_del.add_argument('env')
    cmd_del.set_defaults(func=delIode)

    cmd_list = subparsers.add_parser('list', aliases=['l'], help='Show environment list.')
    cmd_list.add_argument('--iode-dir', '-d', help='set specified root dir')
    cmd_list.set_defaults(func=listIode)

    cmd_run = subparsers.add_parser('run', aliases=['r'], help='run vscode with iode.')
    cmd_run.add_argument('--iode-dir', '-d', help='set specified root dir')
    cmd_run.add_argument('env')
    cmd_run.add_argument('path')
    cmd_run.set_defaults(func=runIode)
    
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.parse_args(['-h'])


if __name__ == '__main__':
    main()
