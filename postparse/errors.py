#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

__author__ = 'WorldCount'


"""
Ошибки парсера почтовых файлов
"""


# Общий класс для ошибок почтовых файлов
class PostError(Exception):

    def __init__(self, link=None, more=None, show_full_link=False):
        self.link = link
        self.dir_file = ''

        if show_full_link is False:
            self.dir_file, self.link = os.path.split(link)

        self.msg = 'Ошибка почтового файла'
        self.more = more

    def error_message(self):
        if self.more:
            return '%s: %s, сообщение: %s' % (self.msg, self.link, str(self.more))
        else:
            return '%s: %s' % (self.msg, self.link)


# Ошибка парсинга имени почтового файла
class ParseNameError(PostError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(ParseNameError, self).__init__(link, more, show_full_link)
        self.msg = 'Ошибка парсинга имени файла'


# ОШИБКИ ФАЙЛА
# Ошибка при работе с почтовым файлом
class PostFileError(PostError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(PostFileError, self).__init__(link, more, show_full_link)
        self.msg = 'Ошибка при работе с почтовым файлом'
        self.more = more


# Ошибка парсинга почтового файла. Файл пуст.
class EmptyPostFile(PostFileError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(EmptyPostFile, self).__init__(link, more, show_full_link)
        self.msg = 'Ошибка, файл пустой'


# Ошибка парсинга почтового файла. Не найден файл в архиве.
class FileInZipNotFound(PostFileError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(FileInZipNotFound, self).__init__(link, more, show_full_link)
        self.msg = 'Не найдено вложение в файле'


# Ошибка парсинга почтового файла. В файле больше 1 вложения.
class AttachInZipError(PostFileError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(AttachInZipError, self).__init__(link, more, show_full_link)
        self.msg = 'Больше одного вложения в архиве'


# Ошибка парсинга почтового файла. Ошибка типа почтового файла
class TypeFileError(PostFileError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(TypeFileError, self).__init__(link, more, show_full_link)
        self.msg = 'Неизвестный формат файла'


# ОШИБКИ ПАРСИНГА
# Ошибка парсинга почтового файла
class PostParseError(PostError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(PostParseError, self).__init__(link, more, show_full_link)
        self.msg = 'Ошибка парсинга файла'

    def error_message(self):
        if self.more:
            return '%s: %s, строка: %s' % (self.msg, self.link, str(self.more))
        else:
            return '%s: %s' % (self.msg, self.link)


# Ошибка парсинга строки почтового файла
class ParseStringError(PostParseError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(ParseStringError, self).__init__(link, more, show_full_link)
        self.msg = 'Ошибка парсинга строки'


# Ошибка парсинга почтового файла. Не найден номер РПО
class RpoNumNotFound(PostParseError):

    def __init__(self, link=None, more=None, show_full_link=False):
        super(RpoNumNotFound, self).__init__(link, more, show_full_link)
        self.msg = 'Не найден номер РПО'
