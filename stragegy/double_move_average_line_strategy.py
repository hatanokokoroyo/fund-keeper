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

        if yesterday_net_worth <= higher_line < today_net_worth:
            return FundOperation.BUY
        elif yesterday_net_worth >= higher_line > today_net_worth:
            return FundOperation.SELL
        else:
            return FundOperation.NO_ACTION
