import datetime
import json

import pandas
import pandas as pd
import requests

from api.trend.doctor_xiong_api import get_fund_detail
from api.trend.doctor_xiong_model import DoctorXiongNetWorthData
from index.bollinger_bands_indicator import calculate_bollinger_bands
from index.move_average_line_indicator import calculate_move_average_line


def main():
    fund_code_list = [
        '016814', '004598', '012863', '001156', '400015', '012832', '017482', '006229', '013311', '001856', '010149',
        '011103', '008702', '006221', '005506', '016814', '004598', '007882', '008591', '015675', '004855', '012863',
        '014111', '012832', '400015', '001156', '005064', '010149', '006229', '011036', '006221', '010210', '012549',
        '012414', '013311', '008089', '001676', '005506', '001676', '011103', '011840', '011463', '009180', '007818',
        '008702', '013081', '013219', '008591', '005918', '016814', '012810', '004598', '007882', '008087', '012769',
        '008586', '005224', '017090', '014130', '012637', '012615', '017482', '001924', '002258', '001678', '013621',
        '010769', '017484', '006166', '001856', '008888', '320007',
    ]
    fetched_fund_code_list = []
    for fund_code in fund_code_list:
        if fund_code in fetched_fund_code_list:
            continue
        fetched_fund_code_list.append(fund_code)

        fund_code, fund_name, net_worth_data_list = get_fund_detail_include_one_year_net_worth_history(fund_code)
        data_frame = convert_net_worth_list_to_data_frame(net_worth_data_list)
        data_frame = calculate_bollinger_bands(data_frame)
        data_frame = calculate_move_average_line(data_frame, 5)
        data_frame = calculate_move_average_line(data_frame, 10)
        data_frame = calculate_move_average_line(data_frame, 20)

        net_worth_list = data_frame['net_worth'].array
        yesterday_net_worth = net_worth_list[-2]
        today_net_worth = net_worth_list[-1]

        bollinger_upper_band = data_frame['upper_band'].array
        bollinger_middle_band = data_frame['middle_band'].array
        bollinger_lower_band = data_frame['lower_band'].array
        today_bollinger_upper_band = bollinger_upper_band[-1]
        today_bollinger_middle_band = bollinger_middle_band[-1]
        today_bollinger_lower_band = bollinger_lower_band[-1]

        ma5 = data_frame['ma5'].array

        if yesterday_net_worth >= today_bollinger_lower_band > today_net_worth:
            print(fund_code, fund_name, '净值向下突破布林带下轨线, 当前净值: ', today_net_worth)
        # 如果(今日净值在中轨线之上)且(昨日净值在5日均线之下)且(今日净值在5日均线之上)
        # if today_net_worth > bollinger_middle_band[-1] and yesterday_net_worth <= ma5[-2] and today_net_worth > ma5[-1]:
        #     print(fund_code, '净值在中轨线之上且向上突破5日均线, 当前净值: ', today_net_worth, fund_name)
        # 如果(今日净值在中轨线之上)且(昨日净值在5日均线之上)且(今日净值在5日均线之下)
        # if bollinger_middle_band[-1] < today_net_worth < ma5[-1] and yesterday_net_worth >= ma5[-2]:
        #     print(fund_code, '净值在中轨线之上且向下突破5日均线, 当前净值: ', today_net_worth, fund_name)
        # 如果(今日净值在中轨线之下)且(昨日净值在5日均线之下)且(今日净值在5日均线之上)
        if bollinger_middle_band[-1] > today_net_worth > ma5[-1] and yesterday_net_worth <= ma5[-2]:
            print(fund_code, '净值在中轨线之下且向上突破5日均线, 当前净值: ', today_net_worth, fund_name)


def get_fund_detail_include_one_year_net_worth_history(fund_code: str):
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    fund_detail = get_fund_detail(fund_code, start_date, end_date)
    new_worth_data_list = fund_detail.get_net_worth_data_list()
    # if last day is not today, add today's net worth
    if new_worth_data_list[-1].date != end_date:
        name, today_net_worth = get_fund_real_time_net_worth(fund_code)
        new_worth_data_list.append(DoctorXiongNetWorthData([end_date, today_net_worth, '', '']))
    return fund_code, fund_detail.name, new_worth_data_list


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
    data_frame = pd.DataFrame([(data.date, data.net_worth) for data in fund_data_list], columns=['date', 'net_worth'])
    return data_frame


if __name__ == '__main__':
    main()
