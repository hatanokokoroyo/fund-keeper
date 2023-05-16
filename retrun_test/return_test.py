import json

import pandas
import pandas as pd
import requests
from matplotlib import pyplot as plt

from api.trend.doctor_xiong_api import get_fund_detail
from api.trend.doctor_xiong_model import DoctorXiongNetWorthData
from stragegy.double_move_average_line_strategy import DoubleMoveAverageLineStrategyImpl
from stragegy.bollinger_bands_strategy import BollingerBandsStrategyImpl
from stragegy.strategy import FundOperation
from index.bollinger_bands_indicator import calculate_bollinger_bands
from index.move_average_line_indicator import calculate_move_average_line

show_chart_flag = False
bollinger_bands_time_window = 30
bollinger_bands_standard_deviation = 2.5

end_date = '2023-05-15'
years = 3
# end_date - years
start_date = pd.to_datetime(end_date) - pd.DateOffset(years=years)


def main():
    # strategy = DoubleMoveAverageLineStrategyImpl()
    strategy = BollingerBandsStrategyImpl()
    return_test(strategy, start_date, end_date, years)


def return_test(strategy, start_date, end_date, years):
    """
    计算收益率
    :param years:
    :param strategy: 策略
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return:  data_frame include columns: MA<time_window>
    """
    fund_code_list = get_fund_code_list_for_test()
    return_rate_is_zero_fund_code_list = []
    return_rate_less_than_5_fund_code_list = []
    return_rate_greater_than_5_fund_code_list = []
    total_return_rate = 0
    for fund_code in fund_code_list:
        # 三年年化利率
        return_rate, fund_name = calculate_return_rate(fund_code, strategy, start_date, end_date)
        if return_rate == 0:
            return_rate_is_zero_fund_code_list.append({fund_code, return_rate, fund_name})
            continue
        if return_rate < 0.05:
            return_rate_less_than_5_fund_code_list.append([fund_code, return_rate, fund_name])
        else:
            return_rate_greater_than_5_fund_code_list.append([fund_code, return_rate, fund_name])
        total_return_rate += return_rate
    print('三年平均年化利率: ' + str(
        total_return_rate / (len(fund_code_list) - len(return_rate_is_zero_fund_code_list)) / years))
    print('以下基金收益率为0: ' + str(return_rate_is_zero_fund_code_list))
    print('以下基金年化收益率小于5%: ' + str(return_rate_less_than_5_fund_code_list))
    print('以下基金年化收益率大于5%: ' + str(return_rate_greater_than_5_fund_code_list))


def get_fund_code_list_for_test():
    fund_code_list = [
        '016814', '004598', '012863', '001156', '400015', '012832', '017482', '006229', '013311', '001856', '010149',
        '011103', '008702', '006221', '005506', '016814', '004598', '007882', '008591', '015675', '004855', '012863',
        '014111', '012832', '400015', '001156', '005064', '010149', '006229', '011036', '006221', '010210', '012549',
        '012414', '013311', '008089', '001676', '005506', '001676', '011103', '011840', '011463', '009180', '007818',
        '008702', '013081', '013219', '008591', '005918', '016814', '012810', '004598', '007882', '008087', '012769',
        '008586', '005224', '017090', '014130', '012637', '012615', '017482', '001924', '002258', '001678', '013621',
        '010769', '017484', '006166', '001856', '008888', '320007',
    ]
    return set(fund_code_list)


