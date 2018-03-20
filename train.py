import sqlite3
import re
from sqlite3 import Error
import argparse


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    finally:
        conn.close()

lastWord = ""

def addword(conn, cursor, word1, word2):
    cursor.execute("SELECT count(id) FROM t WHERE first = ? AND second = ?", (word1, word2))
    row = [item[0] for item in cursor.fetchall()]
    if row[0] == 0:
        cursor.execute("INSERT INTO t(first, second, num) VALUES(?, ?, 1)", (word1, word2))
    else:
        cursor.execute("UPDATE t SET num = num + 1 WHERE first = ? AND second = ?", (word1, word2))
    conn.commit()

def addRow(conn, cursor, line, toLower):
    if toLower:
        line = line.lower()
    line = re.sub('\d', ' ', line)
    words = re.findall(r"[\w']+", line)
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=str, help='path to input file')
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
    create_connection(connectionStr)
    conn = sqlite3.connect(connectionStr)
    conn.execute("CREATE TABLE t(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, first TEXT, second TEXT, num INTEGER)")
    conn.commit()
    cursor = conn.cursor()
    if inputPath != "":
        f = open(inputPath)
        for line in f.readlines():
            addRow(conn, cursor, line, toLower)
    else:
        while True:
            line = input()
            if not line:
                break
            addRow(conn, cursor, line, toLower)
    conn.close()
