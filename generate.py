# -*- coding: utf-8 -*-

import argparse
import sqlite3
import random
import sys


def get_val(sql_cursor, query, list_arg=None):
    """
    Бывает полезно иметь функцию, которая при запросе,
    результатом которого является одна единственная
    ячейка, возвращает значение этой ячейки.
    Вот эта функция.
    """
    if list_arg is not None:
        sql_cursor.execute(query, list_arg)
    else:
        sql_cursor.execute(query)
    row = [item[0] for item in sql_cursor.fetchall()]
    return row[0]


def get_next_word(sql_cursor, current_word):
    """
    Получаем курсор и слово, для которого нужно найти
    следующее. Возвращаем, соответственно, следующее
    слово.
    """
    sql_cursor.execute("SELECT second, num FROM t"
                       " WHERE first = ?", (current_word, ))
    res_list = list()
    for row in sql_cursor.fetchall():
        res_list = res_list + ([row[0]] * row[1])
    if not (len(res_list) == 0):
        return random.choice(res_list)
    return None


def create_parser():
    """
    Функция, которая создает парсер для аргуентов. Ничего не принимает,
    возвращает argparse.ArgumentParser.
    """
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


def output_gen(output):
    """
    Функция, которая позволяет читать одинаково как из файла, так и
    из консоли. Принимает путь к файлу. Возвращает генератор, по
    которому можно проитерироваться и писать строки.
    """
    if output:
        with open(output, 'w') as f:
            yield f
    else:
        yield sys.stdout


def generate(args, cursor, word):
    """
    Функция, которая по входным данным, начинает решать
    задачу.
    """
    result = list()
    result.append(word)
    current_length = 1
    while current_length != args.length:
        word = get_next_word(cursor, word)
        if not word:
            break
        result.append(word)
        current_length += 1
    for out in output_gen(args.output):
        out.write(' '.join(result))
        out.write('\n')


if __name__ == '__main__':
    # Парсим аргументы
    parser = create_parser()
    args = parser.parse_args()
    connection_str = args.model
    conn = sqlite3.connect(connection_str)
    cursor = conn.cursor()
    word = ""
    random.seed()
    # Выбираем первое слово
    if args.seed:
        word = args.seed
        cursor.execute("SELECT count(id) "
                       "FROM t WHERE first = ? OR second = ?", (word, word))
        seed_exists = cursor.fetchall()[0][0]
        if seed_exists == 0:
            raise ValueError('Seed word does not exist')
    else:
        size = get_val(cursor, "SELECT count(id) FROM t")
        word = get_val(cursor,
                        "SELECT first FROM t WHERE id=?",
                        (random.randint(1, size), ))
    # Генерируем цепочку
    generate(args, cursor, word)
    conn.close()
