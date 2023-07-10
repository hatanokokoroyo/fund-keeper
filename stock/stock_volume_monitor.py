# 定时任务, 每10秒执行一次
#
# 0/10 * * * * ? *
#
import datetime
import json
from typing import List

import requests
from apscheduler.schedulers.blocking import BlockingScheduler

from stock.model import NetWorth

headers = {
    "token": "UPIYr4zGtH"
}

sched = BlockingScheduler()
# 交易量增长过滤器, 防止频繁发送消息 {stock_code: volume_growth_rate(round 1)}
filter_map = {}

feishu_bot_hook = 'https://open.feishu.cn/open-apis/bot/v2/hook/028ecc42-3e01-45af-b358-a0446e3c4264'


def read_monitor_file():
    print('读取监控文件')
    # 读取文件./monitor_stock_code_list.csv, 两列字段: stock_code,stock_name,stock_type
    stock_info_list = []
    with open('./monitor_stock_code_list.csv', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith('#'):
                continue
            stock_code, stock_name, stock_type = line.split(',')
            stock_info_list.append((stock_code, stock_name, stock_type))
    return stock_info_list


def get_stock_daily_net_worth(stock_code: str) -> List[NetWorth]:
    url = 'https://api.doctorxiong.club/v1/stock/kline/day'
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    one_year_ago = datetime.datetime.now() - datetime.timedelta(days=4)
    params = {
        'code': stock_code,
        'startDate': one_year_ago,
        'endDate': now,
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


def send_msg(msg):
    # 发送消息
    data = {
        "msg_type": "text",
        "content": {
            "text": msg
        }
    }
    requests.post(feishu_bot_hook, json=data)


@sched.scheduled_job('interval', seconds=60)
def timed_job():
    print('开始执行定时任务')
    stock_info_list = read_monitor_file()
    sent_msg_flag = False
    need_send_msg_list = []
    for stock_code, stock_name, stock_type in stock_info_list:
        daily_net_worth_list: List[NetWorth] = get_stock_daily_net_worth(stock_code)
        # 判断最后一条数据的交易是否是倒数第二条数据的交易量的1.5倍, 保留1位小数
        volume_growth_rate = round((daily_net_worth_list[-1].volume / daily_net_worth_list[-2].volume), 1)

        # 小于1.5的无需关注, 大于1.5后, 进入关注范围
        if volume_growth_rate < 1.5:
            print(f'{stock_name}({stock_code})交易量增长{volume_growth_rate}倍, 不关注')
            continue
        # 如果已经在过滤器中
        sent_volume_growth_rate = filter_map.get(stock_code)
        if sent_volume_growth_rate is not None:
            if sent_volume_growth_rate == volume_growth_rate:
                print(f'{stock_name}({stock_code})交易量增长{volume_growth_rate}倍, 已经发送过消息, 不再发送')
                continue
            else:
                filter_map[stock_code] = volume_growth_rate
        else:
            filter_map[stock_code] = volume_growth_rate
        # 大于2后就考虑是否买入
        # if volume_growth_rate > 3:
        #     print(f'{stock_name}({stock_code})交易量增长{volume_growth_rate}倍, 可以考虑买入')
        #     continue
        today_open = daily_net_worth_list[-1].open
        today_close = daily_net_worth_list[-1].close
        yesterday_close = daily_net_worth_list[-2].close
        # 今日涨幅: (今日收盘价 - 昨日收盘价) / 昨日收盘价
        today_net_worth_growth_rate = round((today_close - yesterday_close) / yesterday_close * 100, 2)
        # 今日振幅: (今日收盘价 / 今日开盘价)
        today_net_worth_amplitude_rate = round((today_close - today_open) / today_open * 100, 2)

        msg = f'{stock_name}({stock_code}-{stock_type})今日涨幅{today_net_worth_growth_rate}%, ' \
              f'振幅{today_net_worth_amplitude_rate}%, 交易量增长{volume_growth_rate}倍'
        need_send_msg_list.append(msg)
        sent_msg_flag = True
        print(msg)
    print('-------------------')
    if len(need_send_msg_list) > 0:
        merge_msg = '-----------' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '----------- \n' + \
                    '\n'.join(need_send_msg_list)
        send_msg(merge_msg)


if __name__ == '__main__':
    timed_job()
    sched.start()
