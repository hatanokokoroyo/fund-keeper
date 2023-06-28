import os
from file_utils import load_from_file
from model import Stock, NetWorth


def get_local_stock_list():
    dir_path = './stock/'
    file_list = os.listdir(dir_path)
    stock_list = []
    for file_name in file_list:
        stock_list.append(file_name.split('.')[0])
    return stock_list


def main():
    second_stage_stock_list = []

    stock_code_list = get_local_stock_list()
    total_stock_count = len(stock_code_list)
    cnt = 0
    for stock_code in stock_code_list:
        cnt += 1
        stock: Stock = load_from_file(stock_code)
        daily_net_worth_list = stock.daily_net_worth_list
        if len(daily_net_worth_list) < 3:
            continue

        # 判断是否是启明星形态
        # 1.前天是下跌
        # 2.昨天开盘收盘价低于前天收盘价
        # 3.今日是上涨
        today_net_worth: NetWorth = daily_net_worth_list[-1]
        yesterday_net_worth: NetWorth = daily_net_worth_list[-2]
        before_yesterday_net_worth: NetWorth = daily_net_worth_list[-3]
        # 前日下跌
        if before_yesterday_net_worth['open'] <= before_yesterday_net_worth['close']:
            continue
        # 昨日开盘价和收盘价都低于前日收盘价
        if max(yesterday_net_worth['open'], yesterday_net_worth['close']) > before_yesterday_net_worth['close']:
            continue
        # 今日上涨, 且开盘价高于昨日开盘和收盘价
        if today_net_worth['open'] >= today_net_worth['close']:
            continue
        if min(today_net_worth['open'], today_net_worth['close']) < min(yesterday_net_worth['open'],
                                                                        yesterday_net_worth['close']):
            continue

        if today_net_worth['close'] == today_net_worth['open']:
            continue
        before_yesterday_net_worth_diff = abs(before_yesterday_net_worth['close'] - before_yesterday_net_worth['open'])
        yesterday_net_worth_diff = abs(yesterday_net_worth['close'] - yesterday_net_worth['open'])
        today_net_worth_diff = abs(today_net_worth['close'] - today_net_worth['open'])

        # 前天和今天的差值, 都应该是昨天的三倍以上
        if before_yesterday_net_worth_diff < yesterday_net_worth_diff * 5:
            continue
        if today_net_worth_diff < yesterday_net_worth_diff * 5:
            continue
        diff_rate = min(before_yesterday_net_worth_diff, today_net_worth_diff) / max(before_yesterday_net_worth_diff,
                                                                                     today_net_worth_diff)
        if diff_rate < 0.8:
            continue

        print(stock_code, stock.name)


if __name__ == '__main__':
    main()
