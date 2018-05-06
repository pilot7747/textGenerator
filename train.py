# coding: utf-8

import sqlite3
import re
from sqlite3 import Error
import argparse
import os
import glob
import contextlib
import sys
import collections


# Класс, чтобы менять цвет шрифта в консоли
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Создаем файл модели
def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    finally:
        connection.close()


last_word = ""

model = collections.Counter()


def add_word(word1, word2):
    """
    Фунцкия, которая добавляет пару
    слов в модель. Пример использования:
    add_word('привет', 'мир')
    """
    global model
    model[(word1, word2)] += 1


def model_to_db(cursor):
    """
    Переводит модель из Counter в sqlite.
    Соответственно, ничего не возвращает,
    принимает collections.Counter.
    """
    global model
    for pair in model:
        squerry = "INSERT INTO t(first, second, num) VALUES (?, ?, ?)"
        cursor.execute(squerry, (pair[0], pair[1], model[pair]))


def add_row(text_line, to_lower):
    """
    Функция, которая обрабатывает строку текста и добавляет ее в
    модель. Принимает строку и флаг, который говорит, нужно ли ее
    перееводить в lower case.
    """
    if to_lower:
        text_line = text_line.lower()
    words = re.findall(r"[\w']+", re.sub('\d', ' ', text_line))
    current_ind = 0
    global last_word
    # Здесь соединяем последнее слово предыдущей строки
    # и первое слово новой.
    if last_word != "" and len(words) != 0:
        add_word(last_word, words[0])
    for word in words[:-1]:
        word1 = word
        word2 = words[current_ind + 1]
        add_word(word1, word2)
        current_ind = current_ind + 1
    if len(words) != 0:
        last_word = words[-1]


def create_parser():
    """
    Функция, которая создает парсер для аргуентов. Ничего не принимает,
    возвращает argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(description='Text generator.'
                                                 ' Use this script for'
                                                 ' generating model and after'
                                                 ' that generate.py'
                                                 ' for generating'
                                                 ' complete text.',
                                     add_help=True)
    parser.add_argument('--input-dir', action='store',
                        type=str, help='path to folder with input files')
    parser.add_argument('--model', action='store',
                        type=str, help='path to model file')
    parser.add_argument('--lc', action='store_true', help='to lower case')
    parser.add_argument('--file', action='store',
                        type=str, help='path to input file')
    return parser


def get_files_generator(args, input_path):
    """
    Функция, которая позволяет читать одинаково как из файла, так и
    из консоли. Принимает аргументы программы и путь к файлам.
    Возвращает генератор, по которому можно проитерироваться и читать
    строки.
    """
    file_list = list()
    # Если ввод с консоли
    if (input_path == "" or input_path is None) and args.file is None:
        yield sys.stdin
    # Вдруг указан конкретный файл
    if args.file:
        input_path = ""
        file_list.append(input_path + args.file)
    else:
        # Добавляем все txt в папках в список
        for top, dirs, files in os.walk(input_path):
            for directory in dirs:
                path = str(os.path.join(top, directory))
                file_list += glob.glob(path + "/*.txt")
        file_list += glob.glob(args.input_dir + "/*.txt")
    for file in file_list:
        with open(file) as f:
            yield f


def generate(args, input_path, conn):
    """
    Функция, которая по входным данным, начинает решать
    задачу.
    """
    cursor = conn.cursor()
    to_lower = args.lc
    # Непосредственно добавляем все построчно в модель
    for gen in get_files_generator(args, input_path):
        for line in gen:
            add_row(line, to_lower)
    model_to_db(cursor)
    conn.commit()
    'conn.close()'


if __name__ == '__main__':
    # Парсим аргументы
    parser = create_parser()
    args = parser.parse_args()
    input_path = args.input_dir
    connection_str = "model.sqlite"
    print(os.getcwd())
    # Если пользователь указал модель
    if args.model:
        connection_str = args.model
    if os.path.exists(connection_str):
        # Если такой файл уже есть, то удаляем
        os.remove(connection_str)
    # Коннектимся к бд
    with contextlib.closing(sqlite3.connect(connection_str)) as conn:
        conn.execute("CREATE TABLE t(id INTEGER PRIMARY KEY AUTOINCREMENT"
                     " NOT NULL, first TEXT, second TEXT, num INTEGER)")
        conn.commit()
        conn.execute("CREATE INDEX first_word_index ON t(first, second)")
        conn.commit()
        generate(args, input_path, conn)
    print(BColors.OKGREEN + 'Done! Model has '
                            'saved to ' + connection_str + BColors.ENDC)
