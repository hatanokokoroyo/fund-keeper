import datetime
import json
from typing import List
import os

import requests

from file_utils import check_file_exists, save_to_file
from model import NetWorth, Stock

headers = {
    "token": "UPIYr4zGtH"
}


def get_all_stock_name_code():
    url = 'https://api.doctorxiong.club/v1/stock/all'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print('请求失败', response.text)
        return None
    response_body = json.loads(response.text)
    # response_body contains: 'data'
    if 'data' not in response_body:
        print('返回数据格式错误', response.text)
        return None
    data_list = response_body['data']
    code_name_dict_list = []
    for data in data_list:
        code_name_dict_list.append({
            'code': data[0],
            'name': data[1]
        })
    return code_name_dict_list


def get_stock_base_info(stock_code: str) -> (bool, dict):
    url = 'https://api.doctorxiong.club/v1/stock'
    params = {
        'code': stock_code
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return False, {}

    stock_data = json.loads(response.text)
    data = stock_data['data']
    if data is None or len(data) == 0:
        return False, {}
    return True, stock_data['data'][0]


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
    if data_list is None:
        print('请求失败', response.text)
        return []
    stock_net_worth_list = []
    for data in data_list:
        stock_net_worth_list.append(NetWorth(date=data[0], open=data[1], close=data[2], high=data[3], low=data[4],
                                             volume=data[5]))
    return stock_net_worth_list


def main():
    # 删除./stock文件夹下的所有文件
    # file_list = os.listdir('./stock/')
    # for file_name in file_list:
    #     os.remove('./stock/' + file_name)
    stock_name_code_list = get_all_stock_name_code()
    if stock_name_code_list is None:
        print('获取股票列表失败')
        return
    total = len(stock_name_code_list)
    count = 0
    for stock_name_code in stock_name_code_list:
        count += 1
        code: str = stock_name_code['code']
        name: str = stock_name_code['name']
        # 过滤掉本地已经存在的股票
        if check_file_exists(code):
            print('数据存在：' + str(count) + '/' + str(total) + ' ' + code + ' ' + name)
            continue
        # 过滤掉ST的股票
        # if name.startswith('st'):
        #     print('ST股票, 已过滤：' + str(count) + '/' + str(total) + ' ' + code + ' ' + name)
        #     continue
        # 过滤掉PE小于等于0的股票
        # success_flag, base_info = get_stock_base_info(code)
        # if success_flag:
        #     try:
        #         float(base_info['pe'])
        #         # if float(base_info['pe']) <= 0:
        #         #     print('PE小于等于0, 已过滤：' + str(count) + '/' + str(total) + ' ' + code + ' ' + name)
        #         #     continue
        #     except Exception as e:
        #         print('PE解析失败, 已过滤：' + str(count) + '/' + str(total) + ' ' + code + ' ' + name, base_info['pe'],
        #               e)
        #         continue
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
