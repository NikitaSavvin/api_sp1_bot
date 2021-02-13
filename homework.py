import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_YP = https://praktikum.yandex.ru/api/user_api/homework_statuses/

class HomeworkStatus(Exception):
    pass

def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    try:
        if homework.get('homework_name') != 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except HomeworkStatus:
        return f'Домашнюю работу "{homework_name}" ещё не взяли в работу или не проверили или возникла ошибка при отправке'


def get_homework_statuses(current_timestamp):
    headers = {f'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'frome_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL_YP, params=params, headers=headers)
        return homework_statuses.json()
    except requests.RequestException as error:
        logging.exception("Exception occurred")
        print(f'Ошибка: {error}') 



def send_message(message, bot_client):
    logging.info('Сообщение отправлено в Telegram')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp
    logging.debug('Запуск NextBot')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]), bot_client)
            current_timestamp = new_homework.get('current_date', current_timestamp)  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
