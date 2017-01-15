#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'WorldCount'
VERSION = '3.0.0'


# Заголовок файла
class PostHeader:

    def __init__(self, header_str=None):
        # Оригинальный заголовок
        self._header = header_str
        # Список с заголовками
        self._index = []
        # Список с данными
        self._data = []

        if self._header:
            self.parse_header(self._header)

    # Метод: парсит и устанавливает заголовок
    def parse_header(self, header):
        if type(header) == str:
            self._index = header.split('|')
            self._data = {key.upper(): '' for key in self._index}
            return True
        elif type(header) == list:
            self._index = header
            self._data = {key.upper(): '' for key in header}
            return True
        else:
            return False

    # Метод: возвращает список заголовков
    def get_header_index(self):
        return self._index

    # Метод: возвращает данные заголовков
    def get_header_data(self):
        return self._data

    # Метод: заголовок в строку
    def format(self):
        return '|'.join(self._index)


# Комментарий в строке почтового файла
class PostComment:

    def __init__(self, raw_comment=None):
        self._ind = -1
        self._data = {'Version': '', 'CountryFrom': '', 'Time': ''}
        self._index = ['Version', 'CountryFrom', 'Time']

        if raw_comment:
            self.parse(raw_comment)

    # Системный метод: Размер данных
    def __len__(self):
        return len(self._data)

    # Системный метод: Получить значение элемента
    def __getitem__(self, item):
        if item in self._data.keys():
            return self._data[item]
        return False

    # Системный метод: Установить значение элемента
    def __setitem__(self, item, value):
        if type(item) == str:
            if item in self._data.keys():
                self._data[item] = value
            else:
                self._data.update({item: value})

            if item not in self._index:
                self._index.append(item)

    # Системный метод: Удалить значение элемента
    def __delitem__(self, item):
        if type(item) == str:
            if item in self._data.keys():
                if item in ['Version', 'CountryFrom', 'Time']:
                    self._data[item] = ''
                else:
                    del self._index[self._index.index(item)]
                    del self._data[item]

    # Системный метод: Данные в строку
    def __str__(self):
        return self.format()

    # Системный метод: Вывод на консоль
    def __repr__(self):
        return self.format()

    # Системный метод: Итератор
    def __iter__(self):
        return self

    # Системный метод: Возвращает следующий элемент
    def __next__(self):
        if self._ind == len(self) - 1:
            self._ind = -1
            raise StopIteration
        self._ind += 1
        return self._index[self._ind]

    # Метод: Возвращает все ключи
    def keys(self):
        return self._index

    # Метод: Возвращает все значения
    def values(self):
        return self._data.values()

    # Метод: Парсит строку с комментарием
    def parse(self, comment_string):
        data = comment_string.split(';')

        for num, line in enumerate(data):

            if num == 0:
                self['Version'] = line
                continue

            comm = line.split('=')

            if len(comm) != 2:
                continue

            self[comm[0]] = comm[1]

    # Метод: Форматирует комментарий в формат почтового файла
    def format(self):
        for_str = []
        for num, ind in enumerate(self):
            if num == 0:
                for_str.append(str(self._data[ind]))
            else:
                value = self._data[ind]
                if value:
                    for_str.append('%s=%s' % (ind, value))

        return ';'.join(for_str)


# Класс строки почтового файла
class PostString:

    # Конструктор
    def __init__(self, header, raw_string=None, num_line=0):
        self._ind = -1
        # Комментарий в строке
        self._comment = PostComment()
        # Данные заголовков
        self._data = header.get_header_data()
        self._data['COMMENT'] = self._comment
        # Список заголовков
        self._index = header.get_header_index()
        # Номер строки
        self._num_line = num_line

        if raw_string:
            self.parse(raw_string, num_line)

    # Системный метод: Размер данных
    def __len__(self):
        return len(self._index)

    # Системный метод: Получить значение элемента
    def __getitem__(self, item):
        key = item
        if type(item) == int and len(self) > item >= 0:
                key = self._index[item]

        if type(key) == str and key.upper() in self._data.keys():
            return self._data[key.upper()]
        return False

    # Системный метод: Установить значение элемента
    def __setitem__(self, item, value):
        key = item
        if type(item) == int and (item < len(self) or item >= 0):
            key = self._index[item]

        if type(key) == str and key.upper() in self._data.keys():
            self._data[key.upper()] = value

    # Системный метод: Удалить значение элемента
    def __delitem__(self, item):
        key = item
        if type(item) == int and (item < len(self) or item >= 0):
            key = self._index[item]

        if type(key) == str and key.upper() in self._data.keys():
            self._data[key.upper()] = ''

    # Системный метод: Данные в строку
    def __str__(self):
        return '[Стр: %d] { ШПИ: %s, ОПС: %s, Дата: %s, Куда: %s, Вес: %s, Вид: %s, Категория: %s }' \
               % (self._num_line, self['Barcode'], self['IndexOper'], self['OperDate'], self['IndexTo'],
                  self['Mass'], self['MailType'], self['MailCtg'])

    # Системный метод: Вывод на консоль
    def __repr__(self):
        return str(self)

    # Системный метод: Итератор
    def __iter__(self):
        return self

    # Системный метод: Возвращает следующий элемент
    def __next__(self):
        if self._ind == len(self) - 1:
            self._ind = -1
            raise StopIteration
        self._ind += 1
        return self._index[self._ind]

    # Метод: Возвращает все ключи
    def keys(self):
        return self._index

    # Метод: Возвращает все значения
    def values(self):
        return self._data.values()

    # Метод: парсит строку
    def parse(self, text_string, line=0):
        self._num_line = line
        data = text_string.split('|')

        if len(self) != len(data):
            return False

        for num, ind in enumerate(self._index):
            if ind == 'COMMENT':
                self._data[ind].parse(data[num])
                continue
            self._data[ind] = data[num]

    # Метод: Форматирует данные в формат строки
    def format(self):
        for_str = []
        for ind in self:
            if ind == 'COMMENT':
                for_str.append(self._data[ind].format())
                continue
            for_str.append(self._data[ind])
        return '|'.join(for_str)

    @property
    def num(self):
        return self._num_line
