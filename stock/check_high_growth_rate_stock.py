import datetime
from typing import List

from file_utils import load_from_file, get_local_stock_list
from model import Stock, NetWorth


# 查询指定时间段内, 股票的最大涨幅
def get_max_growth_rate(stock: Stock, start_date: datetime.datetime, end_date: datetime.datetime) -> (
        float, datetime.datetime, datetime.datetime):
    # 先获取指定时间段内最高的收盘价, 再获取在此之前的最低收盘
    max_close = None
    max_date = None
    min_close = None
    min_date = None
    daily_net_worth_list = stock.daily_net_worth_list
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
    stock_code_list = get_local_stock_list()
    # stock_code_list = ['sh600532']
    matched_stock_list = []
    for stock_code in stock_code_list:
        stock: Stock = load_from_file(stock_code)
        daily_net_worth_list: List[NetWorth] = stock.daily_net_worth_list
        if len(daily_net_worth_list) < 365:
            continue
        # 获取一年内, 最大涨幅超过300%的股票
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365)
        max_growth_rate, min_date, max_date = get_max_growth_rate(stock, start_date, end_date)
        # 最高的日期在一个月内
        if max_growth_rate > 3 and (end_date - datetime.datetime.strptime(max_date, '%Y-%m-%d')).days < 30:
            continue
        if max_growth_rate > 2:
            matched_stock_list.append({
                'code': stock_code,
                'name': stock.name,
                'max_growth_rate': max_growth_rate,
                'min_date': min_date,
                'max_date': max_date
            })
    # matched_stock_list.sort(key=lambda x: x['max_growth_rate'], reverse=True)
    matched_stock_list.sort(key=lambda x: x['min_date'], reverse=True)
    for stock in matched_stock_list:
        print(stock)


if __name__ == '__main__':
    main()
