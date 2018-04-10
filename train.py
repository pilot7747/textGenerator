import sqlite3
import re
from sqlite3 import Error
import argparse
import os
import glob

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


lastWord = ""
model = ()
# Добавляем слово в модель


def addword(conn, cursor, word1, word2):
    squerry = "SELECT count(id) FROM t WHERE first = ? and second = ?"
    cursor.execute(squerry, (word1, word2))
    row = cursor.fetchall()
    if row[0][0] == 0:
        squerry = "INSERT INTO t(first, second, num) VALUES (?, ?, 1)"
        cursor.execute(squerry, (word1, word2))
    else:
        squerry = "UPDATE t SET num = num + 1 WHERE first = ? AND second = ?"
        cursor.execute(squerry, (word1, word2))
# Парсим строчку и добавляем ее по словам в модель


def add_row(connection, sql_cursor, text_line, to_lower):
    if to_lower:
        text_line = text_line.lower()
    words = re.findall(r"[\w']+", re.sub('\d', ' ', text_line))
    current_ind = 0
    global lastWord
    if lastWord != "" and len(words) != 0:
        addword(connection, sql_cursor, lastWord, words[0])
    for word in words[:-1]:
        word1 = word
        word2 = words[current_ind + 1]
        addword(conn, sql_cursor, word1, word2)
        current_ind = current_ind + 1
    if len(words) != 0:
        lastWord = words[-1]


if __name__ == '__main__':
    # Парсим аргументы
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', action='store',
                        type=str, help='path to folder with input files')
    parser.add_argument('--model', action='store',
                        type=str, help='path to model file')
    parser.add_argument('--lc', action='store_true', help='to lower case')
    parser.add_argument('--file', action='store',
                        type=str, help='path to input file')
    args = parser.parse_args()
    inputPath = args.input_dir
    connectionStr = "model.sqlite"
    # Если пользователь не указал модель
    if args.model:
        connectionStr = args.model
    try:
        # Если такой файл уже есть, то удаляем
        os.remove(connectionStr)
        create_connection(connectionStr)
    except OSError:
        pass
    # Коннектимся к бд
    conn = sqlite3.connect(connectionStr)
    conn.execute("CREATE TABLE t(id INTEGER PRIMARY KEY AUTOINCREMENT "
                 "NOT NULL, first TEXT, second TEXT, num INTEGER)")
    conn.commit()
    conn.execute("CREATE INDEX first_word_index ON t(first, second)")
    conn.commit()
    cursor = conn.cursor()
    toLower = args.lc
    if inputPath != "":
        file_list = list()
        # Вдруг указан конкретный файл
        if args.file:
            inputPath = ""
            file_list.append(inputPath + args.file)
        else:
            # Добавляем все txt в папках в список
            for top, dirs, files in os.walk(args.input_dir):
                for directory in dirs:
                    path = str(os.path.join(top, directory))
                    file_list += glob.glob(path + "/*.txt")
            file_list += glob.glob(args.input_dir + "/*.txt")
        # Непосредственно добавляем все построчно в модель
        for filename in file_list:
            f = open(filename)
            current_position = 0
            for line in f:
                add_row(conn, cursor, line, toLower)
                current_position += 1
    else:
        # Чтение с консоли
        while True:
            line = input()
            if not line:
                break
            add_row(conn, cursor, line, toLower)
    conn.commit()
    conn.close()
    print(BColors.OKGREEN + 'Done! Model has '
                            'saved to ' + connectionStr + BColors.ENDC)
