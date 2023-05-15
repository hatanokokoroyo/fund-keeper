import pandas

from stragegy.strategy import FundOperation, FundStrategy
from index.move_average_line_indicator import calculate_move_average_line
from index.bollinger_bands_indicator import calculate_bollinger_bands


class BollingerBandsStrategyImpl(FundStrategy):

    def execute_strategy(self, data_frame: pandas.DataFrame, **kwargs) -> FundOperation:
        data_frame = calculate_bollinger_bands(data_frame, 20, 2)
        data_frame = calculate_move_average_line(data_frame, 10)
        data_frame = calculate_move_average_line(data_frame, 20)

        today_ma_10 = data_frame['ma10'].iloc[-1]
        today_ma_20 = data_frame['ma20'].iloc[-1]

        yesterday_net_worth = data_frame['net_worth'].iloc[-2]
        today_net_worth = data_frame['net_worth'].iloc[-1]

        lower_band = data_frame['lower_band'].iloc[-1]

        buy_price = kwargs.get('hold_price', None)

        # 今日净值向下突破lower_band, 买入
        if yesterday_net_worth >= lower_band > today_net_worth:
            return FundOperation.BUY

        # 如果已经持有仓位, 并且今日净值低于买入价格的95%, 则卖出
        if buy_price is not None and today_net_worth < buy_price * 0.95:
            return FundOperation.SELL

        # # 如果已经持有仓位, 并且今日净值高于买入价格的105%, 则卖出
        # if buy_price is not None and today_net_worth > buy_price * 1.05:
        #     return FundOperation.SELL
        # 如果今日净值向下穿过ma10, 则卖出
        if buy_price is not None and yesterday_net_worth >= today_ma_10 > today_net_worth:
            return FundOperation.SELL
        return FundOperation.NO_ACTION
