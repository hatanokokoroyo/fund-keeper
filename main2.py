import datetime

from fastapi import FastAPI

from web.fund_suggest import *

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# http://localhost:3000/suggest?fund_code=008585&start_date=2023-01-01&end_date=2023-04-16
@app.get("/suggest")
def suggest(fund_code: str, start_date: str, end_date: str, today_net_worth: float):
    error_message, fund_name, fund_daily_net_worth_list = get_fund_detail(fund_code, start_date, end_date,
                                                                          today_net_worth)
    if error_message is not None:
        return {
            'error_message': error_message
        }
    fund_ten_days_moving_average_line = calculate_moving_average_line(fund_daily_net_worth_list, 10)
    fund_twenty_days_moving_average_line = calculate_moving_average_line(fund_daily_net_worth_list, 20)

    chart_base64 = draw_chart(fund_name, fund_code, start_date, end_date, fund_daily_net_worth_list,
                              fund_ten_days_moving_average_line, fund_twenty_days_moving_average_line)
    return {
        # 'fund_code': fund_code,
        # 'fund_daily_net_worth': fund_daily_net_worth_list,
        # 'ten_days_avg_net_worth': fund_ten_days_avg_net_worth_list,
        # 'twenty_days_avg_net_worth': fund_twenty_days_avg_net_worth_list,
        # 'suggest_operation': operation,
        # 'suggest_content': suggest_content,
        'chart_base64': chart_base64
    }


@app.get("/get_one_year_net_worth")
def get_one_year_net_worth(fund_code: str, real_time_net_worth: float = None):
    """
    get one year net worth
    :param fund_code: fund code
    :param real_time_net_worth: real_time_net_worth, if not None, use 1 as today's net worth
    :return: base64 string of chart
    """
    latest_day_not_weekend = datetime.datetime.now()
    if latest_day_not_weekend.weekday() == 5:
        latest_day_not_weekend = latest_day_not_weekend - datetime.timedelta(days=1)
    elif latest_day_not_weekend.weekday() == 6:
        latest_day_not_weekend = latest_day_not_weekend - datetime.timedelta(days=2)

    end_date = latest_day_not_weekend.strftime('%Y-%m-%d')
    start_date = (latest_day_not_weekend - datetime.timedelta(days=365)).strftime('%Y-%m-%d')

    if real_time_net_worth is None:
        real_time_net_worth = 1
    return suggest(fund_code, start_date, end_date, real_time_net_worth)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="localhost", port=7900)
