# -*- coding: utf-8 -*-

import argparse
import sqlite3
import random

# Функция, которая при запросе, возвращающем одно
# единственное значение, возвращает это значение


def get_num(sql_cursor, query):
    sql_cursor.execute(query)
    row = [item[0] for item in sql_cursor.fetchall()]
    return row[0]

# Достаем слово из модели


def get_word(sql_cursor, query, list_arg):
    sql_cursor.execute(query, list_arg)
    row = [item[0] for item in sql_cursor.fetchall()]
    return row[0]

# Находим следующее слово цепочки


def get_next_word(sql_cursor, current_word):
    sql_cursor.execute("SELECT second, num FROM t"
                       " WHERE first = ?", (current_word, ))
    res_list = list()
    for row in sql_cursor.fetchall():
        res_list = res_list + ([row[0]] * row[1])
    if not (len(res_list) == 0):
        return random.choice(res_list)
    return None


# Создаем парсер
def create_parser():
    parser = argparse.ArgumentParser(description='Text generator.'
                                                 ' Use this train.py for'
                                                 ' generating model and after'
                                                 ' that use this script'
                                                 ' for generating'
                                                 ' complete text.',
                                     add_help=True)
    parser.add_argument('--model', action='store', type=str,
                        help='path to model file', required=True)
    parser.add_argument('--seed', action='store', type=str,
                        help='first word, if not defined - random')
    parser.add_argument('--length', action='store', type=int,
                        required=True, help='number of printed words')
    parser.add_argument('--output', action='store',
                        help='path to output file, '
                             'if not defined text will be printed to console')
    return parser


# Генерация текста
def generate(args, cursor, word):
    result = list()
    result.append(word)
    currentLength = 1
    while currentLength != args.length:
        word = get_next_word(cursor, word)
        if not word:
            break
        result.append(word)
        currentLength += 1
    if args.output:
        with open(args.output, 'w') as file:
            file.write(' '.join(result))
            file.close()
    else:
        print(' '.join(result))


if __name__ == '__main__':
    # Парсим аргументы
    parser = create_parser()
    args = parser.parse_args()
    connectionStr = args.model
    conn = sqlite3.connect(connectionStr)
    cursor = conn.cursor()
    word = ""
    random.seed()
    # Выбираем первое слово
    if args.seed:
        word = args.seed
        cursor.execute("SELECT count(id) "
                       "FROM t WHERE first = ? OR second = ?", (word, word))
        seedExists = cursor.fetchall()[0][0]
        if seedExists == 0:
            raise ValueError('Seed word does not exist')
    else:
        size = get_num(cursor, "SELECT count(id) FROM t")
        word = get_word(cursor,
                        "SELECT first FROM t WHERE id=?",
                        (random.randint(1, size), ))
    # Генерируем цепочку
    generate(args, cursor, word)
    conn.close()
