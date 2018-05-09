#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Author: Samonov Alexander <ustasam@gmail.com>

"""
Simple backup script. Tue May 10 2018
"""
__version__ = '0.1 development'

import os
import sys
import logging
import socket
import zipfile
import time
import re
import shutil
import argparse

# ### Config section ###########################################################################################

default = {
    'path': r"\\oaovolga\users_backups\!hostname!",

    'items': [{'item': "!my_documents!", 'path': ""},  # TODO: remove 'path'
              {'item': "!desktop!", 'path': ""},
              {'item': "!disks!", 'path': ""}],

    'skip': [r'RECYCLE.BIN', r'\.tmp$', r'\.log$', r'Thumbs\.db$', r'desctop\.ini$', r'\.lnk$',
             r'event-log$', r'\.mp3$', r'\.wav$', r'\.ogg$', r'\.mkv$', r'\.iso$'],

    'skip_compress': ['.png', '.jpg', '.wmf', '.avi', '.mpg', '.mov', '.mp3', '.ogg', '.mkv',
                      '.fla', '.swf', '.rar', '.arj', '.arc', '.targz', '.7z', '.gz', '.bz',
                      '.zip', '.tif', '.gif', '.dt', '.7zbk', '.iso'],

    'log_file': "sbackups.log",

    'compress': True,
    'compress_extension': ".BAK.zip",
    'file_time_format': '%d.%m.%Y_%H_%M_%S',

    'log_format': r'%(asctime)s %(levelname)-8s %(message)s',
    'log_dateformat': r'%Y-%m-%d %H:%M:%S',

    'mount': False
    }

host_config = {

    'oaovolga': {  # oaovolga host config
        'path': "P:\\",
        'items': [{'item': "C:\\Users\\Администратор.OAOVOLGABAL\\Desktop", 'path': ""},
                  {'item': "C:\\Users\\Администратор.OAOVOLGABAL\\Documents", 'path': ""},
                  {'item': "C:\\Volga", 'path': ""},
                  {'item': "J:\\Docs", 'path': ""},
                  {'item': "I:\\Data\\Buhgalteria", 'path': ""}
                  ],
        'skip': default['skip'] + [r'\Volga\VOLGADB'],
        'mount': True
        },

    'gtx': {  # gtx host config
        'path': r'J:\my_new_backup',
        'items': [{'item': r'J:\james\small\_Chess', 'path': ""},
                  {'item': r'C:\Users\ustas\Documents', 'path': ""}]
        }
    }

##############################################################################################################
# TODO noprevious, nocompress,  nolog


def backup_host(config):  # , items, backup_path, skip, skip_compress_items):

    if config['path'] == "":
        config['path'] = default['path']

    for item in config['items']:

        bak_path = config['path']
        if item['path'] == "":
            bak_path = os.path.join(bak_path, os.path.basename(item['item']))
        elif item['path'] == "-":
            pass
        else:
            bak_path = item['path']

        # TODO: if quiet:
        logging.info("Current backup item: " + item['item'] + " to " + bak_path)

        for root, dirs, files in os.walk(item['item']):
            for name in files:

                skip = False
                for skip_item in config['skip']:
                    if bool(re.search(skip_item, os.path.join(root, name), re.IGNORECASE)):
                        skip = True

                item_compress = config['compress']
                for skip_compress in config['skip_compress']:
                    if name.lower().endswith(skip_compress):
                        item_compress = False

                if not skip:
                    try:
                        backup_file(root, name, bak_path, item['item'], item_compress)
                        pass
                    except Exception, e:
                        logging.error("Error processing file " + os.path.join(root, name) + " " + str(e))
                else:
                    # logging.info("Skipped - " + os.path.join(root, name))
                    pass


