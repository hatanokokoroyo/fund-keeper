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
    try:
        json_object = json.loads(json_str)
        real_time_net_worth = json_object['gsz']
        name = json_object['name']
        return name, float(real_time_net_worth)
    except Exception as e:
        return None, None


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
    # start_date = '2020-05-12'
    start_date = '2021-05-12'
    end_date = '2023-05-12'

    fund_code_list = [
        # '016814', '004598', '012863', '001156', '400015', '012832', '017482', '006229', '013311', '001856', '010149',
        # '011103', '008702', '006221', '005506', '016814', '004598', '007882', '008591', '015675', '004855', '012863',
        # '014111', '012832', '400015', '001156', '005064', '010149', '006229', '011036', '006221', '010210', '012549',
        # '012414', '013311', '008089', '001676', '005506', '001676', '011103', '011840', '011463', '009180', '007818',
        # '008702', '013081', '013219', '008591', '005918', '016814', '012810', '004598', '007882', '008087', '012769',
        # '008586', '005224', '017090', '014130', '012637', '012615', '017482', '001924', '002258', '001678', '013621',
        # '010769', '017484', '006166', '001856', '008888', '320007',
    ]

    all_return = 0
    checked_fund_code_list = []
    for fund_code in fund_code_list:
        if fund_code in checked_fund_code_list:
            continue
        checked_fund_code_list.append(fund_code)
        name, today_net_worth = get_fund_real_time_net_worth(fund_code)
        if name is None:
            name = '未知'
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

        # 绘制基金净值和布林带图表
        plt.figure(figsize=(12, 8))

        # 第一张图开始
        plt.subplot(2, 1, 1)

        # 绘制基金净值折线图
        plt.plot(df.index, df['Net Worth'], label='Net Worth')
        plt.title(fund_code + ' ' + name)
        plt.xlabel('Date')
        plt.ylabel('Net Worth')
        plt.legend(loc='upper left')

        # 调整x轴刻度
        plt.xticks(rotation=45)
        ax = plt.gca()
        ax.xaxis.set_major_locator(dates.DayLocator(interval=5))  # 设置间隔为30天

        # 绘制布林带
        plt.plot(df.index, df['MA'], label='Moving Average')
        plt.plot(df.index, df['Upper Band'], label='Upper Band')
        plt.plot(df.index, df['Lower Band'], label='Lower Band')
        plt.fill_between(df.index, df['Lower Band'], df['Upper Band'], alpha=0.2)  # 填充布林带之间的区域

        # 计算10日移动平均线并绘制
        df['10MA'] = df['Net Worth'].rolling(10).mean()
        plt.plot(df.index, df['10MA'], label='10MA')

        plt.legend(loc='upper left')

        # 移动平均线图
        plt.subplot(2, 1, 2)
        # 绘制基金净值
        plt.plot(df.index, df['Net Worth'], label='Net Worth')
        # 计算10日移动平均线并绘制
        df['10MA'] = df['Net Worth'].rolling(10).mean()
        plt.plot(df.index, df['10MA'], label='10MA')
        # 计算20日移动平均线并绘制
        df['20MA'] = df['Net Worth'].rolling(20).mean()
        plt.plot(df.index, df['20MA'], label='20MA')

        # MACD图
        # plt.subplot(2, 1, 2)
        # df['EMA12'] = df['Net Worth'].ewm(span=12, adjust=False).mean()
        # df['EMA26'] = df['Net Worth'].ewm(span=26, adjust=False).mean()
        # df['MACD Line'] = df['EMA12'] - df['EMA26']
        # df['Signal Line'] = df['MACD Line'].ewm(span=9, adjust=False).mean()
        # df['Histogram'] = df['MACD Line'] - df['Signal Line']
        # plt.plot(df.index, df['MACD Line'], label='MACD Line', color='blue')
        # plt.plot(df.index, df['Signal Line'], label='Signal Line', color='red')
        # plt.bar(df.index, df['Histogram'], label='Histogram', color='gray')
        # plt.legend(loc='upper left')
        # plt.title('MACD')

        # # RSI图
        # plt.subplot(2, 1, 2)
        # rsi = calculate_rsi(fund_data_list)
        # rsi_dates = [data.date for data in fund_data_list[len(fund_data_list) - len(rsi):]]
        # plt.bar(rsi_dates, rsi, color='blue')
        # plt.xlabel('Date')
        # plt.ylabel('RSI')
        # plt.title('Relative Strength Index (RSI)')
        # plt.xticks(rotation=45)
        # # 添加预警线
        # plt.axhline(y=30, color='red', linestyle='--', label='Oversold (30)')
        # plt.axhline(y=70, color='green', linestyle='--', label='Overbought (70)')

        # 使用微软雅黑字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.show()

        # 历史数据回测策略
        # 在这里根据你的策略逻辑编写具体的交易策略和信号生成规则
        # 你可以使用df中的指标数据和历史净值数据进行判断和计算
        # 以下是一个示例策略，假设当价格上穿布林带的上轨线并且MACD出现金叉时，产生买入信号
        # 定义买入和卖出的信号

        # # 策略一
        # # 买入信号: 当净值下穿布林带的下轨线
        # df['Buy Signal'] = df['Net Worth'] < df['Lower Band']
        # # 卖出信号: 当净值上穿布林带的上轨线
        # df['Sell Signal'] = df['Net Worth'] > df['Upper Band']

        # # 策略二 3.3944 %
        # # 买入信号: 当净值同时上穿10日和20日移动平均线
        # df['Buy Signal'] = (df['10MA'] > df['20MA']) & (df['10MA'].shift(1) < df['20MA'].shift(1))
        # # 卖出信号: 当净值下穿10日移动平均线
        # df['Sell Signal'] = df['Net Worth'] < df['10MA']

        # 策略三 2.198 %
        # 买入信号: 当净值下穿布林带的下轨线时产生买入信号, 并记录买入价格
        df['Buy Signal'] = df['Net Worth'] < df['Lower Band']
        df['Buy Price'] = df['Net Worth'].where(df['Buy Signal'], 0)
        # 卖出信号: 当(净值低于10日移动平均线)或(净值上穿布林带的上轨线)或(净值低于买入价格的95%) 3.2066 %
        # df['Sell Signal'] = (df['Net Worth'] < df['10MA']) \
        #                     | (df['Net Worth'] > df['Upper Band']) \
        #                     | (df['Net Worth'] < df['Buy Price'] * 0.95)
        # 卖出信号: 当(净值向上穿过10日和20日移动平均线后向下穿过10日平均线)或(净值低于买入价格的95%) 3.8635 %
        df['Sell Signal'] = (df['Net Worth'].shift(1) > df['10MA'].shift(1)) \
                            & (df['Net Worth'].shift(1) > df['20MA'].shift(1)) \
                            & (df['Net Worth'] < df['10MA']) \
                            | (df['Net Worth'] < (0.95 * df['Buy Price']))
        # 卖出信号: 当[(昨日净值大于10日移动平均线)且(昨日净值大于20日移动平均线)且(净值低于10日移动平均线)]或(净值上穿布林带的上轨线)或(净值低于买入价格的95%) 1.682 %
        # df['Sell Signal'] = ((df['Net Worth'].shift(1) > df['10MA'].shift(1))
        #                      & (df['Net Worth'].shift(1) > df['20MA'].shift(1))
        #                      & (df['Net Worth'] < df['10MA'])) \
        #                     | (df['Net Worth'] > df['Upper Band']) \
        #                     | (df['Net Worth'] < (0.95 * df['Buy Price']))
        # 卖出信号: 当(净值上穿布林带的上轨线)或(净值低于买入价格的95%)
        # df['Sell Signal'] = (df['Net Worth'] > df['Upper Band']) \
        #                     | (df['Net Worth'] < (0.95 * df['Buy Price']))

        # 计算策略收益率
    #     df['Strategy Returns'] = df['Net Worth'].pct_change()
    #     df['Strategy Returns'] = df['Strategy Returns'].where(~df['Buy Signal'], 0)  # 策略买入时收益为净值的涨幅
    #     df['Strategy Returns'] = df['Strategy Returns'].where(~df['Sell Signal'], 0)  # 策略卖出时收益为0
    #
    #     # 输出回测结果
    #     total_return = round((df['Strategy Returns'] + 1).cumprod()[-1], 4)
    #     all_return += total_return
    #     print('总收益率:', total_return, '% - ', name)
    # # 平均收益率
    # print('平均收益率:', round(all_return / len(fund_code_list), 4), '%')


if __name__ == '__main__':
    main()
