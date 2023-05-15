import json

import matplotlib.pyplot as plt
import requests
from matplotlib.pylab import datestr2num

from api.trend.doctor_xiong_api import get_fund_detail
from api.trend.doctor_xiong_model import DoctorXiongFundDetail, DoctorXiongNetWorthData


def main():
    start_date = '2022-01-01'
    end_date = '2023-05-15'

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
        suggest(start_date, end_date, fund_detail, today_net_worth, name, fund_code)


def get_fund_real_time_net_worth(fund_code: str):
    url = 'http://fundgz.1234567.com.cn/js/' + fund_code + '.js'
    r = requests.get(url)
    net_worth_info = r.text
    json_str = net_worth_info[8:-2]
    json_object = json.loads(json_str)
    real_time_net_worth = json_object['gsz']
    name = json_object['name']
    return name, float(real_time_net_worth)


def suggest(start_date, end_date, fund_detail, today_net_worth, name, fund_code):
    net_worth_data_list = fund_detail.get_net_worth_data_list()
    # 添加当日最新净值
    net_worth_data_list.append(DoctorXiongNetWorthData([end_date, today_net_worth, '', '']))
    # use matplotlib, draw a line chart
    x = [datestr2num(net_worth_data.date) for net_worth_data in net_worth_data_list]
    y = [float(net_worth_data.net_worth) for net_worth_data in net_worth_data_list]
    daily_5_avg_net_worth = calculate_daily_avg_net_worth(net_worth_data_list, 5)
    daily_10_avg_net_worth = calculate_daily_avg_net_worth(net_worth_data_list, 10)
    daily_20_avg_net_worth = calculate_daily_avg_net_worth(net_worth_data_list, 20)
    daily_60_avg_net_worth = calculate_daily_avg_net_worth(net_worth_data_list, 60)

    # 获取10和20日均线最后一个值中更高的那个
    today_higher_avg_net_worth = round(max(daily_10_avg_net_worth[-1], daily_20_avg_net_worth[-1]), 4)
    # 如果昨日净值小于today_higher_avg_net_worth，且今日净值大于today_higher_avg_net_worth，买入
    yesterday_net_worth = float(net_worth_data_list[-2].net_worth)

    show_chart(daily_5_avg_net_worth, daily_10_avg_net_worth, daily_20_avg_net_worth, daily_60_avg_net_worth,
                   end_date, fund_detail, start_date, x, y)

    if yesterday_net_worth < today_higher_avg_net_worth and today_net_worth > today_higher_avg_net_worth:
        over_net_worth = (today_net_worth - today_higher_avg_net_worth)
        over_percent = round(over_net_worth / today_higher_avg_net_worth * 100, 4)
        print(fund_code, name)
        print('昨日净值', yesterday_net_worth, '今日净值', today_net_worth, '今日10日均值和20日均值中的较高值', today_higher_avg_net_worth)
        print('推荐买入\n')
        # show_chart(daily_5_avg_net_worth, daily_10_avg_net_worth, daily_20_avg_net_worth, daily_60_avg_net_worth,
        #                end_date, fund_detail, start_date, x, y)
    # 如果昨日净值大于today_higher_avg_net_worth，且今日净值小于today_higher_avg_net_worth，卖出
    elif yesterday_net_worth > today_higher_avg_net_worth and today_net_worth < today_higher_avg_net_worth:
        over_net_worth = (today_higher_avg_net_worth - today_net_worth)
        over_percent = round(over_net_worth / today_higher_avg_net_worth * 100, 4)
        print(fund_code, name)
        print('昨日净值', yesterday_net_worth, '今日净值', today_net_worth, '今日10日均值和20日均值中的较高值', today_higher_avg_net_worth)
        print('推荐卖出\n')
        # show_chart(daily_5_avg_net_worth, daily_10_avg_net_worth, daily_20_avg_net_worth, daily_60_avg_net_worth,
        #                end_date, fund_detail, start_date, x, y)
    # 如果今日净值大于today_higher_avg_net_worth, 继续持有©
    # elif today_net_worth > today_higher_avg_net_worth:
    #     over_net_worth = (today_net_worth - today_higher_avg_net_worth)
    #     over_percent = round(over_net_worth / today_higher_avg_net_worth * 100, 4)
    #     print(name, fund_code, today_net_worth, "10日均值和20日均值中的较高值" + str(over_percent) + '%')
    #     print(round(daily_10_avg_net_worth[-1], 4), round(daily_20_avg_net_worth[-1], 4))
    #     print('推荐继续持有\n')
        # show_chart(daily_5_avg_net_worth, daily_10_avg_net_worth, daily_20_avg_net_worth, daily_60_avg_net_worth,
        #                end_date, fund_detail, start_date, x, y)


def show_chart(daily_5_avg_net_worth, daily_10_avg_net_worth, daily_20_avg_net_worth, daily_60_avg_net_worth, end_date,
               fund_detail,
               start_date, x, y):
    plt.figure(figsize=(15, 10))
    plt.rcParams['font.sans-serif'] = ['Songti SC']
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
    # x_ticks是60个, 平均分布
    x_ticks = [x[i] for i in range(0, len(x), int(len(x) / 60))]
    x_ticks.append(x[-1])
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
            avg_net_worth_list.append(
                sum([float(net_worth_data_list[i - j].net_worth) for j in range(avg_days)]) / avg_days)
    return avg_net_worth_list


if __name__ == '__main__':
    main()
