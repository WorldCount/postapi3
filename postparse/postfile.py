#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import shutil
import hashlib
import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from . import errors
from . import PostHeader, PostString
from ..postgenerate import numfile
from ..postdata import opsinfo


__author__ = 'WorldCount'


"""
Класс почтового файла
"""


# Путь к пакету
_ROOT = os.path.dirname(__file__)
# Директория для временных файлов
TEMP = os.path.join(_ROOT, 'temp')
# Объект с данными по ОПС
_INFO = opsinfo.OpsInfo()
if not _INFO.load():
    _INFO.load_update()
    _INFO.save()

if not os.path.exists(TEMP):
    os.mkdir(TEMP)


# Сортировка по номеру
def sort_by_num(data):
    return data[0]


# Сортировка по ШПИ
def sort_by_barcode(post_string):
    return post_string['barcode']


# Класс почтового файла
class PostFile:

    # Конструктор
    def __init__(self, link, base_ops_num='127950'):
        #
        self._ind = -1
        # Ссылка на файл
        self._link = link
        # Номер базового ОПС
        self._base_ops_num = base_ops_num
        # Заголовок файла
        self._header = None
        # Количество столбцов в заголовке
        self._header_cols = 0
        # Возможно ошибочный
        self._warning = True
        # Дубликат
        self._double = False
        # Упакованный
        self._pack = False
        # Директория, имя файла
        self._dir_file, self._name_file = os.path.split(self._link)
        # Имя файла
        self._name = self._get_name_file()
        # Список отправлений
        self._list_mail = self._parse_file()
        # Количество строк в файле
        self._sum_string = len(self._list_mail)
        # Номер отделения
        self._ops_number = _INFO.ops_head_dict.get(self._list_mail[0]['INDEXOPER'], self._list_mail[0]['INDEXOPER'])
        # Хеш файла
        self._hash = self._get_hash()
        # Дата создания файла
        self._date_file = self._get_date_stamp()
        # Версия ПО
        self._version = self._get_version_file()

    # Метод: возвращает имя файла
    def _get_name_file(self):
        name = numfile.parse_name(self._name_file)
        if not name:
            raise errors.ParseNameError(self._link)
        else:
            return name

    # Метод: получает штам времени файла
    def _get_date_stamp(self):
        stamp = os.path.getmtime(self._link)
        return datetime.datetime.fromtimestamp(stamp)

    # Метод: Возвращает MD5-хеш файла
    def _get_hash(self):
        file_hash = hashlib.md5()
        data = self._list_mail[:]
        data.sort(key=sort_by_barcode)
        md_sum = ''.join([rpo[2] for rpo in data]).encode('utf-8')
        file_hash.update(md_sum)
        return file_hash.hexdigest()

    # Метод: открывает и парсит файл
    def _parse_file(self):
        with open(self._link, 'rb') as rpofile:
            return self._parse_list(rpofile)

    # Метод: парсит список
    def _parse_list(self, file_descriptor):
        # проверяем список на косяки
        check_list = self._check_list(file_descriptor)
        # если файл пустой
        if len(check_list) < 1:
            raise errors.EmptyPostFile(self._link)
        return check_list

    # Метод: проверяет список на косяки
    def _check_list(self, file_descriptor):
        rpo_list = []

        for num, line in enumerate(file_descriptor):
            tmp_line = line.decode('cp866').rstrip()

            if num == 0:
                self._header = PostHeader(tmp_line)
                self._header_cols = self._header.get_length()
            else:
                post_sting = PostString(self._header, tmp_line, num + 1)

                if not post_sting:
                    file_descriptor.close()
                    raise errors.ParseStringError(self._link, num + 1)

                if len(post_sting['barcode']) < 13:
                    file_descriptor.close()
                    raise errors.RpoNumNotFound(self._link, num + 1)
                else:
                    rpo_list.append(post_sting)
        file_descriptor.close()
        return rpo_list

    # Метод: возвращает версию файла
    def _get_version_file(self):
        if self._name[:6] == self._base_ops_num:
            return 'Base'

        list_version = []

        for num, row in enumerate(self._list_mail):
            ver = row['comment']['Version']
            if ver not in list_version:
                list_version.append(ver)

        ver_len = len(list_version)

        if ver_len > 1:
            split_version = []
            for ver in list_version:
                sp = ver[:2]
                if sp not in split_version:
                    split_version.append(sp)

            sp_len = len(split_version)

            if sp_len == 1:
                return max(list_version)
            elif sp_len > 1:
                nw_list = []
                for ver in list_version:
                    if ver[:2].upper() == 'NW':
                        nw_list.append(ver)
                return max(nw_list)
            else:
                return 'Unkown'
        else:
            return list_version[0]

    # Метод: сохраняет файл
    def save(self, file_path, pack=True):
        dir_name, file_name = os.path.split(file_path)
        temp_file = os.path.join(TEMP, file_name)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(temp_file, 'w', newline='', encoding='cp866') as save_file:
            writer = csv.writer(save_file, delimiter='|', quotechar='\n')
            writer.writerow(self._header.list())
            for row in self._list_mail:
                writer.writerow(row.list())

        if pack:
            with ZipFile(file_path, 'w', ZIP_DEFLATED) as my_zip:
                my_zip.write(temp_file, file_name)
        else:
            shutil.copy(temp_file, file_path)
        os.remove(temp_file)

    # Системный метод: размер данных
    def __len__(self):
        return len(self._list_mail)

    # Системный метод: получить значение элемента
    def __getitem__(self, item):
        if type(item) == int and len(self) > item >= 0:
            return self._list_mail[item]
        return False

    # Системный метод: установить значение элемента
    def __setitem__(self, item, value):
        if type(item) == int and len(self) > item >= 0 and type(value) is PostString:
            self._list_mail[item] = value

    # Системный метод: удалить значение элемента
    def __delitem__(self, item):
        if type(item) == int and len(self) > item >= 0:
            del self._list_mail[:][item]

    # Системный метод: данные в строку
    def __str__(self):
        return 'Файл: %s, версия: %s [строк: %s]' % (self.name, self.version, str(self.mail_sum))

    # Системный метод: вывод на консоль
    def __repr__(self):
        return str(self)

    # Системный метод: итератор
    def __iter__(self):
        return self

    # Системный метод: возвращает следующий элемент
    def __next__(self):
        if self._ind == len(self) - 1:
            self._ind = -1
            raise StopIteration
        self._ind += 1
        return self._list_mail[self._ind]

    # Свойство: возвращает имя файла
    @property
    def name(self):
        return self._name

    # Свойство: возвращает полное имя файла
    @property
    def name_raw(self):
        return self._name_file

    # Свойство: возвращает папку файла
    @property
    def dir(self):
        return self._dir_file

    # Свойство: устанавливает имя файла
    @name.setter
    def name(self, value):
        if value:
            self._name = value

    # Свойство: возвращает значение дубликата
    @property
    def double(self):
        return self._double

    # Свойство: устанавливает значение дубликата
    @double.setter
    def double(self, value):
        if value and type(value) is bool:
            self._double = value

    # Свойство: возвращает значение упаковки
    @property
    def pack(self):
        return self._pack

    # Свойство: устанавливает значение упаковки
    @pack.setter
    def pack(self, value):
        if value and type(value) is bool:
            self._pack = value

    # Свойство: возвращает значение предупреждения
    @property
    def warning(self):
        return self._warning

    # Свойство: устанавливает значение предупреждения
    @warning.setter
    def warning(self, value):
        if value and type(value) is bool:
            self._warning = value

    # Свойство: возвращает хеш файла
    @property
    def hash(self):
        return self._hash

    # Свойство: возвращает отправления в файле
    @property
    def mail_list(self):
        return self._list_mail

    # Свойство: устанавливает отправления файла
    @mail_list.setter
    def mail_list(self, mail_list):
        if type(mail_list) is list:
            self._list_mail = mail_list
            self._sum_string = len(mail_list)

    # Свойство: возвращает количество отправлений
    @property
    def mail_sum(self):
        return self._sum_string

    # Свойство: возвращает версию файла
    @property
    def version(self):
        return self._version

    # Свойство: возвращает заголовок файла списком
    @property
    def header_list(self):
        return self._header.list()

    # Свойство: возвращает заголовок файла строкой
    @property
    def header_string(self):
        return self._header.format()

    # Свойство: возвращает номер базового ОПС
    @property
    def base_ops_num(self):
        return self._base_ops_num

    # Свойство: возвращает дату создания файла
    @property
    def create_date(self):
        return self._date_file

    # Свойство: возвращает дату создания файла строкой
    @property
    def create_date_format(self):
        return self._date_file.strftime("%d.%m.%Y %H:%M:%S")

    # Свойство: возвращает ссылку на файл
    @property
    def link(self):
        return self._link

    # Свойство: возвращает номер ОПС
    @property
    def ops_num(self):
        return self._ops_number
