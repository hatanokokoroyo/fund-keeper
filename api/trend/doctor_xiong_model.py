from utils.json_utils import *
import json


class DoctorXiongApiResponse(object):
    def __init__(self, code: int, message: str, **kwargs):
        self.code = code,
        self.message = message
        self.data = kwargs.get('data', None)

    def get_fund_detail(self):
        data = self.data[0]
        return DoctorXiongFundDetail(data)


class DoctorXiongFundDetail(object):
    def __init__(self, data):
        """
        :param data: dict, may be in the following fields
         code: 基金代码
         name: 基金名称
         type: 基金类型
         net_worth: 当前基金单位净值
         expect_worth: 当前基金单位净值估算
         total_worth: 当前基金累计净值
         expect_growth: 当前基金单位净值估算日涨幅,单位为百分比
         day_growth: 单位净值日涨幅,单位为百分比
         last_week_growth: 单位净值周涨幅,单位为百分比
         last_month_growth: 单位净值月涨幅,单位为百分比
         last_three_months_growth: 单位净值三月涨幅,单位为百分比
         last_six_months_growth: 单位净值六月涨幅,单位为百分比
         last_year_growth: 单位净值年涨幅,单位为百分比
         buy_min: 起购额度
         buy_source_rate: 原始买入费率,单位为百分比
         buy_rate: 当前买入费率,单位为百分比
         manager: 基金经理
         fund_scale: 基金规模及日期,日期为最后一次规模变动的日期
         worth_date: 净值更新日期,日期格式为yy-MM-dd HH:mm.2019-06-27 15:00代表当天下午3点
         expect_worth_date: 净值估算更新日期,,日期格式为yy-MM-dd HH:mm.2019-06-27 15:00代表当天下午3点
         net_worth_data: 历史净值信息["2001-12-18" , 1 , 0 , ""]依次表示:日期; 单位净值; 净值涨幅; 每份分红.
         million_copies_income: 每万分收益(货币基金)
         million_copies_income_data: 历史万每分收益信息(货币基金)["2016-09-23",0.4773]依次表示:日期; 每万分收益.
         million_copies_income_date: 七日年化收益更新日期(货币基金)
         seven_days_year_income: 七日年化收益(货币基金)
         seven_days_year_income_data: 历史七日年华收益信息(货币基金)["2016-09-23",2.131]依次表示:日期; 七日年化收益.
        """

        def get_value(key): return data.get(key, None)

        self.code = get_value('code')
        self.name = get_value('name')
        self.type = get_value('type')
        self.net_worth = get_value('net_worth')
        self.expect_worth = get_value('expect_worth')
        self.total_worth = get_value('total_worth')
        self.expect_growth = get_value('expect_growth')
        self.day_growth = get_value('day_growth')
        self.last_week_growth = get_value('last_week_growth')
        self.last_month_growth = get_value('last_month_growth')
        self.last_three_months_growth = get_value('last_three_months_growth')
        self.last_six_months_growth = get_value('last_six_months_growth')
        self.last_year_growth = get_value('last_year_growth')
        self.buy_min = get_value('buy_min')
        self.buy_source_rate = get_value('buy_source_rate')
        self.buy_rate = get_value('buy_rate')
        self.manager = get_value('manager')
        self.fund_scale = get_value('fund_scale')
        self.worth_date = get_value('worth_date')
        self.expect_worth_date = get_value('expect_worth_date')
        self.net_worth_data = get_value('net_worth_data')
        self.million_copies_income = get_value('million_copies_income')
        self.million_copies_income_data = get_value('million_copies_income_data')
        self.million_copies_income_date = get_value('million_copies_income_date')
        self.seven_days_year_income = get_value('seven_days_year_income')
        self.seven_days_year_income_data = get_value('seven_days_year_income_data')

    def get_net_worth_data_list(self) -> list or None:
        if self.net_worth_data is None:
            return None
        net_worth_data_list = []
        for data in self.net_worth_data:
            net_worth_data_list.append(DoctorXiongNetWorthData(data))
        return net_worth_data_list


class DoctorXiongNetWorthData(object):
    def __init__(self, net_worth_data_array):
        self.date = net_worth_data_array[0]
        self.net_worth = float(net_worth_data_array[1])
        self.growth = net_worth_data_array[2]
        self.dividend = net_worth_data_array[3]
