import matplotlib.pyplot as plt

from api.trend.doctor_xiong_api import get_fund_detail
from api.trend.doctor_xiong_model import FundDetail


def main():
    code = '012364'
    start_date = '2022-04-01'
    end_date = '2023-04-10'
    fund_detail = get_fund_detail(code, start_date, end_date)
    if not isinstance(fund_detail, FundDetail):
        print('error')
        return
    net_worth_data_list = fund_detail.get_net_worth_data_list()
    # use matplotlib, draw a line chart
    # max_y = max([net_worth_data.net_worth for net_worth_data in net_worth_data_list])
    # min_y = min([net_worth_data.net_worth for net_worth_data in net_worth_data_list])
    x = [net_worth_data.date for net_worth_data in net_worth_data_list]
    y = [float(net_worth_data.net_worth) for net_worth_data in net_worth_data_list]

    daily_10_avg_net_worth = calculate_10_daily_avg_net_worth(net_worth_data_list)
    daily_20_avg_net_worth = calculate_20_daily_avg_net_worth(net_worth_data_list)
    daily_60_avg_net_worth = calculate_60_daily_avg_net_worth(net_worth_data_list)

    plt.figure(figsize=(10, 5))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.title(fund_detail.name + ' - ' + fund_detail.code + ' - ' + start_date + ' - ' + end_date)
    plt.xlabel('日期')
    plt.ylabel('净值')

    plt.plot(x, y)
    # 打印daily_10_avg_net_worth, 并且标上名字

    plt.plot(x, daily_10_avg_net_worth, label='10日均线')
    # 打印daily_20_avg_net_worth, 并且标上名字
    plt.plot(x, daily_20_avg_net_worth, label='20日均线')
    # 打印daily_60_avg_net_worth, 并且标上名字
    # plt.plot(x, daily_60_avg_net_worth, label='60日均线')
    plt.show()


def calculate_10_daily_avg_net_worth(net_worth_data_list) -> list:
    """
    计算10日均线
    :param net_worth_data_list:
    :return:
    """
    avg_net_worth_list = []

    for i in range(len(net_worth_data_list)):
        if i < 10:
            avg_net_worth_list.append(0)
        else:
            avg_net_worth_list.append(sum([float(net_worth_data_list[i - j].net_worth) for j in range(10)]) / 10)
    return avg_net_worth_list


def calculate_20_daily_avg_net_worth(net_worth_data_list) -> list:
    """
    计算20日均线
    :param net_worth_data_list:
    :return:
    """
    avg_net_worth_list = []

    for i in range(len(net_worth_data_list)):
        if i < 20:
            avg_net_worth_list.append(0)
        else:
            avg_net_worth_list.append(sum([float(net_worth_data_list[i - j].net_worth) for j in range(20)]) / 20)
    return avg_net_worth_list


def calculate_60_daily_avg_net_worth(net_worth_data_list) -> list:
    """
    计算60日均线
    :param net_worth_data_list:
    :return:
    """
    avg_net_worth_list = []

    for i in range(len(net_worth_data_list)):
        if i < 60:
            avg_net_worth_list.append(0)
        else:
            avg_net_worth_list.append(sum([float(net_worth_data_list[i - j].net_worth) for j in range(60)]) / 60)
    return avg_net_worth_list


if __name__ == '__main__':
    main()
