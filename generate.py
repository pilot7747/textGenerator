# -*- coding: utf-8 -*-
import argparse
import sqlite3
import random
import sys


def getnum(sqlCursor, query):
    sqlCursor.execute(query)
    row = [item[0] for item in sqlCursor.fetchall()]
    return row[0]


def getword(sqlCursor, query, listArg):
    sqlCursor.execute(query, listArg)
    row = [item[0] for item in sqlCursor.fetchall()]
    return row[0]


def getnextword(sqlCursor, currentWord):
    sqlCursor.execute("SELECT second, num FROM t WHERE first = ?", currentWord)
    reslist = list()
    for row in sqlCursor.fetchall():
        reslist = reslist + ([row[0]] * row[1])
    if not (len(reslist) == 0):
        return random.choice(reslist)
    return None


if __name__ == '__main__':
    print(sys.getdefaultencoding())
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, help='path to model file', required=True)
    parser.add_argument('--seed', type=str, help='first word, if not defined - random')
    parser.add_argument('--length', type=int, required=True, help='number of printed words')
    parser.add_argument('--output', help='path to output file, if not defined text will be printed to console')
    #args = parser.parse_args('--model model.sqlite --length 100'.split())
    args = parser.parse_args()
    connectionStr = args.model
    conn = sqlite3.connect(connectionStr)
    cursor = conn.cursor()
    size = getnum(cursor, "SELECT count(id) FROM t")
    print(size)
    word = ""
    random.seed()
    if args.seed:
        word = args.seed
    else:
        word = getword(cursor, "SELECT first FROM t WHERE id=?", (random.randint(1, size), ))
    result = word
    currentLength = 1
    end = False
    while currentLength != args.length and (not end):
        word = getnextword(cursor, (word, ))
        if not word:
            end = True
            break
        result = result + ' ' + word
        currentLength = currentLength + 1
    if args.output:
        file = open(args.output)
        file.write(result)
        file.close()
    else:
        print(result)
    conn.close()
