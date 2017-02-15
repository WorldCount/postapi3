#!/usr/bin/env python
# -*- coding: utf-8 -*-

from suds.client import Client
from suds.bindings import binding
from suds import WebFault

__author__ = 'WorldCount'

DEBUG = False


if DEBUG:
    import sys, logging

    logger = logging.getLogger()
    logger.root.setLevel(logging.CRITICAL)
    logger.root.addHandler(logging.StreamHandler(sys.stdout))


SIMPLE_FIELDS = {'IndexOper': 'Индекс места операции', 'AddressOper': 'Адрес места операции',
                 'IndexTo': 'Индекс места назначения', 'AddressTo': 'Адрес места назначения',
                 'MailDirect': 'Код страны назначения', 'MailDirectName': 'Название страны назначения',
                 'CountryFrom': 'Код страны операции', 'CountryFromName': 'Название страны операции',
                 'Payment': 'Наложенный платеж в коп.', 'Value': 'Объявленная ценность в коп.',
                 'MassRate': 'Плата за пересылку в коп.', 'InsrRate': 'Плата за ОЦ в коп.',
                 'AirRate': 'Плата за АВИА в коп.', 'Rate': 'Доп.сбор в коп.', 'CustomDuty': 'Таможенный платеж в коп.',
                 'Barcode': 'Штрих-Код', 'Internum': 'Служебная информация', 'MailName': 'Название отправления',
                 'MailRank': 'Разряд отправления', 'MailRankName': 'Имя разряда отправления',
                 'PostMark': 'Почтовая отметка', 'PostMarkName': 'Имя почтовой отметки',
                 'MailType': 'Вид отправления', 'MailTypeName': 'Имя вида отправления',
                 'MailCtg': 'Категория отправления', 'MailCtgName': 'Имя категории отправления',
                 'Mass': 'Вес отправления в граммах', 'OperType': 'Код операции', 'OperTypeName': 'Имя операции',
                 'OperAttr': 'Атрибут операции', 'OperAttrName': 'Имя атрибута операции', 'OperDate': 'Дата операции',
                 'SendCtg': 'Категория отправителя', 'SendCtgName': 'Имя категории отправителя',
                 'Sndr': 'Отправитель', 'Rcpn': 'Получатель'}

PAYMENT_FIELDS = {'Number': 'Номер перевода', 'EventName': 'Название операции', 'EventDateTime': 'Дата операции',
                  'EventType': 'Код операции', 'IndexTo': 'Индекс получателя', 'IndexEvent': 'Индекс места операции',
                  'SumPaymentForward': 'Наложенный платеж в коп.',
                  'CountryEventCode': 'Страна операции', 'CountryToCode': 'Страна получателя'}

PACK_OPERATION_FIELDS = {'OperTypeID': 'Код операции', 'OperCtgID': 'Атрибут операции', 'OperName': 'Имя операции',
                         'DateOper': 'Дата операции', 'IndexOper': 'Индекс места операции'}