def calculate_return_rate(fund_code, strategy, start_date, end_date):
    """
    计算单个基金的收益率
    :param fund_code: 基金代码
    :param strategy: 策略类
    :param start_date: 开始时间
    :param end_date: 结束时间
    :return:
    """
    print('============================================================')
    buy_amount = 100
    current_buy_count = 0
    total_cost = 0

    # 总盈利值
    total_profit = 0
    # 当前买入价格
    hold_price = 0
    # 当前持有数量
    hold_number = 0
    # 当前买入时间
    last_buy_date = None
    # 查询基金在指定时间内的历史净值
    fund_name, net_worth_data_list = get_fund_detail2(fund_code, start_date, end_date)
    # 从第三十天开始计算
    for i in range(30, len(net_worth_data_list)):
        current_net_worth_data_list = net_worth_data_list[0:i]
        data_frame = convert_net_worth_list_to_data_frame(current_net_worth_data_list)
        fund_operation = strategy.execute_strategy(data_frame, bollinger_bands_time_window=bollinger_bands_time_window,
                                                   bollinger_bands_standard_deviation=bollinger_bands_standard_deviation,
                                                   hold_price=hold_price,
                                                   hold_number=hold_number)

        today_net_worth = current_net_worth_data_list[-1].net_worth
        today = current_net_worth_data_list[-1].date
        if fund_operation == FundOperation.BUY:
            buy_number = round(buy_amount / today_net_worth, 2)
            if hold_number == 0:
                hold_price = today_net_worth
            else:
                hold_price = round(
                    (hold_price * hold_number + today_net_worth * buy_number) / (hold_number + buy_number), 4
                )
            hold_number += buy_number
            last_buy_date = net_worth_data_list[i].date
            current_buy_count += 1
            print('买入日期:', last_buy_date, '买入价格:', hold_price, '买入数量:', buy_number, '持仓价格:', hold_price,
                  '持仓数量:', hold_number)
            # 记录买入点
            current_net_worth_data_list[-1].operation = FundOperation.BUY
        elif fund_operation == FundOperation.SELL and hold_number > 0:
            sell_price = net_worth_data_list[i].net_worth
            profit = round((sell_price - hold_price) * hold_number, 4)
            total_profit += profit
            print('卖出日期:', today, '卖出价格:', sell_price, '卖出数量:', hold_number, '持仓价格:', hold_price,
                  '盈利:', profit)
            hold_number = 0
            last_buy_date = None
            total_cost = current_buy_count * buy_amount
            # 记录卖出点
            current_net_worth_data_list[-1].operation = FundOperation.SELL
    if total_cost != 0:
        return_rate = round(total_profit / total_cost, 4)
    else:
        return_rate = 0
    print(fund_code, 'current period cost:', total_cost, 'total profit:', round(total_profit, 4), ', return rate:',
          return_rate, fund_name)
    # net_worth_data_list生成折线图
    show_chart(net_worth_data_list, fund_code, fund_name, return_rate)

    return return_rate, fund_name


def get_fund_detail2(fund_code: str, start_date, end_date):
    fund_detail = get_fund_detail(fund_code, start_date, end_date)
    net_worth_data_list = fund_detail.get_net_worth_data_list()
    # if last day is not today, add today's net worth
    if net_worth_data_list[-1].date != end_date:
        name, today_net_worth = get_fund_real_time_net_worth(fund_code)
        net_worth_data_list.append(DoctorXiongNetWorthData([end_date, today_net_worth, '', '']))
    return fund_detail.name, net_worth_data_list


def get_fund_real_time_net_worth(fund_code: str):
    url = 'http://fundgz.1234567.com.cn/js/' + fund_code + '.js'
    r = requests.get(url)
    net_worth_info = r.text
    json_str = net_worth_info[8:-2]
    json_object = json.loads(json_str)
    real_time_net_worth = json_object['gsz']
    name = json_object['name']
    return name, float(real_time_net_worth)


def convert_net_worth_list_to_data_frame(fund_data_list: list) -> pandas.DataFrame:
    data_frame = pd.DataFrame([(data.date, data.net_worth) for data in fund_data_list],
                              columns=['date', 'net_worth'])
    return data_frame


def show_chart(net_worth_data_list: list, fund_code, fund_name, return_rate):
    """
    显示基金净值折线图, 根据operation字段区分买入点和卖出点
    :param fund_code:
    :param fund_name:
    :param return_rate:
    :param net_worth_data_list: 基金净值数据列表
    :return:
    """
    if not show_chart_flag:
        return None
    data_frame = pd.DataFrame([(data.date, data.net_worth, data.operation) for data in net_worth_data_list],
                              columns=['date', 'net_worth', 'operation'])
    data_frame.plot(x='date', y='net_worth', kind='line')
    # calculate bollinger bands
    data_frame = calculate_bollinger_bands(data_frame, bollinger_bands_time_window, bollinger_bands_standard_deviation)
    # calculate 10 and 20 moving average line
    data_frame = calculate_move_average_line(data_frame, 10)
    data_frame = calculate_move_average_line(data_frame, 20)

    plt.plot(data_frame['date'], data_frame['upper_band'], color='red', label='upper band')
    plt.plot(data_frame['date'], data_frame['middle_band'], color='pink', label='middle band')
    plt.plot(data_frame['date'], data_frame['lower_band'], color='green', label='lower band')
    plt.fill_between(data_frame.index, data_frame['lower_band'], data_frame['upper_band'], alpha=0.2)  # 填充布林带之间的区域

    plt.plot(data_frame['date'], data_frame['net_worth'], color='blue', label='net worth')
    # 买入卖出点
    buy_point = data_frame[data_frame['operation'] == FundOperation.BUY]
    sell_point = data_frame[data_frame['operation'] == FundOperation.SELL]
    plt.scatter(buy_point['date'], buy_point['net_worth'], color='red', label='buy point')
    plt.scatter(sell_point['date'], sell_point['net_worth'], color='green', label='sell point')

    plt.plot(data_frame['date'], data_frame['ma10'], color='yellow', label='10 move average')
    plt.plot(data_frame['date'], data_frame['ma20'], color='black', label='20 move average')

    plt.legend(loc='best')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.title(fund_code + ' - ' + fund_name + ' - 年化利率' + str(round(return_rate, 4)))
    plt.show()


if __name__ == '__main__':
    main()
