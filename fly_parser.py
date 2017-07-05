# coding=utf-8
""" Модуль предназначен для получения информации о наличии и стоимости
авиабилетов на сайте www.flyniki.com. Основная функция принимает на вход
четыре параметра: IATA-отравления(обязательный), IATA-прибытия(обязательный),
дата отправления(обязательный) и дата возвращения(необязательный). Производится
поиск возможных вариантов перелета и вывод информации на экран. Формат ввода:
IATA- код, состоящий из трёх латинских букв, дата в формате "2017-05-25",
(ГГГГ-ММ-ДД)."""
import sys
from datetime import datetime, timedelta
from itertools import product
import requests
from lxml import html


def valid_date(date):
    """ Проверка валидности даты. Функция получает на вход строку, проверяет ее
    на соответствие указанному шаблону, и проверяет актуальность даты."""
    try:
        if (datetime.strptime(date, '%Y-%m-%d') -
                datetime.now()) < timedelta(-1):
            print 'Дата меньше текущей.'
            return
        return True
    except ValueError:
        print 'Введите корректную дату. Формат даты (yyyy-mm-dd)'
        return


def parser_fly_html(fly_html, path_x):
    """ Функция производит разбор ответа, полученного от сервера
    и формирование результатов обработки для вывода на экран. На вход принимает
    объект fly_html и строку path_x. Возвращаемое значение - список price."""
    price = []
    for node in fly_html.xpath('{}tr/td/*'.format(path_x)):
        res = node.xpath('.//*[@class="lowest"]/span/@title')
        for elem in res:
            price.append([
                elem.split(',')[1][:6],
                elem.split(',')[1][7:],
                elem.split(',')[2],
                elem.split(',')[3].split(':')[0],
                float(''.join(elem.split(':')[3].split('.')).replace(',', '.'))
            ])
    return price


def error_process_resp(result):
    """ Функция производит обработку ошибок ответа сервера."""
    res_json = result.json()
    try:
        fly_html = html.fromstring(res_json['templates']['main'])
    except KeyError:
        if res_json['errorRAW'][0]['code'] == 'departure':
            print 'Введен не кооректный IATA аэропорта отправления.'
            return
        if res_json['errorRAW'][0]['code'] == 'destination':
            print 'Введен не кооректный IATA аэропорта назначения.'
            return
        else:
            print 'Unknown error.'
        return
    if not res_json['templates']['priceoverview']:
        print 'Не удалось найти рейсы на запрошенную дату(ы).'
        return
    return fly_html


def info_output(price_outbond, price_return, currency, return_date):
    """Вывод информации в зависимости от состояния return_date, в случае если
    есть обратный маршрут, осуществляется подсчет общей стоимости перелета."""
    if not return_date:
        print 'Варианты маршрутов:'
        for elem_out in sorted(price_outbond, key=lambda x: x[-1]):
            print ('Вылет:{}, прибытие: {}, длительность:{}, класс:{},' +
                   ' стоимость: {}').format(*elem_out) + currency, '\n'
    else:
        price_result = []
        for elem_out, elem_ret in product(price_outbond, price_return):
            price_result.append({
                'track_out': elem_out,
                'track_return': elem_ret,
                'total_sum': elem_out[-1] + elem_ret[-1]
            })
        for elem_res in sorted(price_result, key=lambda x: x['total_sum']):
            print ('Вылет:{}, прибытие: {}, длительность:{}, класс:{},'
                   ' стоимость:{}').format(*elem_res['track_out']) + currency
            print ('Вылет:{}, прибытие: {}, длительность:{}, класс:{},'
                   'стоимость:{}').format(*elem_res['track_return']) + currency
            print 'Общая стоимость: ', elem_res['total_sum'], currency, '\n'


def parser_flyniki(iata_depart, iata_destination, out_date, return_date):
    """ Функция из полученных данных формирует и отправляет запрос."""
    oneway = '' if return_date else 'on'
    start_url = 'https://www.flyniki.com/ru/start.php'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Referer': 'https://www.flyniki.com/ru/start.php',
        'Accept': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    data = {
        'market': 'RU',
        'language': 'ru',
        'bookingmask_widget_id': 'bookingmask-widget-stageoffer',
        'bookingmask_widget_dateformat': 'dd.mm.yy',
        'oneway': oneway
    }
    req_sess = requests.Session()
    start_post = req_sess.post(
        start_url,
        data=data,
        headers=headers,
        verify=False
    )
    data_res = [
        ('_ajax[templates][]', 'main'),
        ('_ajax[templates][]', 'priceoverview'),
        ('_ajax[templates][]', 'infos'),
        ('_ajax[templates][]', 'flightinfo'),
        ('_ajax[requestParams][departure]', iata_depart),
        ('_ajax[requestParams][destination]', iata_destination),
        ('_ajax[requestParams][returnDeparture]', ''),
        ('_ajax[requestParams][returnDestination]', ''),
        ('_ajax[requestParams][outboundDate]', out_date),
        ('_ajax[requestParams][returnDate]', return_date),
        ('_ajax[requestParams][adultCount]', '1'),
        ('_ajax[requestParams][childCount]', '0'),
        ('_ajax[requestParams][infantCount]', '0'),
        ('_ajax[requestParams][openDateOverview]', ''),
        ('_ajax[requestParams][oneway]', oneway)
    ]
    headers_res = {
        'Accept': 'application/json, text/javascript, */*',
        'Host': 'www.flyniki.com',
        'Origin': 'https://www.flyniki.com',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    result = req_sess.post(
        start_post.url,
        data=data_res,
        headers=headers_res,
        verify=False
    )
    fly_html = error_process_resp(result)
    if not fly_html:
        return
    currency = fly_html.xpath(
        './/*[@id="flighttables"]/div[1]/div[2]/'
        'table/thead/tr[2]/th[4]/text()')[0]
    price_outbond = parser_fly_html(
        fly_html,
        './/*[@class="outbound block"]/div[2]/table/tbody/'
    )
    price_return = parser_fly_html(
        fly_html,
        './/*[@class="return block"]/div[2]/table/tbody/'
    )
    info_output(price_outbond, price_return, currency, return_date)


def parser(args):
    """ Осуществляет разбор параметров полученных из sys.argv и их проверку"""
    if len(args) == 5:
        iata_depart, iata_destination, out_date, return_date = args[1:]
    elif len(args) == 4:
        iata_depart, iata_destination, out_date = args[1:]
        return_date = ''
    else:
        print ('Вы передали {} параметра(ов),'
               'необходимо 3 или 4.').format(len(args[1:]))
        return
    if not valid_date(out_date):
        return
    if return_date:
        if not valid_date(return_date):
            return
        if (datetime.strptime(return_date, '%Y-%m-%d') -
                datetime.strptime(out_date, '%Y-%m-%d')) < timedelta():
            print 'Дата возвращения меньше даты вылета.'
            return
    parser_flyniki(iata_depart, iata_destination, out_date, return_date)


parser(sys.argv)
