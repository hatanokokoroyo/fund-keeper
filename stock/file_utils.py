from model import Stock
from utils.json_utils import dumps, loads
import os


def save_to_file(stock: Stock):
    with open('./stock/' + stock.code + '.json', 'w+', encoding='utf8') as f:
        f.write(dumps(stock))


def load_from_file(stock_code: str) -> Stock:
    with open('./stock/' + stock_code + '.json', 'r', encoding='utf8') as f:
        return loads(f.read(), cls=Stock)


def get_local_stock_list():
    dir_path = './stock/'
    file_list = os.listdir(dir_path)
    stock_list = []
    for file_name in file_list:
        stock_list.append(file_name.split('.')[0])
    return stock_list


def check_file_exists(stock_code: str) -> bool:
    try:
        file_path = './stock/' + stock_code + '.json'
        with open(file_path, 'r', encoding='utf8') as f:
            f.read()
        return True
    except:
        return False
