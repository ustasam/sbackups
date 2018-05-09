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


# # Config section ###########################################################################################

skip = [r'RECYCLE.BIN', r'\.tmp$', r'\.log$', r'Thumbs\.db$', r'desctop\.ini$', r'\.lnk$',
        r'event-log$', r'\.mp3$', r'\.wav$', r'\.ogg$', r'\.mkv$', r'\.iso$']

skip_compress = ['.png', '.jpg', '.wmf', '.avi', '.mpg', '.mov', '.mp3', '.ogg', '.mkv', '.fla', '.swf', '.rar',
                 '.arj', '.arc', '.targz', '.7z', '.gz', '.bz', '.zip', '.tif', '.gif', '.dt', '.7zbk', '.iso']

log_file = "sbackups.log"

config = {

    'default': {
        'path': r"\\oaovolga\users_backups\!hostname!",
        'items': [{'item': "!my_documents!", 'path': ""},
                  {'item': "!desktop!", 'path': ""},
                  {'item': "!disks!", 'path': ""}]
    },

    'oaovolga': {
        'path': "P:\\",
        'items': [{'item': "C:\\Users\\Администратор.OAOVOLGABAL\\Desktop", 'path': ""},
                  {'item': "C:\\Users\\Администратор.OAOVOLGABAL\\Documents", 'path': ""},
                  {'item': "C:\\Volga", 'path': ""},
                  {'item': "J:\\Docs", 'path': ""},
                  {'item': "I:\\Data\\Buhgalteria", 'path': ""}
                  ],
        'skip': skip + [r'\Volga\VOLGADB'],
        'skip_compress': skip_compress,
        'unmount': True
    },

    'gtx': {
        'path': r"J:\my_backup",
        'items': [{'item': "D:\\", 'path': ""},
                  {'item': r"C:\Users\ustas\Documents", 'path': ""}],
        'skip': skip,
        'skip_compress': skip_compress,
        'unmount': True
    }

}

compress = True
compression_extension = ".BAK.zip"
file_time_format = '%d.%m.%Y_%H_%M_%S'

log_format = '%(asctime)s %(levelname)-8s %(message)s'
log_dateformat = '%Y-%m-%d %H:%M:%S'

##############################################################################################################

debug = True

def backup_host(hostname, items, backup_path, skip, skip_compress_items):

    logging.info("Backup host " + hostname + " started.")

    for item in items:

        bak_path = backup_path
        if item['path'] == "":
            bak_path = os.path.join(bak_path, os.path.basename(item['item']))
        elif item['path'] == "-":
            pass
        else:
            bak_path = item['path']

        logging.info("Current backup item: " + item['item'] + " to " + bak_path)

        for root, dirs, files in os.walk(item['item']):
            for name in files:

                skip = False
                for skip_item in skip:
                    if bool(re.search(skip_item, os.path.join(root, name), re.IGNORECASE)):
                        skip = True

                item_compress = compress
                for skip_compress_item in skip_compress_items:
                    if name.lower().endswith(skip_compress_item):
                        item_compress = False

                if not skip:

                    logging.info("File : " + os.path.join(root, name))

                    try:
                        backup_file(root, name, bak_path, item['item'], item_compress)
                    except Exception, e:
                        logging.error("Error processing file " + os.path.join(root, name) + " " + str(e))
                else:
                    # logging.info("Skipped - " + os.path.join(root, name))
                    pass

    logging.info("Backup host " + hostname + " completed.")


def backup_file(root, name, bkpath, bkroot, compress=True):

    rel_path = os.path.relpath(root, bkroot)
    target_path = os.path.join(bkpath, rel_path)

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    src_filename = os.path.join(root, name)
    bak_filename_c = os.path.join(target_path, name)
    bak_filename = bak_filename_c + (".BAK.zip" if compress else "")

    src_filename_mtime = os.path.getmtime(src_filename)

    if not debug:

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

        if compress:
            zip_file = zipfile.ZipFile(bak_filename, 'w', zipfile.ZIP_DEFLATED)
            zip_file.write(src_filename, name)
            zip_file.close()
            shutil.copystat(src_filename, bak_filename)
        else:
            shutil.copy2(src_filename, bak_filename)


def backup(c, conf, docs=False):
    # mount
    print "backup"
    pass


def complicated():
    pass


def restore():
    pass


def clean_versions():
    pass


def mark_deleted():
    pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='Commands')

    backup_parser = subparsers.add_parser('backup', help='Backup operation')

    restore_parser = subparsers.add_parser('restore', help='Restore operation')
    restore_parser.add_argument('target', action='store', help='Restory target directory')
    restore_parser.add_argument('source', action='store', default=".", help='Source backup directory')

    clean_versions_parser = subparsers.add_parser('clean', help='Clean old versions operation')
    clean_versions_parser.add_argument('-source', action='store', default=".", help='Source backup directory')
    clean_versions_parser.add_argument('depth', action='store',
                                       type=int, default=-1, help='Version cleaning depth')

    mark_deleted_parser = subparsers.add_parser('mark', help='Mark deleted operation')
    mark_deleted_parser.add_argument('-source', action='store', default=".", help='Source backup directory')

    complicated_parser = subparsers.add_parser('complicated', help='Backup, mark, clean operation')
    complicated_parser.add_argument('depth', action='store',
                                    type=int, default=-1, help='Version cleaning depth')

    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    print parser.parse_args()





#
#     print 44
#
#     commands = ["backup", "restore", "clean_versions", "mark_deleted", "complicated"]
#
#     hostname = socket.gethostname()
#
#     # host configuration
#     host_conf = config['default']
#     if hostname in config:
#         host_conf = config[hostname]
#     elif hostname.lower() in config:
#         host_conf = config[hostname.lower()]
#     elif hostname.upper() in config:
#         host_conf = config[hostname.upper()]
#
#     # log configuration
#     conf_log_file = log_file
#     if "log_file" in host_conf:
#         conf_log_file =  host_conf["log_file"]
#     if not os.path.isabs(conf_log_file):
#         conf_log_file = os.path.join(host_conf['path'], conf_log_file)
#
#     logging.basicConfig(
#         filename=conf_log_file,
#         level=logging.DEBUG,
#         datefmt=log_dateformat,
#         format=log_format)
#
#     ch = logging.StreamHandler()
#     ch.setFormatter(logging.Formatter(log_format))
#     logging.getLogger().addHandler(ch)
#
#     logging.info("")
#     logging.info("Backuper started.")
#
#
#
#     a=1/0
#
#     # set configuration from defaults
#     print host_conf
#     # host_conf[]= host_conf[] if host_conf[] in host_conf else 33
#
#     print host_conf
#     #commands
#
#
#     error = ""
#     action = "backup"
#
#     if len(sys.argv) > 1:
#         action = sys.argv[1].lower()
#         logging.info("action " + action)
#
#     if action not in arguments:
#         action = "arguments"
#         error = "Unknown command."
#
#     if action == "arguments":
#         print('Arguments: ' + ", ".join(arguments) + '.')
#
#     elif action == "backup":
#         backup(host_conf)
#
#     elif action == "restore":
#         # restore(host_conf)
#         pass
#     elif action == "clean_versions":
#         # clean_versions(host_conf)
#         pass
#     elif action == "mark_deleted":
#         # mark_deleted(host_conf)
#         pass
#     elif action == "complicated":
#         backup(host_conf)
#         # clean_versions(host_conf)
#         # mark_deleted(host_conf)
#
#     if error != "":
#         print "Error: " + error
