import pandas

from stragegy.strategy import FundOperation, FundStrategy
from index.move_average_line_indicator import calculate_move_average_line


class DoubleMoveAverageLineStrategyImpl(FundStrategy):

    def execute_strategy(self, data_frame: pandas.DataFrame, **kwargs) -> FundOperation:
        data_frame = calculate_move_average_line(data_frame, 10)
        data_frame = calculate_move_average_line(data_frame, 20)
        today_10 = data_frame['ma10'].iloc[-1]
        today_20 = data_frame['ma20'].iloc[-1]

        yesterday_net_worth = data_frame['net_worth'].iloc[-2]
        today_net_worth = data_frame['net_worth'].iloc[-1]

        higher_line = max(today_10, today_20)
        lower_line = min(today_10, today_20)

        if self.is_direct_up_cross_double_line(data_frame):
            return FundOperation.BUY
        # 向下穿过单线卖出
        # elif yesterday_net_worth >= higher_line > today_net_worth:
        # 向下穿过双线卖出
        elif yesterday_net_worth >= lower_line > today_net_worth:
            return FundOperation.SELL
        else:
            return FundOperation.NO_ACTION

    @staticmethod
    def is_direct_up_cross_double_line(data_frame: pandas.DataFrame) -> bool:
        data_frame = calculate_move_average_line(data_frame, 10)
        data_frame = calculate_move_average_line(data_frame, 20)
        today_10 = data_frame['ma10'].iloc[-1]
        today_20 = data_frame['ma20'].iloc[-1]

        yesterday_net_worth = data_frame['net_worth'].iloc[-2]
        today_net_worth = data_frame['net_worth'].iloc[-1]

        higher_line = max(today_10, today_20)

        # 如果今日净值没有穿过higher_line, 则返回False
        if today_net_worth <= higher_line:
            return False
        # 如果昨日净值也在higher_line上方, 则返回False
        if yesterday_net_worth > higher_line:
            return False
        # 今日净值已经向上突破higher_line, 但是要求净值上次与双线交叉时, 交叉的是当时较低的那条线
        # 此时昨日净值在higher_line下方, 且昨日净值在两条线之间, 从前天开始, 逐天向前检查, 如果发现净值小于较低的那条线, 则返回True
        # 如果一直没有发现, 则返回False
        index = -3
        while index >= -len(data_frame):
            if data_frame['net_worth'].iloc[index] < min(data_frame['ma10'].iloc[index],
                                                         data_frame['ma20'].iloc[index]):
                return True
            index -= 1
            if index < -len(data_frame):
                return False

    @staticmethod
    def is_direct_down_cross_double_line(data_frame: pandas.DataFrame) -> bool:
        data_frame = calculate_move_average_line(data_frame, 10)
        data_frame = calculate_move_average_line(data_frame, 20)
        today_10 = data_frame['ma10'].iloc[-1]
        today_20 = data_frame['ma20'].iloc[-1]

        yesterday_net_worth = data_frame['net_worth'].iloc[-2]
        today_net_worth = data_frame['net_worth'].iloc[-1]

        lower_line = min(today_10, today_20)

        # 如果今日净值没有穿过lower_line, 则返回False
        if today_net_worth >= lower_line:
            return False
        # 如果昨日净值也在lower_line下方, 则返回False
        if yesterday_net_worth < lower_line:
            return False
        # 今日净值已经向下突破lower_line, 但是要求净值上次与双线交叉时, 交叉的是当时较高的那条线
        # 此时昨日净值在lower_line上方, 且昨日净值在两条线之间, 从前天开始, 逐天向前检查, 如果发现净值大于较高的那条线, 则返回True
        # 如果一直没有发现, 则返回False
        index = -3
        while index >= -len(data_frame):
            if data_frame['net_worth'].iloc[index] > max(data_frame['ma10'].iloc[index],
                                                         data_frame['ma20'].iloc[index]):
                return True
            elif data_frame['net_worth'].iloc[index] < min(data_frame['ma10'].iloc[index],
                                                           data_frame['ma20'].iloc[index]):
                return False
            index -= 1
            if index < -len(data_frame):
                return False
        return False
