import requests
from urllib import request
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime, timedelta
from datetime import datetime
import csv

BASE_URL = 'https://zcash.flypool.org/miners/t1NDwS7YBXt7pfbmpaRsy6kkGZgM39Ywyix/payouts'
DEBUG = 1


def get_html(url):
    """
    Получаем html по заданному url
    :param url:
    :return:
    """
    req = request.Request(url, None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'})
    response = request.urlopen(req)
    return response.read()


def get_yobit_data(coin):
    """
    Получаем с биржи Yobit последний курс по монете
    """
    base_url = 'https://yobit.net/api/3/ticker/'
    url = base_url + coin
    resp = requests.get(url)
    json = resp.json()
    return json[coin]['last']


def get_flypool_data():
    """
    Получаю с флайпула json с данными
    Не буду использовать, т.к. в json непонятные значения (ethPerMin) и т.д.
    """
    url = 'http://zcash.flypool.org/api/miner_new/t1NDwS7YBXt7pfbmpaRsy6kkGZgM39Ywyix'
    resp = requests.get(url)
    return resp.json()


def get_hashrate():
    """
    Получаем с флайпула средний hashrate
    через json
    :return:
    """
    url = 'http://zcash.flypool.org/api/miner_new/t1NDwS7YBXt7pfbmpaRsy6kkGZgM39Ywyix'
    resp = requests.get(url)
    json = resp.json()
    hashrate = json['avgHashrate']
    return int(hashrate)


def get_zec_day():
    url = 'https://zcash.flypool.org/miners/t1NDwS7YBXt7pfbmpaRsy6kkGZgM39Ywyix/payouts'
    html = get_html(url)
    soup = BeautifulSoup(html, "lxml")
    zec_day = soup.find('table', class_='table table-condensed table-bordered').find_all('tr')[3].find_all('td')[1].text
    return float(zec_day)


def write_csv(data):
    with open ('avito.csv', 'a') as f:
        writer = csv.writer(f, lineterminator='\n')

        writer.writerow( (data['title'],
                          data['price'],
                          data['metro'],
                          data['url']) )


def main():
    # Все монеты биржи Yobit - https://yobit.net/api/3/info

    zec_day = round(get_zec_day(), 8)                           # Сколько зарабатываем zec в день
    avg_hashrate = get_hashrate()                               # Средний хэшрейт
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M")   # Время
    zec_btc = get_yobit_data('zec_btc')                         # Курс zec_btc с биржи Yobit
    btc_usd = round(get_yobit_data('btc_usd'), 2)               # Курс btc_usd с биржи Yobit
    btc_rur = round(get_yobit_data('btc_rur'), 2)               # Курс btc_rur с биржи Yobit

    # -----Прогнозируемый заработок в сутки-----
    btc_per_day = round(zec_day * zec_btc, 8)                   # В биткоинах
    usd_per_day = round(btc_per_day * btc_usd, 2)               # В долларах
    rub_per_day = round(btc_per_day * btc_rur, 2)               # В рублях

    if DEBUG:
        print("Time: \t\t\t"+now)
        # print("ZEC in DAY: \t" + str(zec_day))
        print("Avg. Hashrate: \t" + str(avg_hashrate)+" H/s")
        print("ZEC/BTC: \t\t" + str(zec_btc))
        print("BTC/USD: \t\t" + str(btc_usd))
        print("BTC/RUR: \t\t" + str(btc_rur))
        print('\n-----Прогнозируемая доходность-----')
        print('\t\tDay\t\t\t\tWeek\t\t\tMonth')
        print('ZEC:\t' + str(zec_day)+'\t\t\t'+str(round(zec_day*7, 8))+'\t\t\t'+str(round(zec_day*30.5, 8)))
        print('BTC:\t' + str(btc_per_day)+'\t\t'+str(round(btc_per_day*7, 8))+'\t\t'+str(round(btc_per_day*30.5, 8)))
        print('USD:\t' + str(usd_per_day)+'\t\t\t'+str(round(usd_per_day*7, 8))+'\t\t\t'+str(round(usd_per_day*30.5, 8)))
        print('RUB:\t' + str(rub_per_day)+'\t\t\t'+str(round(rub_per_day*7, 8))+'\t\t\t'+str(round(rub_per_day*30.5, 8)))

    # -----Запись данных в файл-----
    with open ('fly_data.csv', 'a') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow((now,
                         zec_btc,
                         btc_usd,
                         btc_rur,
                         avg_hashrate,
                         zec_day,
                         btc_per_day,
                         usd_per_day,
                         rub_per_day))


if __name__ == '__main__':
    main()
