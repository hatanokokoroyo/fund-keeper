import pandas


def calculate_move_average_line(data_frame: pandas.DataFrame, time_window: int) -> pandas.DataFrame:
    """
    计算移动平均线
    :param data_frame: | 日期 | 净值 |
    :param time_window: 时间窗口大小(日)
    :return:  data_frame include columns: MA<time_window>
    """
    data_frame['MA' + str(time_window)] = data_frame['Net Worth'].rolling(time_window).mean()
    return data_frame
