from typing import List

import pandas

from file_utils import load_from_file, get_local_stock_list
from index.move_average_line_indicator import calculate_move_average_line
import pandas as pd
import datetime
from model import Stock, NetWorth


def convert_datetime_str_to_datetime(date_time_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_time_str, '%Y-%m-%d')


def match_first_stage_break_through(data_frame):
    one_year_data = data_frame.iloc[-250:]

    match_date_list: List[str] = []
    # 从第30条数据开始算起
    index = 190
    match_range = 10
    while index < len(one_year_data) - match_range:
        index += 1
        current_data = one_year_data.iloc[index]
        current_ma200 = current_data['ma200']
        current_close = current_data['close']
        if not (current_close > current_data['ma50'] > current_data['ma150'] > current_data['ma200']):
            continue
        # 必须在200日线上方一定区间内
        # if not (current_ma200 * 1.1 < current_close < current_ma200 * 1.5):
        if not (current_ma200 * 1.1 < current_close):
            continue
        # ma200已经连续上涨20日
        ma200_up_20_days_flag = True
        for i in range(1, 20):
            if one_year_data.iloc[index - i]['ma200'] < one_year_data.iloc[index - i - 1]['ma200']:
                ma200_up_20_days_flag = False
                break
        if not ma200_up_20_days_flag:
            continue
        # 取指定范围条数据收盘价的均值, 指定范围条数据的收盘价, 都在均价的0.9倍到1.1倍之间, 且都在ma50之上
        match_flag = True
        avg_close_of_after_match_range_days = one_year_data.iloc[index:index + match_range]['close'].mean()
        for i in range(match_range):
            if not (avg_close_of_after_match_range_days * 0.9 < one_year_data.iloc[index + i]['close']
                    < avg_close_of_after_match_range_days * 1.1):
                match_flag = False
                break
            if one_year_data.iloc[index + i]['close'] < one_year_data.iloc[index + i]['ma50']:
                match_flag = False
                break
        # 指定范围条数据 (最大收盘价 - 最小收盘价) / 最小收盘价 < 0.15
        max_close = one_year_data.iloc[index:index + match_range]['close'].max()
        min_close = one_year_data.iloc[index:index + match_range]['close'].min()
        if (max_close - min_close) / min_close > 0.12:
            continue
        # 前150日的均价必须小于后指定范围日的均价
        avg_close_of_last_30_days = one_year_data.iloc[index - 150:index]['close'].mean()
        if avg_close_of_last_30_days > avg_close_of_after_match_range_days:
            continue
        # 前150日至少有三分之一在ma200以下
        ma200_below_count = 0
        for i in range(150):
            if one_year_data.iloc[index - i]['close'] < one_year_data.iloc[index - i]['ma200']:
                ma200_below_count += 1
        if ma200_below_count < 50:
            continue
        # 数据向前30日, 如果有任意一天收盘价低于ma200, 则符合条件
        break_through_flag = False
        for i in range(30):
            if one_year_data.iloc[index - i]['close'] < one_year_data.iloc[index - i]['ma200']:
                break_through_flag = True
                break
        if match_flag and break_through_flag:
            match_date_list.append(datetime.datetime.strftime(current_data['date'], '%Y-%m-%d'))
            # 接下来30日的数据不需要进行扫描了
            index += 15
    return match_date_list


def main():
    first_stage_break_through_stock_list = []

    stock_code_list = get_local_stock_list()
    # stock_code_list = ['sh605011']
    total_stock_count = len(stock_code_list)
    cnt = 0
    for stock_code in stock_code_list:
        cnt += 1
        stock: Stock = load_from_file(stock_code)
        daily_net_worth_list = stock.daily_net_worth_list
        # 300开头的股票, 一般是创业板, 不考虑
        if stock_code[2:5] == '300':
            continue
        if len(daily_net_worth_list) < 200:
            # print(stock_code, stock.name, '数据不足: ' + str(len(daily_net_worth_list)))
            continue
        # 最后一条数据, 必须是最近七日的数据
        if daily_net_worth_list[-1]['date'] < (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(
                '%Y-%m-%d'):
            continue
        try:
            # convert to dataFrame
            data_frame = pd.DataFrame(
                [(f['open'], f['close'], f['high'], f['low'], f['volume'], convert_datetime_str_to_datetime(f['date']))
                 for f in
                 daily_net_worth_list],
                columns=['open', 'close', 'high', 'low', 'volume', 'date'])
            data_frame['net_worth'] = data_frame['close']
            data_frame = calculate_move_average_line(data_frame, 50)
            data_frame = calculate_move_average_line(data_frame, 150)
            data_frame = calculate_move_average_line(data_frame, 200)

            match_date_list: List[str] = match_first_stage_break_through(data_frame)
            if len(match_date_list) == 0:
                continue
            first_stage_break_through_stock_list.append((stock_code, stock.name, match_date_list))
        except Exception as e:
            print(stock_code, stock.name, 'error')
            print(e)
            continue

        print(stock_code, stock.name, 'done', cnt, '/', total_stock_count, match_date_list)
    for stock_code, stock_name, match_date_list in first_stage_break_through_stock_list:
        # 如果match_date_list中, 有日期在两个月内, 则打印
        for match_date in match_date_list:
            if datetime.datetime.strptime(match_date, '%Y-%m-%d') > datetime.datetime.now() - datetime.timedelta(
                    days=60):
                print(stock_code, stock_name, match_date_list)


if __name__ == '__main__':
    main()
