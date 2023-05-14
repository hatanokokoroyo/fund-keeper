import json

import matplotlib.dates as dates
import matplotlib.pyplot as plt
import pandas as pd
import requests

from api.trend.doctor_xiong_api import get_fund_detail
from api.trend.doctor_xiong_model import DoctorXiongFundDetail


def get_fund_real_time_net_worth(fund_code: str):
    url = 'http://fundgz.1234567.com.cn/js/' + fund_code + '.js'
    r = requests.get(url)
    net_worth_info = r.text
    json_str = net_worth_info[8:-2]
    json_object = json.loads(json_str)
    real_time_net_worth = json_object['gsz']
    name = json_object['name']
    return name, float(real_time_net_worth)


def calculate_rsi(data, period=14):
    changes = []
    for i in range(1, len(data)):
        net_worth_diff = data[i].net_worth - data[i - 1].net_worth
        changes.append(net_worth_diff)

    gains = [val if val > 0 else 0 for val in changes]
    losses = [-val if val < 0 else 0 for val in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi_values = []
    rsi_values.append(100 - (100 / (1 + avg_gain / avg_loss)))

    for i in range(period, len(changes)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rsi = 100 - (100 / (1 + avg_gain / avg_loss))
        rsi_values.append(rsi)

    return rsi_values


def main():
    start_date = '2020-01-01'
    end_date = '2023-05-13'

    fund_code_list = [
        '016814', '004598', '012863', '001156', '400015', '012832', '017482', '006229', '013311', '001856', '010149',
        '011103', '008702', '006221', '005506', '016814', '004598', '007882', '008591', '015675', '004855', '012863',
        '014111', '012832', '400015', '001156', '005064', '010149', '006229', '011036', '006221', '010210', '012549',
        '012414', '013311', '008089', '001676', '005506', '001676', '011103', '011840', '011463', '009180', '007818',
        '008702', '013081', '013219', '008591', '005918', '016814', '012810', '004598', '007882', '008087', '012769',
        '008586', '005224', '017090', '014130', '012637', '012615', '017482', '001924', '002258', '001678', '013621',
        '010769', '017484', '006166', '001856', '008888', '320007',
    ]

    all_return = 0
    checked_fund_code_list = []
    for fund_code in fund_code_list:
        if fund_code in checked_fund_code_list:
            continue
        checked_fund_code_list.append(fund_code)
        name, today_net_worth = get_fund_real_time_net_worth(fund_code)
        fund_detail = get_fund_detail(fund_code, start_date, end_date)

        if not isinstance(fund_detail, DoctorXiongFundDetail):
            print('error')
            return
        fund_data_list = fund_detail.get_net_worth_data_list()

        # 创建DataFrame对象，用于进行数据处理和计算
        df = pd.DataFrame([(data.date, data.net_worth) for data in fund_data_list], columns=['Date', 'Net Worth'])
        # 将日期列转换为日期类型,
        df['Date'] = pd.to_datetime(df['Date'])
        # 将日期列设置为索引
        df.set_index('Date', inplace=True)

        # 计算布林带指标
        window = 20  # 布林带的时间窗口大小
        num_std = 2  # 布林带的标准差倍数

        df['MA'] = df['Net Worth'].rolling(window).mean()  # 中轨线，即移动平均线
        df['Upper Band'] = df['Net Worth'].rolling(window).mean() + num_std * df['Net Worth'].rolling(
            window).std()  # 上轨线
        df['Lower Band'] = df['Net Worth'].rolling(window).mean() - num_std * df['Net Worth'].rolling(
            window).std()  # 下轨线

        # # 计算10日移动平均线并绘制
        df['10MA'] = df['Net Worth'].rolling(10).mean()
        # # 计算20日移动平均线并绘制
        df['20MA'] = df['Net Worth'].rolling(20).mean()

        avg_return_rate = calculate_avg_return_rate(df)
        print('平均收益率：', avg_return_rate, '% - ', name)


def calculate_avg_return_rate(df):
    # 因为计算布林带指标时，需要前20个数据，所以这里从第20个数据开始计算




if __name__ == '__main__':
    main()
