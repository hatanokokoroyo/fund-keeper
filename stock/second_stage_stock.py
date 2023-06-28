import os
from typing import List

import pandas

from file_utils import load_from_file, get_local_stock_list
from index.move_average_line_indicator import calculate_move_average_line
import pandas as pd
import datetime
from model import Stock, NetWorth


def match_second_stage(data_frame: pandas.DataFrame, last_index) -> bool:
    # 当前收盘价 > 50日均线 > 150日均线 > 200日均线
    # 200日均线连续上涨20日
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
    # 大于一年内最低收盘价的1.3倍
    if not year_low_close * 1.3 <= today_close:
        return False
    # 大于一年内最高收盘价的0.75倍
    if not today_close >= year_high_close * 0.75:
        return False
    # 200日均线连续上涨20日
    for i in range(1, 20):
        if data_frame.iloc[last_index - i]['ma200'] < data_frame.iloc[last_index - i - 1]['ma200']:
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


def calculate_rsi(data_frame, time_window):
    """
    计算RSI
    :param data_frame:
    :param time_window:
    :return:
    """
    data_frame['change'] = data_frame['close'] - data_frame['close'].shift(1)
    data_frame['gain'] = data_frame['change'].apply(lambda x: x if x > 0 else 0)
    data_frame['loss'] = data_frame['change'].apply(lambda x: abs(x) if x < 0 else 0)
    data_frame['avg_gain'] = data_frame['gain'].rolling(time_window).mean()
    data_frame['avg_loss'] = data_frame['loss'].rolling(time_window).mean()
    data_frame['rs'] = data_frame['avg_gain'] / data_frame['avg_loss']
    data_frame['rsi'] = 100 - (100 / (1 + data_frame['rs']))
    return data_frame['rsi']


def get_max_growth_rate(daily_net_worth_list: List[NetWorth], start_date: datetime.datetime,
                        end_date: datetime.datetime) -> (
        float, datetime.datetime, datetime.datetime):
    # 先获取指定时间段内最高的收盘价, 再获取在此之前的最低收盘
    max_close = None
    max_date = None
    min_close = None
    min_date = None
    # copy一份, 避免修改原始数据
    daily_net_worth_list = daily_net_worth_list.copy()
    daily_net_worth_list.sort(key=lambda x: x['date'], reverse=True)
    for net_worth in daily_net_worth_list:
        current_datetime = datetime.datetime.strptime(net_worth['date'], '%Y-%m-%d')
        if current_datetime < start_date or current_datetime > end_date:
            continue
        if max_close is None or net_worth['close'] > max_close:
            max_close = net_worth['close']
            # 每次更新最高收盘价时, 重置最低收盘价
            min_close = max_close
            max_date = current_datetime
        if net_worth['close'] < min_close:
            min_close = net_worth['close']
            min_date = current_datetime
    if max_close is None or min_close is None or min_close == 0 or max_close == 0 or min_close == max_close:
        return 0, None, None
    return (max_close - min_close) / min_close, \
        datetime.datetime.strftime(min_date, '%Y-%m-%d'), \
        datetime.datetime.strftime(max_date, '%Y-%m-%d'),


def main():
    second_stage_stock_list = []

    stock_code_list = get_local_stock_list()
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
        # 获取半年内的最大增长率
        max_growth_rate, min_date, max_date = get_max_growth_rate(
            daily_net_worth_list, datetime.datetime.now() - datetime.timedelta(days=180), datetime.datetime.now())
        if max_growth_rate < 1.5:
            # print(stock_code, stock.name, '半年内增长率不足: ' + str(max_growth_rate))
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
            data_frame = calculate_move_average_line(data_frame, 50)
            data_frame = calculate_move_average_line(data_frame, 150)
            data_frame = calculate_move_average_line(data_frame, 200)

            is_second_flag = match_second_stage(data_frame, -1)
            if not is_second_flag:
                continue

            # 计算250日相对强度指标
            # data_frame['rsi250'] = calculate_rsi(data_frame, 250)
            # # 250日RSI大于50
            # if data_frame.iloc[-1]['rsi250'] < 60:
            #     continue

            # 额外过滤条件: 5日均线大于10日均线大于20日均线
            # data_frame = calculate_move_average_line(data_frame, 5)
            # data_frame = calculate_move_average_line(data_frame, 10)
            # data_frame = calculate_move_average_line(data_frame, 20)
            # if not data_frame.iloc[-1]['ma5'] > data_frame.iloc[-1]['ma10'] > data_frame.iloc[-1]['ma20']:
            #     continue
            # # 5, 10, 20均线, 今日大于昨日
            # if not data_frame.iloc[-1]['ma5'] > data_frame.iloc[-2]['ma5'] \
            #         and data_frame.iloc[-1]['ma10'] > data_frame.iloc[-2]['ma10'] \
            #         and data_frame.iloc[-1]['ma20'] > data_frame.iloc[-2]['ma20']:
            #     continue
            # 今日交易量, 必须大于昨日交易量的2倍
            # if not data_frame.iloc[-1]['volume'] > data_frame.iloc[-2]['volume'] * 1.5:
            #     continue
            # 最近20日内, 价格均高于50日均线
            # over_ma50_20day_flag = True
            # for i in range(1, 20):
            #     if data_frame.iloc[-i]['close'] < data_frame.iloc[-i]['ma50']:
            #         over_ma50_20day_flag = False
            #         break
            # if not over_ma50_20day_flag:
            #     continue

            second_stage_start_date = get_second_stage_start_date(data_frame)
            second_stage_stock_list.append(
                (stock_code, stock.name, second_stage_start_date, max_growth_rate))

        except Exception as e:
            print(stock_code, stock.name, 'error')
            print(e)
            continue
        print(stock_code, stock.name, 'done', cnt, '/', total_stock_count)

    second_stage_stock_list.sort(key=lambda x: x[2], reverse=True)
    for stock_code, stock_name, second_stage_start_date, max_growth_rate in second_stage_stock_list:
        print(stock_code, stock_name, second_stage_start_date, max_growth_rate)


if __name__ == '__main__':
    main()