def backup_file(root, name, bkpath, bkroot, compress=True):

    rel_path = os.path.relpath(root, bkroot)
    target_path = os.path.join(bkpath, rel_path)

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    src_filename = os.path.join(root, name)
    bak_filename_c = os.path.join(target_path, name)
    bak_filename = bak_filename_c + (".BAK.zip" if compress else "")

    src_filename_mtime = os.path.getmtime(src_filename)

    if os.path.isfile(bak_filename):

        bak_filename_mtime = os.path.getmtime(bak_filename)
        if abs(bak_filename_mtime - src_filename_mtime) < 0.0001:
            # print "Same modification time: " + src_filename
            return  # has no changed

        mtime_str = time.strftime('%d.%m.%Y_%H_%M_%S', time.localtime(bak_filename_mtime))
        new_name = bak_filename_c + "-" + mtime_str + (".BAK.zip" if compress else "")

        if os.path.isfile(new_name):
            os.remove(new_name)
        os.rename(bak_filename, new_name)

    logging.info("File : " + os.path.join(root, name))

    if compress:
        zip_file = zipfile.ZipFile(bak_filename, 'w', zipfile.ZIP_DEFLATED)
        zip_file.write(src_filename, name)
        zip_file.close()
        shutil.copystat(src_filename, bak_filename)
    else:
        shutil.copy2(src_filename, bak_filename)


def backup(nocompress=False, noprevious=False):
    # TODO: mount

    config = get_config()

    logging.info("Backup host " + socket.gethostname() + " started.")

    backup_host(config)

    logging.info("Backup host " + socket.gethostname() + " completed.")


def restore():
    # config = get_config()
    pass


def clean_versions():
    # config = get_config()
    pass


def mark_deleted():
    # config = get_config()
    pass


def complicated():
    # config = get_config()
    pass


def get_config():
    hostname = socket.gethostname()

    host_conf = default
    if hostname in host_config:
        host_conf = host_config[hostname]
    elif hostname.lower() in host_config:
        host_conf = host_config[hostname.lower()]
    elif hostname.upper() in host_config:
        host_conf = host_config[hostname.upper()]

    for key, value in default.iteritems():
        if key not in host_conf:
            host_conf[key] = value

    return host_conf


if __name__ == "__main__":

    print ""
    if len(sys.argv) == 1:
        sys.argv.append("backup")  # default command

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    backup_parser = subparsers.add_parser('backup', help='Backup operation')
    backup_parser.add_argument('--nocompress', action='store_true',
                               default=False, help='Skip compress action')
    backup_parser.add_argument('--noprevious', action='store_true',
                               default=False, help='Delete previous versions')

    restore_parser = subparsers.add_parser('restore', help='Restore operation')
    restore_parser.add_argument('--target', '-t', action='store', help='Restory target directory')
    restore_parser.add_argument('--source', '-s', action='store', default=".", help='Source backup directory')

    clean_versions_parser = subparsers.add_parser('clean', help='Clean old versions operation')
    clean_versions_parser.add_argument('--source', '-s', action='store', default=".",
                                       help='Source backup directory')
    clean_versions_parser.add_argument('--depth', '-d', action='store',
                                       type=int, default=-1, help='Version cleaning depth')

    mark_deleted_parser = subparsers.add_parser('mark', help='Mark deleted operation')
    mark_deleted_parser.add_argument('--source', '-s', action='store', default=".",
                                     help='Source backup directory')

    complicated_parser = subparsers.add_parser('complicated', help='Backup, mark, clean operation')
    complicated_parser.add_argument('--depth', '-d', action='store',
                                    type=int, default=-1, help='Version cleaning depth')

    parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    # log configuration
    config = get_config()

    if not os.path.isabs(config['log_file']):
        config['log_file'] = os.path.join(config['path'], config['log_file'])

    if not os.path.exists(os.path.dirname(config['log_file'])):
        os.makedirs(os.path.dirname(config['log_file']))

    logging.basicConfig(
        filename=config['log_file'],
        level=logging.DEBUG,
        datefmt=config['log_dateformat'],
        format=config['log_format'])

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(config['log_format']))
    logging.getLogger().addHandler(ch)

    logging.info("")
    logging.info("Backuper started.")

    # execute command operation

    if args.command == "backup":
        backup(nocompress=args.nocompress, noprevious=args.noprevious)

    elif args.command == "restore":
        restore()

    elif args.command == "clean":
        clean_versions()

    elif args.command == "mark":
        mark_deleted()
        
    elif args.command == "complicated":
        backup()
        clean_versions()
        mark_deleted()
