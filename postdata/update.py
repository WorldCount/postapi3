#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from zipfile import ZipFile
from dbfread import DBF
from grab import Grab

__author__ = 'WorldCount'


# Путь к пакету
_ROOT = os.path.dirname(__file__)
# Директория для временных файлов
TEMP = os.path.join(_ROOT, 'temp')
# Ожидание соединения
CONNECT_TIMEOUT = 15
# Ожидания ответа от сервера
TIMEOUT = 15
# Объект для запросов и парсинга
_GRAB = Grab()
_HEADERS = {'Accept-Language': 'ru-ru;q=0.9,ru,en;q=0.3'}
_GRAB.setup(connect_timeout=CONNECT_TIMEOUT, timeout=TIMEOUT, headers=_HEADERS)

URLS = {'index': 'http://vinfo.russianpost.ru/database/ops.html',
        'index_update': 'http://vinfo.russianpost.ru/database/',
        'news': 'http://vinfo.russianpost.ru/jsp/index.jsp',
        'land': 'https://tracking.pochta.ru/support/dictionaries/countries',
        'operation': 'https://tracking.pochta.ru/support/dictionaries/operation_codes',
        'mail_type': 'https://tracking.pochta.ru/support/dictionaries/mailtype',
        'mail_category': 'https://tracking.pochta.ru/support/dictionaries/category_codes',
        'mail_rank': 'https://tracking.pochta.ru/support/dictionaries/mailrank',
        'send_category': 'https://tracking.pochta.ru/support/dictionaries/send_ctg',
        'post_mark': 'https://tracking.pochta.ru/support/dictionaries/postmark'}


if not os.path.exists(TEMP):
    os.mkdir(TEMP)


# Получает данные по ссылке
def _get_code(url, to_dict=False):
    _GRAB.go(url)
    data = _GRAB.doc.select('//body//article[@class="page-help-article__content"]/table/tbody/tr')
    if len(data):
        res = []
        for num, row in enumerate(data):
            if num == 0:
                continue

            data_line = [col.text() for col in row.select('.//td')]

            if data_line:
                if '\xab' in data_line[1]:
                    data_line[1] = data_line[1].replace('\xab', '"')
                if '\xbb' in data_line[1]:
                    data_line[1] = data_line[1].replace('\xbb', '"')
                if '\u2013' in data_line[1]:
                    data_line[1] = data_line[1].replace('\u2013', '-')
                res.append(data_line)
        if to_dict:
            return dict(res)
        else:
            return res
    return False


# Получает последнюю дату обновления индексов
def get_last_index_update_date():
    _GRAB.go(URLS['index'])
    data = _GRAB.doc.select('//body/table[2]/tr[2]/td/table[3]/tr')
    if len(data):
        data.text()
        for_parse = data[-1]
        data = for_parse.select('.//td')
        return data[0].text()


# Получает последние новости
def get_last_news():
    _GRAB.go(URLS['news'])
    data = _GRAB.doc.select('//body/table[2]/tr[2]/td[1]/table/tr')
    if len(data):
        news = []
        for line in data[:-1]:
            part = line.select('.//td')
            date = part[0].text()
            body = part.select('.//font[@class="newsMessage"]').html()

            body = body.replace('<font class="newsMessage">', '')
            body = body.replace('</font>', '')
            body = body.strip()

            body = body.replace('\t', ' ')
            body = body.replace('    ', ' ')
            body = body.replace('   ', ' ')
            body = body.replace('  ', ' ')

            if '\xab' in body:
                body = body.replace('\xab', '')

            if '\xbb' in body:
                body = body.replace('\xbb', '')

            if '\u2022' in body:
                body = body.replace('\u2022', ' - ')

            if '\u2026' in body:
                body = body.replace('\u2026', '...')

            if '<a' in body:
                f_start = body.find('<a')
                f_end = body.rfind('>')
                full_link = body[f_start:f_end+1]
                l_start = full_link.find('>')
                l_end = full_link.rfind('<')
                link = full_link[l_start+1:l_end]
                body = body.replace(full_link, link)

            body = body.replace('<br><br>', '')
            body = body.replace('<br>', '')
            body = body.replace('<ul>', '')
            body = body.replace('</ul>', '')
            body = body.replace('<li>', ' - ')
            body = body.replace('</li>', '')
            body = body.replace(' Н', 'Н')

            news.append([date, body])
        return news
    return False


