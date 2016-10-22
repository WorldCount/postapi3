#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

__author__ = 'WorldCount'


"""
Ошибки парсера почтовых файлов
"""


#
class PostError(Exception):

    def __init__(self, link='', more='', show_full_link=False):
        self.link = link
        self.dir_file = ''

        if show_full_link is False:
            self.dir_file, self.link = os.path.split(link)

        self.msg = 'Ошибка почтового файла'
        self.more = more

    def error_message(self):
        return '%s: %s' % (self.msg, self.link)

