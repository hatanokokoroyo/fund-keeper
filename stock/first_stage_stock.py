from typing import List

import pandas

from file_utils import load_from_file, get_local_stock_list
from index.move_average_line_indicator import calculate_move_average_line
import pandas as pd
import datetime
from model import Stock, NetWorth


def match_first_stage_include_break_through(data_frame: pandas.DataFrame) -> bool:
    # 200日均线连续上涨20日
    for i in range(1, 10):
        if data_frame.iloc[-i]['ma200'] < data_frame.iloc[-i - 1]['ma200']:
            return False
    # 最后一条数据的日期必须是七日之内
    last_date = data_frame.iloc[-1]['date']
    today = datetime.datetime.today()
    if (today - last_date).days > 7:
        return False
    # 在过去三个月内, 至少有两个月的时间, 收盘价一直在200日均线通道的内部
    # 200日均线通道的上下界, 分别是ma200_upper_bound, ma200_lower_bound
    in_bound_count = 0
    for i in range(1, 90):
        if data_frame.iloc[-i]['ma200_lower_bound'] <= data_frame.iloc[-i]['close'] <= \
                data_frame.iloc[-i]['ma200_upper_bound']:
            in_bound_count += 1
    if in_bound_count < 60:
        return False
    return True


def convert_datetime_str_to_datetime(date_time_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_time_str, '%Y-%m-%d')


def main():
    first_stage_stock_list = []

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
        try:
            # convert to dataFrame
            data_frame = pd.DataFrame(
                [(f['open'], f['close'], f['high'], f['low'], f['volume'], convert_datetime_str_to_datetime(f['date']))
                 for f in
                 daily_net_worth_list],
                columns=['open', 'close', 'high', 'low', 'volume', 'date'])
            # calculate 50,150,200 move average line
            data_frame['net_worth'] = data_frame['close']
            data_frame = calculate_move_average_line(data_frame, 200)
            # calculate upper and lower bound of ma200 with 20%
            wave_rate = 0.1
            data_frame['ma200_upper_bound'] = data_frame['ma200'] * (1 + wave_rate)
            data_frame['ma200_lower_bound'] = data_frame['ma200'] * (1 - wave_rate)
            # calculate break through
            break_through_flag = match_first_stage_include_break_through(data_frame)
            if not break_through_flag:
                continue

            # 最近七日内, 有任意一天的交易量, 是昨日的2倍以上, 且该日是阳线
            # for i in range(1, 3):
            #     if data_frame.iloc[-i]['close'] <= data_frame.iloc[-i]['open']:
            #         continue
            #     if data_frame.iloc[-i]['volume'] > data_frame.iloc[-i - 1]['volume'] * 2:
            #         first_stage_stock_list.append((stock_code, stock.name))
            #         print(stock_code, stock.name, 'match volume break through')
            #         break
            # 今日交易量, 是昨日的2倍以上, 且今日是阳线
            # if data_frame.iloc[-1]['close'] > data_frame.iloc[-1]['open'] and \
            #         data_frame.iloc[-1]['volume'] > data_frame.iloc[-2]['volume'] * 2:
            #     first_stage_stock_list.append((stock_code, stock.name))
            #     print(stock_code, stock.name, 'match volume break through')
            #     continue
            first_stage_stock_list.append((stock_code, stock.name))
            print(stock_code, stock.name, 'match volume break through')
        except Exception as e:
            print(stock_code, stock.name, 'error')
            print(e)
            continue
        print(stock_code, stock.name, 'done', cnt, '/', total_stock_count)
    for stock_code, stock_name in first_stage_stock_list:
        print(stock_code, stock_name)


if __name__ == '__main__':
    main()
