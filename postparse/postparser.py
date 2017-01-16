#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import postfile, packfile, errors


__author__ = 'WorldCount'


# Парсит почтовый файл
class PostParser:

    # Конструктор
    def __init__(self, link, base_ops_num='127950'):
        # Ссылка на файл
        self._link = link
        # Номер базового ОПС
        self._base_ops_num = base_ops_num
        # Архив, или нет
        self._pack = self.is_pack()
        # Объект для работы
        self._work_object = None

    # Метод: проверяет, является ли файл архивом
    def is_pack(self):
        with open(self._link, 'r', encoding='cp866') as f:
            symbol = f.read(2).lower()

        if symbol == 'op':
            return False
        elif symbol == 'pk':
            return True
        else:
            return None

    # Метод: загружает файл РПО, возвращает объект
    def load(self):
        if self._pack is True:
            my_object = packfile.PackFile(self._link, self._base_ops_num)
            my_object.pack = True
        elif self._pack is False:
            my_object = postfile.PostFile(self._link, self._base_ops_num)
            my_object.pack = False
        else:
            raise errors.TypeFileError(self._link)
        # Оставляем ссылку на объект себе
        self._work_object = my_object
        return my_object

    # Свойство: возвращает ссылку на файл
    @property
    def link(self):
        return self._link

    # Свойство: возвращает номер базового ОПС
    @property
    def base_ops_num(self):
        return self._base_ops_num

    # Свойство: устанавливает номер базового ОПС
    @base_ops_num.setter
    def base_ops_num(self, value):
        if value and type(value) == int:
            self._base_ops_num = str(value)
        elif value and type(value) == str:
            self._base_ops_num = value
        else:
            pass

    # Свойство: возвращает данные является ли файл архивом
    @property
    def pack(self):
        return self._pack

    # Свойство: возвращает созданный объект файла РПО
    @property
    def work_object(self):
        return self._work_object
