import logging
import os
import requests


def hey_root(message: str):
    """ Alert wrapper for admin alerts """

    logging.error(f"{message}")

    base_endpoint = 'https://api.telegram.org/bot'
    chat_id = -1002114319600
    api_key = os.environ.get('TELEGRAM_API_KEY')

    with open('message.md', 'w', encoding='utf-8') as f:
        f.write(message)

    file_dir = os.path.abspath('message.md')
    url = f'{base_endpoint}{api_key}/sendDocument?chat_id={chat_id}'

    response = requests.post(
        url,
        files={"document": open(file_dir, "rb")},
    )

    print(response.text)

    if response.status_code == 200:
        os.remove('message.md')

    else:
        # fire_alternative_contact_strategy(message)
        pass


if __name__ == "__main__":
    hey_root('This is a test message')
