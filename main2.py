from fastapi import FastAPI

from web.fund_suggest import *

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# http://localhost:3000/suggest?fund_code=008585&start_date=2023-01-01&end_date=2023-04-16
@app.get("/suggest")
def suggest(fund_code: str, start_date: str, end_date: str):
    error_message, fund_name, fund_daily_net_worth_list = get_fund_detail(fund_code, start_date, end_date)
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


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="localhost", port=7900)
