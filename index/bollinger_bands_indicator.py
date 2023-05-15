import pandas


def calculate_bollinger_bands(data_frame: pandas.DataFrame, time_window: int = 20,
                              std_diff_multiple: float = 2) -> pandas.DataFrame:
    """
    计算布林带指标
    :param data_frame: | 日期 | 净值 |
    :param time_window: 时间窗口大小(日)
    :param std_diff_multiple:  标准差倍数
    :return:  data_frame include columns: time_window, std, middle_band, upper_band, lower_band
    """
    data_frame['time_window'] = time_window
    # 计算中轨线
    data_frame['middle_band'] = data_frame['net_worth'].rolling(window=time_window).mean()
    # 计算标准差
    data_frame['std'] = data_frame['net_worth'].rolling(window=time_window).std()
    # 计算上轨线
    data_frame['upper_band'] = data_frame['middle_band'] + std_diff_multiple * data_frame['std']
    # 计算下轨线
    data_frame['lower_band'] = data_frame['middle_band'] - std_diff_multiple * data_frame['std']
    return data_frame
