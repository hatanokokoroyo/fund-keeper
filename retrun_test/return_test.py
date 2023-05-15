import json

import pandas
import pandas as pd
import requests

from api.trend.doctor_xiong_api import get_fund_detail
from api.trend.doctor_xiong_model import DoctorXiongNetWorthData
from stragegy.double_move_average_line_strategy import DoubleMoveAverageLineStrategyImpl
from stragegy.bollinger_bands_strategy import BollingerBandsStrategyImpl
from stragegy.strategy import FundOperation


def main():
    start_date = '2020-05-15'
    # start_date = '2020-05-15'
    end_date = '2023-05-15'
    # strategy = DoubleMoveAverageLineStrategyImpl()
    strategy = BollingerBandsStrategyImpl()
    return_test(strategy, start_date, end_date)


def return_test(strategy, start_date, end_date):
    """
    计算收益率
    :param strategy: 策略
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return:  data_frame include columns: MA<time_window>
    """
    fund_code_list = get_fund_code_list_for_test()
    total_return_rate = 0
    for fund_code in fund_code_list:
        # 三年年化利率
        return_rate = calculate_return_rate(fund_code, strategy, start_date, end_date)
        total_return_rate += return_rate
    print('三年平均年化利率: ' + str(total_return_rate / len(fund_code_list) / 3))


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
        fund_operation = strategy.execute_strategy(data_frame, hold_price=hold_price,
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
            print('买入日期:', last_buy_date, '买入价格:', hold_price, '买入数量:', buy_number, '持仓价格:', hold_price,
                  '持仓数量:', hold_number)
        elif fund_operation == FundOperation.SELL and hold_number > 0:
            sell_price = net_worth_data_list[i].net_worth
            profit = round((sell_price - hold_price) * hold_number, 4)
            total_profit += profit
            print('卖出日期:', today, '卖出价格:', sell_price, '卖出数量:', hold_number, '持仓价格:', hold_price, '盈利:', profit)
            current_buy_price = None
            hold_number = 0
            last_buy_date = None
    return_rate = round(total_profit / buy_amount, 4)
    print(fund_code, 'total profit:', round(total_profit, 4), ', return rate:', return_rate)
    return return_rate


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


if __name__ == '__main__':
    main()
