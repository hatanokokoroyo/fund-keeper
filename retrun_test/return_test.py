import pandas


def return_test(strategy, start_date, end_date):
    """
    计算收益率
    :param strategy: 策略
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return:  data_frame include columns: MA<time_window>
    """
    fund_code_list = get_fund_code_list_for_test()
    for fund_code in fund_code_list:
        return_rate = calculate_return_rate(fund_code, strategy, start_date, end_date)


def get_fund_code_list_for_test():
    return [
        '016814', '004598', '012863', '001156', '400015', '012832', '017482', '006229', '013311', '001856', '010149',
        '011103', '008702', '006221', '005506', '016814', '004598', '007882', '008591', '015675', '004855', '012863',
        '014111', '012832', '400015', '001156', '005064', '010149', '006229', '011036', '006221', '010210', '012549',
        '012414', '013311', '008089', '001676', '005506', '001676', '011103', '011840', '011463', '009180', '007818',
        '008702', '013081', '013219', '008591', '005918', '016814', '012810', '004598', '007882', '008087', '012769',
        '008586', '005224', '017090', '014130', '012637', '012615', '017482', '001924', '002258', '001678', '013621',
        '010769', '017484', '006166', '001856', '008888', '320007',
    ]


def calculate_return_rate(fund_code, strategy, start_date, end_date):
    """
    计算单个基金的收益率
    :param fund_code: 基金代码
    :param strategy: 策略类
    :param start_date: 开始时间
    :param end_date: 结束时间
    :return:
    """
    # 总盈利值
    total_profit = 0
    # 当前买入金额
    current_buy_amount = 0
    # 当前买入时间
    current_buy_date = None
    # 查询基金在指定时间内的历史净值
    
