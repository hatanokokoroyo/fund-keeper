import requests
from api.trend.doctor_xiong_model import *
from utils.json_utils import *

api_domain = 'https://api.doctorxiong.club/v1'


# return FundDetail or None
def get_fund_detail(fund_code: str, start_date: str, end_date: str):
    """
    get fund details
    :param fund_code: fund code
    :param start_date: yyyy-MM-dd
    :param end_date: yyyy-MM-dd
    :return: FundDetail or None
    """
    url = api_domain + '/fund/detail/list'
    params = {
        'code': fund_code,
        'startDate': start_date,
        'endDate': end_date
    }
    headers = {
        "token": ""
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.exceptions.Timeout:
        return None
    if response.status_code != 200:
        return None
    print(response.text)
    api_response = loads(response.text, formatter=format_camel_to_snake, cls=DoctorXiongApiResponse)
    if api_response.code[0] != 200:
        return api_response.message
    return api_response.get_fund_detail()


# def get_today_net_worth(fund_code) -> float:
