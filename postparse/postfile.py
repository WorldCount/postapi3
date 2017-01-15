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


__author__ = 'WorldCount'


"""
Класс почтового файла
"""


# Путь к пакету
_ROOT = os.path.dirname(__file__)
# Директория для временных файлов
TEMP = os.path.join(_ROOT, 'temp')

if not os.path.exists(TEMP):
    os.mkdir(TEMP)


# Сортировка по номеру
def sort_by_num(list):
    return list[0]


# Сортировка по ШПИ
def sort_by_barcode(post_string):
    return post_string['barcode']


# Класс почтового файла
class PostFile:

    # Конструктор
    def __init__(self, link, base_ops_num='127950'):
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
        self._ops_number = ''
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

    # Метод: открывает файл
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

    # Метод: возвращает заголовок файла
    def get_header(self):
        if self._header:
            return self._header.format()
        return False

    # Метод: возвращает дату создания файла
    def create_date(self):
        return self._date_file.strftime("%d.%m.%Y %H:%M:%S")

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

    # Метод: Сохраняет файл
    def save(self, file_path, pack=True):
        dir_name, file_name = os.path.split(file_path)
        temp_file = os.path.join(TEMP, file_name)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(temp_file, 'w', newline='', encoding='cp866') as save_file:
            writer = csv.writer(save_file, delimiter='|', quotechar='\n')
            writer.writerow(self._header._index)
            for row in self._list_mail:
                writer.writerow(row.list())

        if pack:
            with ZipFile(file_path, 'w', ZIP_DEFLATED) as my_zip:
                my_zip.write(temp_file, file_name)
        else:
            shutil.copy(temp_file, file_path)
        os.remove(temp_file)
