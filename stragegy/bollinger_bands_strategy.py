import pandas

from stragegy.strategy import FundOperation, FundStrategy
from index.move_average_line_indicator import calculate_move_average_line
from index.bollinger_bands_indicator import calculate_bollinger_bands
from stragegy.double_move_average_line_strategy import DoubleMoveAverageLineStrategyImpl


class BollingerBandsStrategyImpl(FundStrategy):

    def execute_strategy(self, data_frame: pandas.DataFrame, **kwargs) -> FundOperation:
        bollinger_bands_time_window = kwargs.get('bollinger_bands_time_window')
        bollinger_bands_standard_deviation = kwargs.get('bollinger_bands_standard_deviation')

        # data_frame = calculate_bollinger_bands(data_frame, 20, 2)
        data_frame = calculate_bollinger_bands(data_frame, bollinger_bands_time_window,
                                               bollinger_bands_standard_deviation)
        data_frame = calculate_move_average_line(data_frame, 10)
        data_frame = calculate_move_average_line(data_frame, 20)

        today_ma_10 = data_frame['ma10'].iloc[-1]
        today_ma_20 = data_frame['ma20'].iloc[-1]
        upper_ma = max(today_ma_10, today_ma_20)
        lower_ma = min(today_ma_10, today_ma_20)

        yesterday_net_worth = data_frame['net_worth'].iloc[-2]
        today_net_worth = data_frame['net_worth'].iloc[-1]

        lower_band = data_frame['lower_band'].iloc[-1]
        upper_band = data_frame['upper_band'].iloc[-1]

        hold_price = kwargs.get('hold_price', None)

        # 策略一 0.0072
        # # 今日净值向下突破lower_band, 买入
        # if yesterday_net_worth >= lower_band > today_net_worth:
        #     return FundOperation.BUY
        # # 如果今日净值向下穿过ma10, 则卖出
        # if hold_price is not None and yesterday_net_worth >= today_ma_10 > today_net_worth:
        #     return FundOperation.SELL
        # return FundOperation.NO_ACTION

        # 策略二 0.03079
        # 今日净值低于下轨线, 买入
        # if yesterday_net_worth >= lower_band > today_net_worth:
        #     return FundOperation.BUY
        # # 如果今日净值向下穿过双移动平均线, 则卖出
        # if hold_price is not None and DoubleMoveAverageLineStrategyImpl.is_direct_down_cross_double_line(data_frame):
        #     # 如果今日净值大于持有价格, 则卖出
        #     if today_net_worth > hold_price:
        #         return FundOperation.SELL
        # return FundOperation.NO_ACTION

        # 策略三 0.0375
        # # 今日净值低于下轨线, 买入
        # if lower_band > today_net_worth:
        #     return FundOperation.BUY
        # # 如果今日净值向下穿过双移动平均线, 则卖出
        # if hold_price is not None and DoubleMoveAverageLineStrategyImpl.is_direct_down_cross_double_line(data_frame):
        #     # 如果今日净值大于持有价格, 则卖出
        #     if today_net_worth > hold_price:
        #         return FundOperation.SELL
        # return FundOperation.NO_ACTION

        # 策略四
        # 30, 2.5, 一年  0.06335, 三年平均 0.02516
        # 30, 2, 一年 0.05532, 三年平均 0.02633
        # 20, 2, 一年 0.05266, 三年平均 0.02469
        # 今日净值低于下轨线, 买入
        if lower_band > today_net_worth:
            return FundOperation.BUY
        # # 如果今日净值低于持仓价格0.95, 则卖出
        # if hold_price is not None and today_net_worth < hold_price * 0.95:
        #     return FundOperation.SELL
        # 如果今日净值向下穿过双移动平均线, 且今日净值大于持仓价格, 则卖出
        if hold_price is not None and DoubleMoveAverageLineStrategyImpl.is_direct_down_cross_double_line(data_frame):
            if today_net_worth > hold_price:
                return FundOperation.SELL
        return FundOperation.NO_ACTION
