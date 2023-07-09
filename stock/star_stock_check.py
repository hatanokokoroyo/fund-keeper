import datetime
from typing import List

import pandas as pd

from file_utils import load_from_file, get_local_stock_list
from stock.model import Stock, NetWorth


def convert_datetime_str_to_datetime(date_time_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_time_str, '%Y-%m-%d')


def check_index(stock_code: str, start_date: str, end_date: str):
    # 从本地文件获取净值数据
    stock: Stock = load_from_file(stock_code)
    net_worth_list: List[NetWorth] = stock.daily_net_worth_list
    # 截取数据[start_date - 200, end_date]
    start_date_index = 0
    end_date_index = 0
    for i in range(len(net_worth_list)):
        if net_worth_list[i]['date'] == start_date:
            start_date_index = i
        if net_worth_list[i]['date'] == end_date:
            end_date_index = i
    # net_worth_list = net_worth_list[start_date_index - 200: end_date_index + 1]
    # 转换为dataframe
    data_frame: pd.DataFrame = pd.DataFrame(
        [(f['open'], f['close'], f['high'], f['low'], f['volume'], convert_datetime_str_to_datetime(f['date']))
         for f in
         net_worth_list],
        columns=['open', 'close', 'high', 'low', 'volume', 'date'])
    # 区间最大值和最小值, 天数
    period_cnt = end_date_index - start_date_index + 1
    period_max_close = None
    period_max_close_index = None
    period_min_close = None
    period_min_close_index = None
    for i in range(start_date_index, end_date_index + 1):
        if period_max_close is None or net_worth_list[i]['close'] > period_max_close:
            period_max_close = net_worth_list[i]['close']
            period_max_close_index = i
        if period_min_close is None or net_worth_list[i]['close'] < period_min_close:
            period_min_close = net_worth_list[i]['close']
            period_min_close_index = i

    # 计算[start_date, end_date]数据的的(最大值 - 最小值) / 最小值 (保留四位小数)
    period_max_over_min_close_percent = round((period_max_close - period_min_close) / period_min_close, 4)
    # 计算[start_date_index, end_date_index]数据的平均值, (最大值 - 平均值) / 平均值 (保留四位小数), (最小值 - 平均值) / 平均值 (保留四位小数)
    period_avg_close = data_frame[start_date_index: end_date_index]['close'].mean()
    period_max_close_over_avg_percent = round((period_max_close - period_avg_close) / period_avg_close, 4)
    period_min_close_over_avg_percent = round((period_min_close - period_avg_close) / period_avg_close, 4)
    # 计算50日均线和200日均线
    data_frame['ma50'] = data_frame['close'].rolling(window=50).mean()
    data_frame['ma200'] = data_frame['close'].rolling(window=200).mean()
    # 基于50日均线, 计算[start_date, end_date]数据的(最大值 - ma50) / ma50 (保留四位小数), (最小值 - ma50) / ma50 (保留四位小数)
    period_max_close_over_ma50_percent = round(
        (period_max_close - data_frame['ma50'].iloc[period_max_close_index]) / data_frame['ma50'].iloc[
            period_max_close_index], 4)
    period_min_close_over_ma50_percent = round(
        (period_min_close - data_frame['ma50'].iloc[period_min_close_index]) / data_frame['ma50'].iloc[
            period_min_close_index], 4)
    # 基于200日均线, 计算[start_date, end_date]数据的(最大值 - ma200) / ma200 (保留四位小数), (最小值 - ma200) / ma200 (保留四位小数)
    period_max_close_over_ma200_percent = round(
        (period_max_close - data_frame['ma200'].iloc[period_max_close_index]) / data_frame['ma200'].iloc[
            period_max_close_index], 4)
    period_min_close_over_ma200_percent = round(
        (period_min_close - data_frame['ma200'].iloc[period_min_close_index]) / data_frame['ma200'].iloc[
            period_min_close_index], 4)
    print(
        f'{stock_code}\t{start_date}\t{end_date}\t{period_cnt}\t{period_max_over_min_close_percent}\t{period_max_close_over_avg_percent}\t{period_min_close_over_avg_percent}\t{period_max_close_over_ma50_percent}\t{period_min_close_over_ma50_percent}\t{period_max_close_over_ma200_percent}\t{period_min_close_over_ma200_percent}')


def main():
    stock_period_list = [
        # stock_code, start_date, end_date
        ('sz300280', '2023-03-20', '2023-04-21'),
        ('sz300426', '2023-02-01', '2023-03-08'),
        ('sh601858', '2022-12-01', '2023-03-16'),
        ('', '', ''),
        ('', '', ''),
        ('', '', ''),
        ('', '', ''),
        ('', '', ''),
        ('', '', ''),
        ('', '', ''),
        ('', '', ''),
        ('', '', ''),
        ('', '', ''),
    ]
    # filter empty
    stock_period_list = list(filter(lambda x: x[0] != '', stock_period_list))
    # print tsv head
    print(
        f'code\tstart_date\tend_date\tperiod_cnt\tperiod_max_over_min_close_percent\tperiod_max_close_over_avg_percent\tperiod_min_close_over_avg_percent\tperiod_max_close_over_ma50_percent\tperiod_min_close_over_ma50_percent\tperiod_max_close_over_ma200_percent\tperiod_min_close_over_ma200_percent')
    for stock_period in stock_period_list:
        check_index(stock_period[0], stock_period[1], stock_period[2])


if __name__ == '__main__':
    main()
