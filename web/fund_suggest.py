# use fastapi lib, listen on 3000 port
import base64
import io
from enum import Enum

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import datestr2num

import api.trend.doctor_xiong_api as api


class FundOperation(Enum):
    BUY = 1
    SELL = 2


class FundDailyNetWorth(object):
    def __init__(self, date, net_worth, **kwargs):
        self.date = date
        self.net_worth = net_worth
        self.operation = kwargs.get('operation', None)


# class FundSuggestDetail(object):
#     def __init__(self, fund_code, fund_daily_net_worth, ten_days_avg_net_worth, twenty_days_avg_net_worth,
#                  suggest_operation, suggest_content, chart_base64):
#         self.fund_code = fund_code
#         self.fund_daily_net_worth = fund_daily_net_worth
#         self.ten_days_avg_net_worth = ten_days_avg_net_worth
#         self.twenty_days_avg_net_worth = twenty_days_avg_net_worth
#         self.suggest_operation = suggest_operation
#         self.suggest_content = suggest_content
#         self.chart_base64 = chart_base64


def get_fund_detail(fund_code, start_date, end_date, today_net_worth) -> (str, str, list):
    """
    get fund details
    :param fund_code: fund code
    :param start_date: yyyy-MM-dd
    :param end_date: yyyy-MM-dd
    :return: error_message, fund name, list of FundDailyNetWorth
    """
    result = api.get_fund_detail(fund_code, start_date, end_date)
    if result is None:
        return None, None, None
    if isinstance(result, str):
        return result, None, None
    fund_name = result.name
    # convert fund_daily_net_worth_list to a list of FundDailyNetWorth from DoctorXiongNetWorthData
    fund_daily_net_worth_list = [FundDailyNetWorth(net_worth_data[0], net_worth_data[1]) for net_worth_data in
                                 result.net_worth_data]
    # if last of fund_daily_net_worth_list is not today, add today's net worth
    if fund_daily_net_worth_list[-1].date != end_date:
        fund_daily_net_worth_list.append(FundDailyNetWorth(end_date, today_net_worth))
    return None, fund_name, fund_daily_net_worth_list


def calculate_moving_average_line(fund_daily_net_worth_list, avg_days) -> list:
    """
    calculate moving average line
    :param fund_daily_net_worth_list: list of FundDailyNetWorth
    :param avg_days: days of moving average
    :return: list of FundDailyNetWorth
    """
    result = []
    for i in range(len(fund_daily_net_worth_list)):
        if i < avg_days - 1:
            result.append(FundDailyNetWorth(fund_daily_net_worth_list[i].date, None))
            continue
    net_worth_array = np.array(
        [float(fund_daily_net_worth.net_worth) for fund_daily_net_worth in fund_daily_net_worth_list])
    moving_avg_array = np.convolve(net_worth_array, np.ones(avg_days) / avg_days, mode='valid')
    moving_avg_data_list = [FundDailyNetWorth(fund_daily_net_worth_list[i + avg_days - 1].date, moving_avg_array[i]) for
                            i in range(len(moving_avg_array))]
    result.extend(moving_avg_data_list)
    return result


def draw_chart(fund_name, fund_code, start_date, end_date, fund_daily_net_worth_list, fund_ten_days_avg_net_worth_list,
               fund_twenty_days_avg_net_worth_list):
    print('last of date is ' + fund_daily_net_worth_list[-1].date + ', last of net worth is ' + str(
        fund_daily_net_worth_list[-1].net_worth))
    plt.figure(figsize=(15, 10))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.title(fund_name + ' - ' + fund_code + ' - ' + start_date + ' - ' + end_date)
    plt.xlabel('日期')
    plt.ylabel('净值')

    x, y = convert_fund_daily_net_worth_list_to_x_y(fund_daily_net_worth_list)

    plt.plot_date(x, y, '-', label='净值')
    x, y_fund_ten_days_avg_net_worth_list = convert_fund_daily_net_worth_list_to_x_y(fund_ten_days_avg_net_worth_list)

    plt.plot_date(x, y_fund_ten_days_avg_net_worth_list, '-', label='10日均线')
    x, y_fund_twenty_days_avg_net_worth_list = convert_fund_daily_net_worth_list_to_x_y(
        fund_twenty_days_avg_net_worth_list)
    plt.plot_date(x, y_fund_twenty_days_avg_net_worth_list, '-', label='20日均线')
    plt.legend()
    # x_ticks是密度比x更小的数组
    x_ticks = [x[i] for i in range(len(x)) if i % 10 == 0]
    if x[-1] not in x_ticks:
        x_ticks.append(x[-1])
    plt.xticks(x_ticks, rotation=45)
    plt.grid()
    # return base64 of chart png, zip it to reduce size, file name is fund_name.png
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read())
    buf.close()

    # save png as a file
    plt.savefig('chart.png')
    plt.close()
    return chart_base64


def convert_fund_daily_net_worth_list_to_x_y(fund_daily_net_worth_list) -> (list, list):
    x = [datestr2num(net_worth_data.date) for net_worth_data in fund_daily_net_worth_list]
    y = []
    for i in range(len(fund_daily_net_worth_list)):
        if fund_daily_net_worth_list[i].net_worth is None:
            y.append(None)
        else:
            y.append(float(fund_daily_net_worth_list[i].net_worth))
    return x, y


def calculate_suggest(fund_daily_net_worth_list, fund_ten_days_avg_net_worth_list,
                      fund_twenty_days_avg_net_worth_list) -> (FundOperation, str):
    pass


if __name__ == '__main__':
    error_message, fund_name, fund_daily_net_worth_list = get_fund_detail("008585", "2023-01-01", "2023-04-16", 1)
    fund_ten_days_moving_average_line = calculate_moving_average_line(fund_daily_net_worth_list, 10)
    fund_twenty_days_moving_average_line = calculate_moving_average_line(fund_daily_net_worth_list, 20)

    chart_base64 = draw_chart(fund_name, "008585", "2023-01-01", "2023-04-17", fund_daily_net_worth_list,
                              fund_ten_days_moving_average_line, fund_twenty_days_moving_average_line)
    print(chart_base64)
