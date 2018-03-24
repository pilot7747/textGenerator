# -*- coding: utf-8 -*-
import sqlite3
import re
from sqlite3 import Error
import argparse
import sys
import os
import glob


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    finally:
        conn.close()

lastWord = ""


def addword(conn, cursor, word1, word2):
    cursor.execute("SELECT count(id) FROM t WHERE first = ? and second = ?", (word1, word2))
    row = cursor.fetchall()
    if row[0][0] == 0:
        cursor.execute("INSERT INTO t(first, second, num) VALUES (?, ?, 1)", (word1, word2))
    else:
        cursor.execute("UPDATE t SET num = num + 1 WHERE first = ? AND second = ?", (word1, word2))


def addRow(conn, cursor, line, toLower):
    if toLower:
        line = line.lower()
    words = re.findall(r"[\w']+", re.sub('\d', ' ', line))
    current = 0
    global lastWord
    if lastWord != "" and len(words) != 0:
        addword(conn, cursor, lastWord, words[0])
    for word in words[:-1]:
        word1 = word
        word2 = words[current + 1]
        addword(conn, cursor, word1, word2)
        current = current + 1
    if len(words) != 0:
        lastWord = words[-1]

if __name__ == '__main__':
    print(sys.getdefaultencoding())
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', action='store', type=str, help='path to folder with input files')
    parser.add_argument('--model', type=str, help='path to model file')
    parser.add_argument('--lc', action='store_true', help='to lower case')
    args = parser.parse_args()
    current = 0
    toLower = args.lc
    inputPath = ""
    connectionStr = "model.sqlite"
    inputPath = args.input_dir
    if args.model:
        connectionStr = args.model + "model.sqlite"
    try:
        os.remove(connectionStr)
        create_connection(connectionStr)
    except OSError:
        pass
    conn = sqlite3.connect(connectionStr)
    conn.execute("CREATE TABLE t(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, first TEXT, second TEXT, num INTEGER)")
    conn.commit()
    conn.execute("CREATE INDEX first_word_index ON t(first, second)")
    conn.commit()
    cursor = conn.cursor()

    if inputPath != "":
        filelist = glob.glob(inputPath + "*.txt")
        print(filelist)
        for filename in filelist:
            f = open(filename)
            currentposition = 0
            for line in f:
                addRow(conn, cursor, line, toLower)
                currentposition += 1
    else:
        while True:
            line = input()
            if not line:
                break
            addRow(conn, cursor, line, toLower)
    conn.commit()
    conn.close()
    print(BColors.OKGREEN + 'Done! Model has been saved to ' + connectionStr + BColors.ENDC)
