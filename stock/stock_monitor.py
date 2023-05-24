import json

import pandas
import requests

headers = {
    "token": "UPIYr4zGtH"
}


def main():
    code_name_dict_list = get_all_stock_name_code()
    if code_name_dict_list is None:
        return
    total_stock_count = len(code_name_dict_list)
    cnt = 0
    need_monitor_stock_list = []
    for code_name_dict in code_name_dict_list:
        code = code_name_dict['code']
        name = code_name_dict['name']
        try:
            # 输出进度条
            cnt += 1
            print('进度: ' + str(cnt) + '/' + str(total_stock_count))
            stock_net_worth_list = get_stock_daily_net_worth(code)
            if stock_net_worth_list is None:
                continue
            if len(stock_net_worth_list) < 200:
                continue
            # columns=['close', 'volume'],
            data_frame = pandas.DataFrame(
                stock_net_worth_list,
                columns=['date', 'open', 'close', 'high', 'low', 'volume']
            )
            data_frame = calculate_move_average_line(data_frame, 50)
            data_frame = calculate_move_average_line(data_frame, 200)
            data_frame = calculate_move_average_volume_line(data_frame, 5)
            data_frame = calculate_move_average_volume_line(data_frame, 10)
            data_frame = calculate_move_average_volume_line(data_frame, 30)
            # 如果最后一条数据: (50日线在200日线之上) && (今日收盘价在50日线之上), 输出code和name
            if not data_frame.iloc[-1]['ma_200'] < data_frame.iloc[-1]['ma_50'] < data_frame.iloc[-1]['close']:
                continue
            if not data_frame.iloc[-1]['mav_5'] < data_frame.iloc[-1]['mav_10'] < data_frame.iloc[-1]['mav_30']:
                continue
            # 从三天前开始, 向前7日内, 持续mav5 < mav10 < mav30, 符合条件的, 不是持续低成交量需要专注的, 就是成交量已经快速提升的
            keeping_low_volume_flag = True
            for index in range(3, 11):
                if not data_frame.iloc[-index]['mav_5'] < data_frame.iloc[-index]['mav_10'] \
                       < data_frame.iloc[-index]['mav_30']:
                    keeping_low_volume_flag = False
                    break
            if not keeping_low_volume_flag:
                continue
            need_monitor_stock_list.append({
                'code': code,
                'name': name
            })
        except Exception as e:
            print(code, name, '出现异常: ' + str(e))
            continue
    print('需要关注的股票列表: ')
    print(need_monitor_stock_list)


def get_all_stock_name_code():
    url = 'https://api.doctorxiong.club/v1/stock/all'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print('请求失败')
        return None
    data_list = json.loads(response.text)['data']
    code_name_dict_list = []
    for data in data_list:
        code_name_dict_list.append({
            'code': data[0],
            'name': data[1]
        })
    return code_name_dict_list


def get_stock_daily_net_worth(code):
    url = 'https://api.doctorxiong.club/v1/stock/kline/day'
    params = {
        'code': code,
        'startDate': '2022-01-01',
        'endDate': '2023-05-23',
        'type': 1
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('请求失败')
        return None
    data_list = json.loads(response.text)['data']
    stock_net_worth_list = []
    for data in data_list:
        stock_net_worth_list.append({
            'date': data[0],
            'open': float(data[1]),
            'close': float(data[2]),
            'high': float(data[3]),
            'low': float(data[4]),
            'volume': float(data[5])
        })
    return stock_net_worth_list


def calculate_move_average_line(data_frame, time_window):
    # 使用收盘价计算移动平均线
    data_frame['ma_' + str(time_window)] = data_frame['close'].rolling(window=time_window).mean()
    return data_frame


def calculate_move_average_volume_line(data_frame, time_window):
    # 使用成交量计算移动平均线
    data_frame['mav_' + str(time_window)] = data_frame['volume'].rolling(window=time_window).mean()
    return data_frame


if __name__ == '__main__':
    main()
