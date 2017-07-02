# coding=utf-8
import requests
from lxml import html
from datetime import date 
import re

# Проверка валидности даты
def valid_date(inp_date):
    try:
        if not bool(re.match('\d{4}-\d{2}-\d{2}', inp_date)):
            print 'Введите корректную дату'
            return False
        yy, mm, dd = map(int, inp_date.split('-'))
        delta = date(yy, mm, dd) - date.today()
        if delta.days < 0:
            print 'Дата меньше текущей'
            return False
        print 'ok'
        return True
    except ValueError:
        print 'Введите корректную дату'
        return False

def parser_flyniki(iata_depart, iata_destination, out_data, return_data):

    oneway = '' if return_data else  'on'
    start_url = 'https://www.flyniki.com/ru/start.php'

    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:50.0) Gecko/20100101 Firefox/50.0',
                'Referer': 'https://www.flyniki.com/ru/start.php',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'}
    data = {'market': 'RU',
            'language': 'ru',
            'bookingmask_widget_id': 'bookingmask-widget-stageoffer',
            'bookingmask_widget_dateformat': 'dd.mm.yy',
            'oneway': 'on',}

    req_sess = requests.Session()
    start_post = req_sess.post(start_url, data=data, headers=headers, verify=False)
    
    data_res = [('_ajax[templates][]', 'main'),
                ('_ajax[templates][]', 'priceoverview'),
                ('_ajax[templates][]', 'infos'),
                ('_ajax[templates][]', 'flightinfo'),
                ('_ajax[requestParams][departure]', iata_depart),
                ('_ajax[requestParams][destination]', iata_destination),
                ('_ajax[requestParams][returnDeparture]', ''),
                ('_ajax[requestParams][returnDestination]', ''),
                ('_ajax[requestParams][outboundDate]', out_data),
                ('_ajax[requestParams][returnDate]', return_data),
                ('_ajax[requestParams][adultCount]', '1'),
                ('_ajax[requestParams][childCount]', '0'),
                ('_ajax[requestParams][infantCount]', '0'),
                ('_ajax[requestParams][openDateOverview]', ''),
                ('_ajax[requestParams][oneway]', oneway),]
    
    headers_res = { 'Accept': 'application/json, text/javascript, */*',
                    'Host': 'www.flyniki.com',
                    'Origin': 'https://www.flyniki.com',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'}

    result = requests.post(start_post.url, data=data_res, headers=headers_res, cookies=req_sess.cookies, verify=False)
    try:
        fly_html = html.fromstring(result.json()['templates']['main'])
    except KeyError:
        if result.json()['errorRAW'][0]['code'] == 'departure':
            print 'Веден не кооректный IATA аэропорта отправления.'
            return
        if result.json()['errorRAW'][0]['code'] == 'destination':
            print 'Веден не кооректный IATA аэропорта назначения.'
            return
    if not bool(result.json()['templates']['priceoverview']):
        print 'Не удалось найти рейсы на запрошенную дату.'
        return
    currency = fly_html.xpath('.//*[@id="flighttables"]/div[1]/div[2]/table/thead/tr[2]/th[4]/text()')[0]

    def parser_fly_html(path_x):
        price = list()
        for row in range(len(fly_html.xpath(path_x + "tr"))):
            block = fly_html.xpath(path_x +  'tr[' + str(row) + ']/td')
            for node in block:
                res = node.xpath('.//*[@class="lowest"]/span/@title')
                for elem in res:
                    price.append(list([elem.split(',')[1][:6],
                                       elem.split(',')[1][7:],
                                       elem.split(',')[2],
                                       elem.split(',')[3].split(':')[0],
                                       float(''.join(elem.split(':')[3].split('.')).replace(',','.'))]))
        return price

    price_outbond = parser_fly_html('.//*[@class="outbound block"]/div[2]/table/tbody/')
    price_return = parser_fly_html('.//*[@class="return block"]/div[2]/table/tbody/')
    if not return_data:

        print 'Варианты маршрутов:'
        for elem_out in price_outbond:
            print 'Вылет:{}, прибытие: {}, длительность:{}, класс:{}, стоимость: {}'.format(*elem_out) + currency
    else:

        print 'Варианты маршрутов:'
        for elem_out in price_outbond:
            for elem_ret in price_return:
                print 'Вылет:{}, прибытие: {}, длительность:{}, класс:{}, стоимость: {}'.format(*elem_out) + currency
                print 'Вылет:{}, прибытие: {}, длительность:{}, класс:{}, стоимость: {}'.format(*elem_ret) + currency
                print 'Общая стоимость: ', elem_out[-1] + elem_ret[-1], currency


iata_depart = "DM"
iata_destination = "bne"
out_data = "2017-07-07"
return_data = "2017-07-29"
parser_flyniki(iata_depart, iata_destination, out_data, return_data)
"""
def parser():
    
    while True:
        out_data = raw_input('Введите дату вылета (yyyy-mm-dd): ')
        if valid_date(out_data):
            break
    while True:
        return_data = raw_input('Введите дату возвращения (yyyy-mm-dd): ')
        if return_data:
            if valid_date(return_data):
                break
        return_data  =''
        break
    #iata_depart = raw_input('Введите аэропорт вылета: (IATA)')
    #iata_destination = raw_input('Введите аэропорт назначения: (IATA)')

    parser_flyniki(iata_depart, iata_destination, out_data, return_data)
parser()
"""




