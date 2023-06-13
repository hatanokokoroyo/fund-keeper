from model import Stock
from utils.json_utils import dumps, loads


def save_to_file(stock: Stock):
    with open('./stock/' + stock.code + '.json', 'w+', encoding='utf8') as f:
        f.write(dumps(stock))


def load_from_file(stock_code: str) -> Stock:
    with open('./stock/' + stock_code + '.json', 'r', encoding='utf8') as f:
        return loads(f.read(), cls=Stock)


def check_file_exists(stock_code: str) -> bool:
    try:
        file_path = './stock/' + stock_code + '.json'
        with open(file_path, 'r', encoding='utf8') as f:
            f.read()
        return True
    except:
        return False