# Класс: Клиент единичного доступа
class SimpleTrackClient:

    # Конструктор
    def __init__(self, login, password, url):
        """
        :param login: логин на сервисе трекинга Почты России
        :param password: пароль на сервисе трекинга Почты России
        :param url: ссылка к wsdl описанию сервиса
        """

        self.login = login
        self.password = password
        self.url = url
        # Заголовки
        self.headers = {'Content-Type': 'application/soap+xml; charset="UTF-8"'}
        binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        # Создаем SOAP-Клиент
        self.api = Client(self.url, username=self.login, password=self.password, headers=self.headers)
        # Создаем заголовок авторизации для запросов
        self.auth = self._get_auth()
        # Создаем объект OperationHistoryRequest для запроса
        self.operation_history = self._get_operation_history_query()
        # Создаем объект PostalOrderEventsForMailInput для запроса
        self.payment_history = self._get_payment_history_query()

    # Метод: Возвращает распарсенный ответ от сервера
    def check_barcode(self, barcode):
        response = self._get_raw_barcode_info(barcode)
        if not response:
            return False
        else:
            return self._parse_tracking_response(response)

    # Метод: Возвращает распарсенный ответ от сервера
    def check_payment(self, barcode):
        response = self._get_raw_payment_info(barcode)
        if not response:
            return False
        else:
            return self._parse_payment_response(response)

    # Метод: Возвращает заголовок авторизации
    def _get_auth(self):
        auth = self.api.factory.create('getOperationHistory.AuthorizationHeader')
        auth.login, auth.password = self.login, self.password
        return auth

    # Метод: Возвращает запрос на историю операции
    def _get_operation_history_query(self):
        query = self.api.factory.create('getOperationHistory.OperationHistoryRequest')
        query.MessageType, query.Language = 0, 'RUS'
        return query

    # Метод: Возвращает запрос на историю операции
    def _get_payment_history_query(self):
        query = self.api.factory.create('PostalOrderEventsForMail.PostalOrderEventsForMailInput')
        return query

    # Метод: Возвращает сырой ответ от сервера
    def _get_raw_barcode_info(self, barcode):
        if len(barcode) < 14 and barcode[1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return False
        self.operation_history.Barcode = barcode
        try:
            response = self.api.service.getOperationHistory(self.operation_history, self.auth)
        except WebFault as e:
            return False
        return response

    # Метод: Возвращает сырой ответ от сервера
    def _get_raw_payment_info(self, barcode):
        if len(barcode) < 14 and barcode[1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return False
        self.payment_history._Barcode = barcode
        try:
            response = self.api.service.PostalOrderEventsForMail(self.auth, self.payment_history)
        except WebFault:
            return False
        return response

    # Метод: Парсит ответ от сервера
    def _parse_payment_response(self, response):
        # Если есть ошибка, то заканчиваем работу
        if not response or 'error' in response:
            return False

        # Если есть записи
        if 'PostalOrderEvent' in response:
            data = []
            for record in response.PostalOrderEvent:
                temp = {'Number': '', 'EventName': '', 'EventDateTime': '', 'EventType': '', 'IndexTo': '',
                        'IndexEvent': '', 'SumPaymentForward': '', 'CountryEventCode': '', 'CountryToCode': ''}

                try:
                    # Название операции
                    temp['EventName'] = record._EventName
                except AttributeError:
                    pass

                try:
                    # Дата и время операции
                    temp['EventDateTime'] = record._EventDateTime
                except AttributeError:
                    pass

                try:
                    # Страна получателя
                    temp['CountryToCode'] = record._CountryToCode
                except AttributeError:
                    pass

                try:
                    # Сумма наложенного платежа
                    temp['SumPaymentForward'] = record._SumPaymentForward
                except AttributeError:
                    pass

                try:
                    # Страна отправителя
                    temp['CountryEventCode'] = record._CountryEventCode
                except AttributeError:
                    pass

                try:
                    # Почтовый индекс получателя
                    temp['IndexTo'] = record._IndexTo
                except AttributeError:
                    pass

                try:
                    # Код операции
                    temp['EventType'] = record._EventType
                except AttributeError:
                    pass

                try:
                    # Почтовый индекс места операции
                    temp['IndexEvent'] = record._IndexEvent
                except AttributeError:
                    pass

                try:
                    # Номер почтового перевода
                    temp['Number'] = record._Number
                except AttributeError:
                    pass

                data.append(temp)
            return data
        return False

    # Метод: Парсит ответ от сервера
    def _parse_tracking_response(self, response):
        # Если есть ошибка, то заканчиваем работу
        if not response or 'error' in response:
            return False

        # Если есть записи
        if 'historyRecord' in response:
            data = []
            # Перебираем их
            for record in response.historyRecord:
                temp = {'IndexOper': '', 'AddressOper': '', 'IndexTo': '', 'AddressTo': '',
                        'MailDirect': '', 'MailDirectName': '', 'CountryFrom': '', 'CountryFromName': '',
                        'Payment': '', 'Value': '', 'MassRate': '', 'InsrRate': '', 'AirRate': '',
                        'Rate': '', 'CustomDuty': '', 'Barcode': '', 'Internum': '', 'MailName': '',
                        'MailRank': '', 'MailRankName': '', 'PostMark': '', 'PostMarkName': '',
                        'MailType': '', 'MailTypeName': '', 'MailCtg': '', 'MailCtgName': '',
                        'Mass': '', 'OperType': '', 'OperTypeName': '', 'OperAttr': '', 'OperAttrName': '',
                        'OperDate': '', 'SendCtg': '', 'SendCtgName': '', 'Sndr': '', 'Rcpn': ''}

                # Индекс и название места операции
                if 'OperationAddress' in record.AddressParameters:
                    try:
                        # Индекс места операции
                        temp['IndexOper'] = record.AddressParameters.OperationAddress.Index
                    except AttributeError:
                        pass

                    try:
                        # Адрес места операции
                        temp['AddressOper'] = record.AddressParameters.OperationAddress.Description
                    except AttributeError:
                        pass

                # Индекс и название места назначения
                if 'DestinationAddress' in record.AddressParameters:
                    try:
                        # Индекс места назначения
                        temp['IndexTo'] = record.AddressParameters.DestinationAddress.Index
                    except AttributeError:
                        pass

                    try:
                        # Адрес места назначения
                        temp['AddressTo'] = record.AddressParameters.DestinationAddress.Description
                    except AttributeError:
                        pass

                # Код и название страны назначения
                if 'MailDirect' in record.AddressParameters:
                    try:
                        # Код страны назначения
                        temp['MailDirect'] = record.AddressParameters.MailDirect.Id
                    except AttributeError:
                        pass

                    try:
                        # Название страны назначения
                        temp['MailDirectName'] = record.AddressParameters.MailDirect.NameRU
                    except AttributeError:
                        pass

                # Код и название страны операции
                if 'CountryOper' in record.AddressParameters:
                    try:
                        # Код страны операции
                        temp['CountryFrom'] = record.AddressParameters.CountryOper.Id
                    except AttributeError:
                        pass

                    try:
                        # Название страны операции
                        temp['CountryFromName'] = record.AddressParameters.CountryOper.NameRU
                    except AttributeError:
                        pass

                # Наложка, ОЦ и сборы
                if 'FinanceParameters' in record:
                    try:
                        # Наложка
                        temp['Payment'] = record.FinanceParameters.Payment
                    except AttributeError:
                        pass

                    try:
                        # Ценность
                        temp['Value'] = record.FinanceParameters.Value
                    except AttributeError:
                        pass

                    try:
                        # Плата за пересылку
                        temp['MassRate'] = record.FinanceParameters.MassRate
                    except AttributeError:
                        pass

                    try:
                        # Плата за ОЦ
                        temp['InsrRate'] = record.FinanceParameters.InsrRate
                    except AttributeError:
                        pass

                    try:
                        # Плата за АВИА
                        temp['AirRate'] = record.FinanceParameters.AirRate
                    except AttributeError:
                        pass

                    try:
                        # Доп.сбор
                        temp['Rate'] = record.FinanceParameters.Rate
                    except AttributeError:
                        pass

                    try:
                        # Таможенный сбор
                        temp['CustomDuty'] = record.FinanceParameters.CustomDuty
                    except AttributeError:
                        pass

                # Параметры отправления
                if 'ItemParameters' in record:
                    try:
                        # ШПИ
                        temp['Barcode'] = record.ItemParameters.Barcode
                    except AttributeError:
                        pass

                    try:
                        # Служебная информация
                        temp['Internum'] = record.ItemParameters.Internum
                    except AttributeError:
                        pass

                    try:
                        # Полное название отправления
                        temp['MailName'] = record.ItemParameters.ComplexItemName
                    except AttributeError:
                        pass

                    try:
                        # Код разряда отправления
                        temp['MailRank'] = record.ItemParameters.MailRank.Id
                    except AttributeError:
                        pass

                    try:
                        # Имя разряда отправления
                        temp['MailRankName'] = record.ItemParameters.MailRank.Name
                    except AttributeError:
                        pass

                    try:
                        # Код вида отправления
                        temp['MailType'] = record.ItemParameters.MailType.Id
                    except AttributeError:
                        pass

                    try:
                        # Имя вида отправления
                        temp['MailTypeName'] = record.ItemParameters.MailType.Name
                    except AttributeError:
                        pass

                    try:
                        # Код категории отправления
                        temp['MailCtg'] = record.ItemParameters.MailCtg.Id
                    except AttributeError:
                        pass

                    try:
                        # Имя категории отправления
                        temp['MailCtgName'] = record.ItemParameters.MailCtg.Name
                    except AttributeError:
                        pass

                    try:
                        # Код отметки
                        temp['PostMark'] = record.ItemParameters.PostMark.Id
                    except AttributeError:
                        pass

                    try:
                        # Название отметки
                        temp['PostMarkName'] = record.ItemParameters.PostMark.Name
                    except AttributeError:
                        pass

                    try:
                        # Вес отправления
                        temp['Mass'] = record.ItemParameters.Mass
                    except AttributeError:
                        pass

                # Параметры операции
                if 'OperationParameters' in record:
                    try:
                        # Код операции
                        temp['OperType'] = record.OperationParameters.OperType.Id
                    except AttributeError:
                        pass

                    try:
                        # Имя операции
                        temp['OperTypeName'] = record.OperationParameters.OperType.Name
                    except AttributeError:
                        pass

                    try:
                        # Атрибут
                        temp['OperAttr'] = record.OperationParameters.OperAttr.Id
                    except AttributeError:
                        pass

                    try:
                        # Атрибут
                        temp['OperAttrName'] = record.OperationParameters.OperAttr.Name
                    except AttributeError:
                        pass

                    try:
                        # Дата операции
                        temp['OperDate'] = record.OperationParameters.OperDate
                    except AttributeError:
                        pass

                # Параметры получателя и отправителя
                if 'UserParameters' in record:
                    try:
                        # Код категории отправителя
                        temp['SendCtg'] = record.UserParameters.SendCtg.Id
                    except AttributeError:
                        pass

                    try:
                        # Название категории отправителя
                        temp['SendCtgName'] = record.UserParameters.SendCtg.Name
                    except AttributeError:
                        pass

                    try:
                        # Отправитель
                        temp['Sndr'] = record.UserParameters.Sndr
                    except AttributeError:
                        pass

                    try:
                        # Получатель
                        temp['Rcpn'] = record.UserParameters.Rcpn
                    except AttributeError:
                        pass

                data.append(temp)

            return data
        return False


# Класс: Клиент пакетного доступа
class PackTrackClient:

    # Конструктор
    def __init__(self, login, password, url, track_in_ticket=3000):
        """
        :param login: логин на сервисе трекинга Почты России
        :param password: пароль на сервисе трекинга Почты России
        :param url: ссылка к wsdl описанию сервиса
        :param track_in_ticket: отправлений на один запрос
        """

        self.login = login
        self.password = password
        self.url = url
        self.track_in_ticket = track_in_ticket
        binding.envns = ('SOAP-ENV', 'http://schemas.xmlsoap.org/soap/envelope/')
        # Создаем клиент
        self.api = Client(self.url, username=self.login, password=self.password)
        # Текст ошибки
        self.error = ''
        #

    # Метод: Разбивает список с ШПИ по указанному количеству
    def split_barcode_list(self, barcode_list):
        return [barcode_list[i: i + self.track_in_ticket] for i in range(0, len(barcode_list), self.track_in_ticket)]

    # Метод: Создает тикет на сервере
    def create_ticket(self, barcode_list):
        barcodes = []
        self.error = ''

        # Если количество РПО больше максимального количества для запроса
        if len(barcode_list) > self.track_in_ticket:
            self.error = 'Количество РПО в списке превышает максимальный лимит для запроса'
            return False

        #  Перебираем РПО и создаем объекты для запроса
        for barcode in barcode_list:
            item = self.api.factory.create('item')
            item._Barcode = barcode
            barcodes.append(item)

        # Создаем объект с РПО
        file = self.api.factory.create('file')
        file.Item = barcodes
        # Создаем объект с РПО
        try:
            response = self.api.service.getTicket(file, self.login, self.password, 'RUS')
        except WebFault:
            return False

        # Если есть ошибки
        if 'error' in response:
            self.error = response.error._ErrorName
            return False
        # Если есть номер тикета в ответе
        if 'value' in response:
            return {response.value: barcode_list}
        return False

    #
    def get_ticket(self, ticket_id):
        self.error = ''
        data = {}

        response = self.api.service.getResponseByTicket(ticket=ticket_id, login=self.login, password=self.password)
        # Если есть ошибки
        if 'error' in response:
            self.error = response.error._ErrorName
            return False

        # Перебираем РПО
        for rpo in response.value.Item:
            barcode = rpo._Barcode

            if barcode not in data.keys():
                data.update({barcode: {'Operation': [], 'ErrorID': '', 'ErrorName': ''}})

            if 'Error' in rpo:
                data[barcode]['ErrorID'] = rpo.Error._ErrorTypeID or ''
                data[barcode]['ErrorName'] = rpo.Error._ErrorName or ''
            else:
                for oper in rpo.Operation:
                    data[barcode]['Operation'].append({'OperTypeID': oper._OperTypeID, 'OperCtgID': oper._OperCtgID,
                                                       'OperName': oper._OperName, 'DateOper': oper._DateOper,
                                                       'IndexOper': oper._IndexOper})
        return data
