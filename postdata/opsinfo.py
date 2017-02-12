#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
from . import update

__author__ = 'WorldCount'


# Генерирует данные по ОПС
class OpsInfo:

    def __init__(self, ops_head_num='127950'):
        self._root = os.path.dirname(__file__)
        self._ops_head_num = ops_head_num
        self._data_file = os.path.join(self._root, 'ops.pkl')
        self._index_data = None

        # Информация по данным
        self.info = {'last_update': '', 'update_link': ''}
        # Последняя дата обновления на сервере
        self._server_update_date = ''
        # Список ОПС: Короткие имена
        self.ops_short_list = []
        # Список ОПС: Длинные имена
        self.ops_long_list = []
        # Словарь ОПС: ОПС -> Список подчиненных ОПС
        self.ops_sub_dict = {}
        # Словарь ОПС: ОПС -> Главное ОПС
        self.ops_head_dict = {}
        # Словарь ОПС: Корокий номер ОПС -> Длинный номер ОПС
        self.ops_short_dict = {}
        # Словарь ОПС: Длинный номер ОПС -> Короткий номер ОПС
        self.ops_long_dict = {}

    # Метод: загружает данные из файла
    def load(self):
        if os.path.exists(self._data_file):
            with open(self._data_file, 'rb') as load_file:
                self.info = pickle.load(load_file)
                self.ops_short_list = pickle.load(load_file)
                self.ops_long_list = pickle.load(load_file)
                self.ops_sub_dict = pickle.load(load_file)
                self.ops_head_dict = pickle.load(load_file)
                self.ops_short_dict = pickle.load(load_file)
                self.ops_long_dict = pickle.load(load_file)
            return True
        return False

    # Метод: сохраняет данные в файл
    def save(self):
        if os.path.exists(self._data_file):
            os.remove(self._data_file)

        with open(self._data_file, 'wb') as save_file:
            pickle.dump(self.info, save_file, 2)
            pickle.dump(self.ops_short_list, save_file, 2)
            pickle.dump(self.ops_long_list, save_file, 2)
            pickle.dump(self.ops_sub_dict, save_file, 2)
            pickle.dump(self.ops_head_dict, save_file, 2)
            pickle.dump(self.ops_short_dict, save_file, 2)
            pickle.dump(self.ops_long_dict, save_file, 2)

    # Метод: возвращает дату последнего обновления на сервере
    def get_last_server_update_date(self):
        try:
            date = update.get_last_index_update_date()
            return date
        except Exception:
            return False

    # Метод: возвращает данные, требуется ли обновление
    def check_update_required(self):
        self._server_update_date = self.get_last_server_update_date()
        if self.info['last_update'] == self._server_update_date:
            return False
        return True

    # Метод: скачивает обновление
    def download_update(self):
        try:
            link = update.get_index_update(update.TEMP)
            self.info['update_link'] = link
            return True
        except Exception:
            return False

    # Метод: загружает данные по индексам
    def load_index_data(self):
        try:
            self._index_data = update.load_index(self.info['update_link'])
            return True
        except Exception:
            return False

    # Метод: заполняет списки ОПС данными
    def fill_ops_data(self):
        if self._index_data:
            self.ops_long_list = []
            self.ops_short_list = []
            self.ops_sub_dict = {}
            self.ops_head_dict = {}
            self.ops_short_dict = {}
            self.ops_long_dict = {}

            for line in self._index_data.records:
                # главное ОПС
                subs = line['OPSSUBM']
                index = line['INDEX']
                # если ОПС подчиняется главному
                if subs == self._ops_head_num:
                    # заполняем списки ОПС
                    ops_short = index[3:]
                    self.ops_long_list.append(index)
                    self.ops_short_list.append(ops_short)

                    self.ops_long_dict.update({index: ops_short})
                    self.ops_short_dict.update({ops_short: index})

                # если ОПС подчиняется главному или находится в подчинении главного
                if subs in self.ops_long_list or subs == self._ops_head_num:
                    # если в подчинении у главного
                    if subs == self._ops_head_num:
                        self.ops_head_dict.update({index: index})

                        if index in self.ops_sub_dict.keys():
                            self.ops_sub_dict[index].append(index)
                        else:
                            self.ops_sub_dict.update({index: [index, ]})
                        continue

                    self.ops_head_dict.update({index: subs})

                    if subs in self.ops_sub_dict.keys():
                        self.ops_sub_dict[subs].append(index)
                    else:
                        self.ops_sub_dict.update({subs: [index, ]})

    # Метод: генерирует данные
    def gen_all_data(self):
        load = self.load_index_data()
        if load:
            self.fill_ops_data()
            return True
        return False

    # Метод: загружает и обновляет данные
    def load_update(self):
        self._server_update_date = self.get_last_server_update_date()
        response = self.download_update()
        if response:
            update_result = self.gen_all_data()
            if update_result:
                self.info['last_update'] = self._server_update_date
                self.clear()
                return True
            return False
        return False

    # Метод: удаляет файл с индексами
    def clear(self):
        return update.remove_temp_file(self.info['update_link'])