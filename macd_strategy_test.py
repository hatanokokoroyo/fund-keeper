import json

import pandas as pd
import matplotlib.pyplot as plt
import requests
from api.trend.doctor_xiong_api import get_fund_detail
from api.trend.doctor_xiong_model import DoctorXiongFundDetail, DoctorXiongNetWorthData


def calculate_macd(df, short_period=12, long_period=26, signal_period=9):
    df['EMA_short'] = df['Net Worth'].ewm(span=short_period, adjust=False).mean()
    df['EMA_long'] = df['Net Worth'].ewm(span=long_period, adjust=False).mean()
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    df['Signal Line'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal Line']
    return df


def calculate_bollinger_bands(df, window=20, num_std=2):
    df['MA'] = df['Net Worth'].rolling(window).mean()
    df['Upper Band'] = df['MA'] + num_std * df['Net Worth'].rolling(window).std()
    df['Lower Band'] = df['MA'] - num_std * df['Net Worth'].rolling(window).std()
    return df


def get_fund_real_time_net_worth(fund_code: str):
    url = 'http://fundgz.1234567.com.cn/js/' + fund_code + '.js'
    r = requests.get(url)
    net_worth_info = r.text
    json_str = net_worth_info[8:-2]
    json_object = json.loads(json_str)
    real_time_net_worth = json_object['gsz']
    name = json_object['name']
    return name, float(real_time_net_worth)


def main():
    start_date = '2022-01-01'
    end_date = '2023-05-11'

    fund_code_list = [
        '016814', '004598', '012863', '001156', '400015', '012832', '017482', '006229', '013311', '001856', '010149',
        '011103', '008702', '006221', '005506', '016814', '004598', '007882', '008591', '015675', '004855', '012863',
        '014111', '012832', '400015', '001156', '005064', '010149', '006229', '011036', '006221', '010210', '012549',
        '012414', '013311', '008089', '001676', '005506', '001676', '011103', '011840', '011463', '009180', '007818',
        '008702', '013081', '013219', '008591', '005918', '016814', '012810', '004598', '007882', '008087', '012769',
        '008586', '005224', '017090', '014130', '012637', '012615', '017482', '001924', '002258', '001678', '013621',
        '010769', '017484', '006166', '001856', '008888', '320007',
    ]

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
        df['Date'] = pd.to_datetime(df['Date'])  # 将日期列转换为日期类型
        df.set_index('Date', inplace=True)  # 将日期列设置为索引

        # 计算MACD指标
        df['EMA12'] = df['Net Worth'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Net Worth'].ewm(span=26, adjust=False).mean()
        df['MACD Line'] = df['EMA12'] - df['EMA26']
        df['Signal Line'] = df['MACD Line'].ewm(span=9, adjust=False).mean()
        df['Histogram'] = df['MACD Line'] - df['Signal Line']

        # 绘制MACD图表
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        plt.plot(df.index, df['Net Worth'], label='Net Worth')
        plt.legend(loc='upper left')
        plt.title('Fund Net Worth')

        plt.subplot(2, 1, 2)
        plt.plot(df.index, df['MACD Line'], label='MACD Line', color='blue')
        plt.plot(df.index, df['Signal Line'], label='Signal Line', color='red')
        plt.bar(df.index, df['Histogram'], label='Histogram', color='gray')
        plt.legend(loc='upper left')
        plt.title('MACD')

        plt.show()


if __name__ == '__main__':
    main()
