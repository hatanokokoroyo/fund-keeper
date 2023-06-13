import os

import pandas

from file_utils import load_from_file
from index.move_average_line_indicator import calculate_move_average_line
import pandas as pd
import datetime
from model import Stock, NetWorth


def get_local_stock_list():
    dir_path = './stock/'
    file_list = os.listdir(dir_path)
    stock_list = []
    for file_name in file_list:
        stock_list.append(file_name.split('.')[0])
    return stock_list


def match_second_stage(data_frame: pandas.DataFrame, last_index) -> bool:
    # 当前收盘价 > 50日均线 > 150日均线 > 200日均线
    # 200日均线 > 30天前的200日均线
    # 当前收盘价 >= 最近一年最低收盘价的1.3倍
    # 当前收盘价 <= 最近一年最高收盘价的0.75倍
    today_close = data_frame.iloc[last_index]['close']
    today_ma50 = data_frame.iloc[last_index]['ma50']
    today_ma150 = data_frame.iloc[last_index]['ma150']
    today_ma200 = data_frame.iloc[last_index]['ma200']

    year_low_close = data_frame['close'].min()
    year_high_close = data_frame['close'].max()

    if not today_close > today_ma50 > today_ma150 > today_ma200:
        return False

    if not year_low_close * 1.3 <= today_close <= year_high_close * 0.75:
        return False
    # 200日均线连续上涨20日
    for i in range(1, 20):
        if data_frame.iloc[last_index - i]['ma200'] > data_frame.iloc[last_index - i - 1]['ma200']:
            return False
    return True


def get_second_stage_start_date(data_frame: pandas.DataFrame) -> datetime.datetime:
    # 从最后一条数据, 向前遍历, 直到找到不符合
    last_index = -2
    while match_second_stage(data_frame, last_index):
        last_index -= 1
    return data_frame.iloc[last_index + 1]['date']


def get_second_stage_start_date_dichotomy_version(data_frame: pandas.DataFrame) -> datetime.datetime:
    # 从最后一条数据, 向前遍历, 直到找到不符合
    last_index = -2
    while match_second_stage(data_frame, last_index):
        last_index -= 1
    return data_frame.iloc[last_index + 1]['date']


def convert_datetime_str_to_datetime(date_time_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_time_str, '%Y-%m-%d')


def main():
    second_stage_stock_list = []

    stock_code_list = get_local_stock_list()
    total_stock_count = len(stock_code_list)
    cnt = 0
    for stock_code in stock_code_list:
        cnt += 1
        stock: Stock = load_from_file(stock_code)
        daily_net_worth_list = stock.daily_net_worth_list
        if len(daily_net_worth_list) < 200:
            # print(stock_code, stock.name, '数据不足: ' + str(len(daily_net_worth_list)))
            continue
        try:
            # convert to dataFrame
            data_frame = pd.DataFrame(
                [(f['open'], f['close'], f['high'], f['low'], convert_datetime_str_to_datetime(f['date'])) for f in
                 daily_net_worth_list],
                columns=['open', 'close', 'high', 'low', 'date'])
            # calculate 50,150,200 move average line
            data_frame['net_worth'] = data_frame['close']
            data_frame = calculate_move_average_line(data_frame, 50)
            data_frame = calculate_move_average_line(data_frame, 150)
            data_frame = calculate_move_average_line(data_frame, 200)

            is_second_flag = match_second_stage(data_frame, -1)
            if not is_second_flag:
                continue
            second_stage_start_date = get_second_stage_start_date(data_frame)
            second_stage_stock_list.append((stock_code, stock.name, second_stage_start_date))
        except Exception as e:
            print(stock_code, stock.name, 'error')
            print(e)
            continue
        print(stock_code, stock.name, 'done', cnt, '/', total_stock_count)

    second_stage_stock_list.sort(key=lambda x: x[2], reverse=True)
    for stock_code, stock_name, second_stage_start_date in second_stage_stock_list:
        print(stock_code, stock_name, second_stage_start_date)


if __name__ == '__main__':
    main()
