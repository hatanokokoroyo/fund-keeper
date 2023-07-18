import requests

bot_token = '6372981299:AAH4qbevjVJVRpcqIs6J-Mr0I0r7UlWuhEA'
chat_id = '-281666808'


def send_message(text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    proxies = {
        "http": "http://localhost:7890",
        "https": "http://localhost:7890"
    }
    timeout = 10
    try:
        response = requests.post(url, json=data, proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message. Error code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")


def main():
    send_message('hello world')


if __name__ == '__main__':
    main()
