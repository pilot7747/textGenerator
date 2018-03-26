# -*- coding: utf-8 -*-
import argparse
import sqlite3
import random


def get_num(sql_cursor, query):
    sql_cursor.execute(query)
    row = [item[0] for item in sql_cursor.fetchall()]
    return row[0]


def get_word(sql_cursor, query, list_arg):
    sql_cursor.execute(query, list_arg)
    row = [item[0] for item in sql_cursor.fetchall()]
    return row[0]


def get_next_word(sql_cursor, current_word):
    sql_cursor.execute("SELECT second, num FROM t WHERE first = ?", current_word)
    res_list = list()
    for row in sql_cursor.fetchall():
        res_list = res_list + ([row[0]] * row[1])
    if not (len(res_list) == 0):
        return random.choice(res_list)
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, help='path to model file', required=True)
    parser.add_argument('--seed', type=str, help='first word, if not defined - random')
    parser.add_argument('--length', type=int, required=True, help='number of printed words')
    parser.add_argument('--output', help='path to output file, if not defined text will be printed to console')
    args = parser.parse_args()
    connectionStr = args.model
    conn = sqlite3.connect(connectionStr)
    cursor = conn.cursor()
    size = get_num(cursor, "SELECT count(id) FROM t")
    word = ""
    random.seed()
    if args.seed:
        word = args.seed
    else:
        word = get_word(cursor, "SELECT first FROM t WHERE id=?", (random.randint(1, size), ))
    result = word
    currentLength = 1
    end = False
    while currentLength != args.length and (not end):
        word = get_next_word(cursor, (word, ))
        if not word:
            end = True
            break
        result = result + ' ' + word
        currentLength = currentLength + 1
    if args.output:
        file = open(args.output, 'w')
        file.write(result)
        file.close()
    else:
        print(result)
    conn.close()
