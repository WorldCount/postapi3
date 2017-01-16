#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import postfile, errors
from zipfile import ZipFile


__author__ = 'WorldCount'


# Класс запакованного почтового файла
class PackFile(postfile.PostFile):

    # Конструктор
    def __init__(self, link, base_ops_num='127950'):
        super(PackFile, self).__init__(link, base_ops_num)
        self._warning = False
        self._pack = True

    # Метод: открывает и парсит файл
    def _parse_file(self):
        with ZipFile(self._link) as my_zip:
            if len(my_zip.namelist()) > 1:
                raise errors.AttachInZipError(self._link)
            try:
                f = my_zip.namelist()[0]
                return self._parse_list(my_zip.open(f))
            except IndexError:
                raise errors.FileInZipNotFound
