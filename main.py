import matplotlib.pyplot as plt
from matplotlib.pylab import datestr2num

from api.trend.doctor_xiong_api import get_fund_detail
from api.trend.doctor_xiong_model import DoctorXiongFundDetail


def main():
    code = '010149'
    start_date = '2021-01-01'
    end_date = '2023-04-15'
    fund_detail = get_fund_detail(code, start_date, end_date)
    if not isinstance(fund_detail, DoctorXiongFundDetail):
        print('error')
        return
    net_worth_data_list = fund_detail.get_net_worth_data_list()
    # use matplotlib, draw a line chart
    x = [datestr2num(net_worth_data.date) for net_worth_data in net_worth_data_list]

    y = [float(net_worth_data.net_worth) for net_worth_data in net_worth_data_list]

    daily_5_avg_net_worth = calculate_daily_avg_net_worth(net_worth_data_list, 5)
    daily_10_avg_net_worth = calculate_daily_avg_net_worth(net_worth_data_list, 10)
    daily_20_avg_net_worth = calculate_daily_avg_net_worth(net_worth_data_list,20 )
    daily_60_avg_net_worth = calculate_daily_avg_net_worth(net_worth_data_list, 60)

    plt.figure(figsize=(15, 10))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.title(fund_detail.name + ' - ' + fund_detail.code + ' - ' + start_date + ' - ' + end_date)
    plt.xlabel('日期')
    plt.ylabel('净值')

    plt.plot_date(x, y, '-', label='净值')
    # 打印daily_10_avg_net_worth, 并且标上名字
    # plt.plot_date(x, daily_5_avg_net_worth, '-', label='5日均线')
    plt.plot_date(x, daily_10_avg_net_worth, '-', label='10日均线')
    # 打印daily_20_avg_net_worth, 并且标上名字
    plt.plot_date(x, daily_20_avg_net_worth, '-', label='20日均线')
    # 打印daily_60_avg_net_worth, 并且标上名字
    plt.plot(x, daily_60_avg_net_worth, label='60日均线')
    plt.legend()
    # x_ticks是密度比x更小的数组
    x_ticks = [x[i] for i in range(len(x)) if i % 10 == 0]
    plt.xticks(x_ticks, rotation=45)
    plt.grid()
    plt.show()


def calculate_daily_avg_net_worth(net_worth_data_list, avg_days: int) -> list:
    """
    计算均线
    :param net_worth_data_list:
    :param avg_days:
    :return:
    """
    avg_net_worth_list = []

    for i in range(len(net_worth_data_list)):
        if i < avg_days:
            avg_net_worth_list.append(None)
        else:
            avg_net_worth_list.append(sum([float(net_worth_data_list[i - j].net_worth) for j in range(avg_days)]) / avg_days)
    return avg_net_worth_list


if __name__ == '__main__':
    main()