# Возвращает коды операций
def get_code_operation():
    _GRAB.go(URLS['operation'])
    data = _GRAB.doc.select('//body//article[@class="page-help-article__content"]/table/tbody/tr')
    res = []
    for num, row in enumerate(data):
        if num == 0:
            continue

        data_line = [col.text() for col in row.select('.//td')]
        if data_line:
            if '\xab' in data_line[1]:
                data_line[1] = data_line[1].replace('\xab', '"')
            if '\xbb' in data_line[1]:
                data_line[1] = data_line[1].replace('\xbb', '"')
            if '\u2013' in data_line[1]:
                data_line[1] = data_line[1].replace('\u2013', '-')
        if len(data_line) > 3:
            print(data_line)


# Возвращает коды видов отправлений
def get_code_mail_type(to_dict=False):
    return _get_code(URLS['mail_type'], to_dict)


# Возвращает коды категорий отправлений
def get_code_mail_category(to_dict=False):
    return _get_code(URLS['mail_category'], to_dict)


# Возвращает коды рангов отправлений
def get_code_mail_rank(to_dict=False):
    return _get_code(URLS['mail_rank'], to_dict)


# Возвращает коды категорий отправителей
def get_code_send_category(to_dict=False):
    return _get_code(URLS['send_category'], to_dict)


# Возвращает коды почтовых отметок
def get_code_post_mark(to_dict=False):
    return _get_code(URLS['post_mark'], to_dict)


# Получает данные по странам
def get_land_data():
    _GRAB.go(URLS['land'])
    data = _GRAB.doc.select('//body//article[@class="page-help-article__content"]/table/tbody/tr')
    if len(data):
        res = []
        for num, row in enumerate(data):
            if num == 0:
                continue

            text = row.text().split(' ')[0]
            if text == '0':
                continue

            nums = text.split('/')
            data_line = [col.text() for col in row.select('.//td')]
            if len(nums) > 1:
                for code in nums:
                    temp = [code,]
                    temp.extend(data_line[1:])
                    res.append(temp)
            else:
                res.append(data_line)
        return res
    return False


# Удаляет загруженный файл
def remove_temp_file(path_to_index_file):
    if os.path.exists(path_to_index_file):
        try:
            os.remove(path_to_index_file)
        except Exception:
            return False
        return True
    return None


# Получает обновление индексов
def get_index_update(load_dir, unpack=True):
    file_name = 'PIndx.zip'
    file_url = os.path.join(URLS['index_update'], file_name)
    temp_file_path = os.path.join(TEMP, file_name)

    if not os.path.exists(load_dir):
        os.makedirs(load_dir)

    try:
        _GRAB.go(file_url)
        _GRAB.response.save(temp_file_path)
    except Exception:
        return False

    if os.path.exists(temp_file_path):
        if unpack:
            with ZipFile(temp_file_path) as my_zip:
                name = my_zip.namelist()[0]
                my_zip.extractall(load_dir)
            link_to_file = os.path.join(load_dir, name)
        else:
            link_to_file = os.path.join(load_dir, file_name)
            shutil.copy(temp_file_path, link_to_file)
        # удаляем временный файл
        remove_temp_file(temp_file_path)
        return link_to_file
    else:
        return False


# Читает данные по индексам
def load_index(path_to_index_file):
    if os.path.exists(path_to_index_file):
        db_read = DBF(path_to_index_file)
        return db_read
    return False
