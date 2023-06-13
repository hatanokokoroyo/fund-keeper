from typing import List


class Stock(object):
    def __init__(self, **kwargs):
        self.name: str = kwargs.get('name')
        self.code: str = kwargs.get('code')
        self.time_net_worth_list: List[NetWorth] = kwargs.get('time_net_worth_list', None)
        self.daily_net_worth_list: List[NetWorth] = kwargs.get('daily_net_worth_list', None)
        self.week_net_worth_list: List[NetWorth] = kwargs.get('week_net_worth_list', None)


class NetWorth(object):
    def __init__(self, **kwargs):
        self.open: float = float(kwargs.get('open'))
        self.close: float = float(kwargs.get('close'))
        self.high: float = float(kwargs.get('high'))
        self.low: float = float(kwargs.get('low'))
        self.volume: float = float(kwargs.get('volume'))
        # %Y-%m-%d
        self.date: str = kwargs.get('date')