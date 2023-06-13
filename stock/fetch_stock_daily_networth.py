import datetime
import json
from typing import List
from model import NetWorth, Stock
from file_utils import check_file_exists, save_to_file

import requests

headers = {
    "token": "UPIYr4zGtH"
}


def get_all_stock_name_code():
    url = 'https://api.doctorxiong.club/v1/stock/all'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print('请求失败')
        return None
    data_list = json.loads(response.text)['data']
    code_name_dict_list = []
    for data in data_list:
        code_name_dict_list.append({
            'code': data[0],
            'name': data[1]
        })
    return code_name_dict_list


def get_stock_daily_net_worth(stock_code: str) -> List[NetWorth]:
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
        stock_net_worth_list.append(NetWorth(date=data[0], open=data[1], close=data[2], high=data[3], low=data[4],
                                             volume=data[5]))
    return stock_net_worth_list


def main():
    stock_name_code_list = get_all_stock_name_code()
    total = len(stock_name_code_list)
    count = 0
    for stock_name_code in stock_name_code_list:
        count += 1
        code = stock_name_code['code']
        name = stock_name_code['name']
        if check_file_exists(code):
            print('数据存在存在：' + str(count) + '/' + str(total) + ' ' + code + ' ' + name)
            continue
        try:
            daily_net_worth_list = get_stock_daily_net_worth(code)
            stock = Stock(name=name, code=code, daily_net_worth_list=daily_net_worth_list)
            save_to_file(stock)
        except Exception as e:
            print('请求失败：' + str(count) + '/' + str(total) + ' ' + code + ' ' + name)
            print(e)
            continue
        print('请求成功：' + str(count) + '/' + str(total) + ' ' + code + ' ' + name)


if __name__ == '__main__':
    main()
