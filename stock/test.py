import datetime
import requests
import json
from utils.json_utils import  dumps, loads

headers = {
    "token": "UPIYr4zGtH"
}


class Stock(object):
    def __init__(self, **kwargs):
        self.name: str = kwargs.get('name')
        self.code: str = kwargs.get('code')
        self.time_net_worth_list: list[NetWorth] = kwargs.get('time_net_worth_list', None)
        self.daily_net_worth_list: list[NetWorth] = kwargs.get('daily_net_worth_list', None)
        self.week_net_worth_list: list[NetWorth] = kwargs.get('week_net_worth_list', None)


class NetWorth(object):
    def __init__(self, **kwargs):
        self.open: float = float(kwargs.get('open'))
        self.close: float = float(kwargs.get('close'))
        self.high: float = float(kwargs.get('high'))
        self.low: float = float(kwargs.get('low'))
        self.volume: float = float(kwargs.get('volume'))
        # %Y-%m-%d
        self.date: str = kwargs.get('date')


def get_stock_daily_net_worth(stock_code: str) -> list[NetWorth]:
    url = 'https://api.doctorxiong.club/v1/stock/kline/day'
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    params = {
        'code': stock_code,
        'startDate': one_year_ago,
        'endDate': end_date,
        'type': 1
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('请求失败')
        return []
    data_list = json.loads(response.text)['data']
    stock_net_worth_list = []
    for data in data_list:
        stock_net_worth_list.append({
            'date': data[0],
            'open': float(data[1]),
            'close': float(data[2]),
            'high': float(data[3]),
            'low': float(data[4]),
            'volume': float(data[5])
        })
    return stock_net_worth_list


def save_to_file(stock: Stock):
    with open('./stock/' + stock.code + '.json', 'w+', encoding='utf8') as f:
        f.write(dumps(stock))


def load_from_file(stock_code: str) -> Stock:
    with open('./stock/' + stock_code + '.json', 'r', encoding='utf8') as f:
        return loads(f.read(), cls=Stock)


def main():
    daily_net_worth_list = get_stock_daily_net_worth('sz002546')
    stock = Stock(name='新联电子', code='sz002546', daily_net_worth_list=daily_net_worth_list)
    save_to_file(stock)
    stock = load_from_file('sz002546')
    print(dumps(stock))


if __name__ == '__main__':
    main()
