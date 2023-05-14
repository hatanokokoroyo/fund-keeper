from abc import abstractmethod, ABCMeta

import pandas


# enum of operation: BUY, SELL, HOLD, NO_ACTION
class FundOperation(object):
    BUY = 0
    SELL = 1
    HOLD = 2
    NO_ACTION = 3


class FundStrategy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_strategy(self, data_frame: pandas.DataFrame, **kwargs) -> FundOperation:
        """
        执行策略, 判断是否需要买入或卖出
        :param data_frame: 包含最新基金净值的data_frame
        :param kwargs: 传入策略所需参数
        :return: FundOperation
        """
        pass
