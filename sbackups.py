#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Tue Nov  7 10:30:53 2017

@author: ustas
OAO Volga backup script 23.10.2014 Samonov Alexander
"""
import os
import logging
import socket
import zipfile
import time
import re
import shutil

# # Config section #############################################################

skip = [r'RECYCLE.BIN', r'\.tmp$', r'\.log$', r'Thumbs\.db$', r'desctop\.ini$', r'\.lnk$',
        r'event-log$', r'\.mp3$', r'\.wav$', r'\.ogg$', r'\.mkv$', r'\.iso$',
        r'\Volga\VOLGADB'
        ]

skip_zip = ['.png', '.jpg', '.wmf', '.avi', '.mpg', '.mov', '.mp3', '.ogg', '.mkv', '.fla', '.swf', '.rar',
            '.arj', '.arc', '.targz', '.7z', '.gz', '.bz', '.zip', '.tif', '.gif', '.dt', '.7zbk', '.iso']

logfile = "backup144.log"

config = {
    'OAOVOLGA': {
        'backup_path': "P:\\",
        'items': [{'root': "C:\\Users\\Администратор.OAOVOLGABAL\\Desktop", 'backup_path': ""},
                  {'root': "C:\\Users\\Администратор.OAOVOLGABAL\\Documents", 'backup_path': ""},
                  {'root': "C:\\Volga", 'backup_path': ""},
                  {'root': "J:\\Docs", 'backup_path': ""},
                  {'root': "I:\\Data\\Buhgalteria", 'backup_path': ""}
                  ],
        'skip': skip,
        'skip_zip': skip_zip,
        'unmount': True,
    },
    'GTX': {
        'backup_path': r"J:\my_backup",
        'items': [{'root': "D:\\", 'backup_path': ""},
                  {'root': r"C:\Users\ustas\Documents", 'backup_path': ""}],
        'skip': skip,
        'skip_zip': skip_zip,
        'unmount': True
    }
}

###############################################################################################################

logfile = os.path.join(backup_path, "backup144.log")


def backup_host(hostname, items, backup_path, skip, skip_zip):

    logging.info("Backup host " + hostname + " started.")

    for item in items:

        bk_path = backup_path
        if item['backup_path'] == "":
            bk_path = os.path.join(bk_path, os.path.basename(item['root']))
        elif item['backup_path'] == "-":
            pass
        else:
            bk_path = item['backup_path']

        logging.info("Current backup item: " + item['root'] + " to " + bk_path)

        for root, dirs, files in os.walk(item['root']):
            for name in files:
                do_skip = False
                for skip_item in skip:
                    if bool(re.search(skip_item, os.path.join(root, name), re.IGNORECASE)):
                        do_skip = True
                if not do_skip:
                    # logging.info("File - " + os.path.join(root, name))
                    try:
                        bak_cp(root, name, bk_path, item['root'])
                    except Exception, e:
                        logging.error("Error processing file " + os.path.join(root, name) + " " + str(e))
                else:
                    # logging.info("Skipped - " + os.path.join(root, name))
                    pass

    logging.info("Backup host " + hostname + " completed.")


def bak_cp(root, name, bkpath, bkroot, do_zip=True):
    rel_path = os.path.relpath(root, bkroot)
    target_path = os.path.join(bkpath, rel_path)

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    for skip_zip_item in skip_zip:
        if name.lower().endswith(skip_zip_item):
            do_zip = False

    src_filename = os.path.join(root, name)
    bak_filename_c = os.path.join(target_path, name)
    bak_filename = bak_filename_c + (".BAK.zip" if do_zip else "")

    src_filename_mtime = os.path.getmtime(src_filename)

    if os.path.isfile(bak_filename):

        bak_filename_mtime = os.path.getmtime(bak_filename)
        if abs(bak_filename_mtime - src_filename_mtime) < 0.0001:
            # print "Same modification time: " + src_filename
            return  # has no changed

        mtime_str = time.strftime('%d.%m.%Y_%H_%M_%S', time.localtime(bak_filename_mtime))
        new_name = bak_filename_c + "-" + mtime_str + (".BAK.zip" if do_zip else "")

        if os.path.isfile(new_name):
            os.remove(new_name)
        os.rename(bak_filename, new_name)

    logging.info("File : " + src_filename)

    if do_zip:
        zip_file = zipfile.ZipFile(bak_filename, 'w', zipfile.ZIP_DEFLATED)
        zip_file.write(src_filename, name)
        zip_file.close()
        shutil.copystat(src_filename, bak_filename)
    else:
        shutil.copy2(src_filename, bak_filename)


def test_deleted():
    pass


if __name__ == "__main__":

    if (not os.path.isdir(backup_path)):
        os.makedirs(backup_path)

    format = '%(asctime)s %(levelname)-8s %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        filename=logfile,
        level=logging.DEBUG,
        datefmt=datefmt,
        format=format)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(format))
    logging.getLogger().addHandler(ch)

    logging.info("")
    logging.info("Backuper started.")

    if socket.gethostname().lower() == hostname.lower():
        backup_host()

 