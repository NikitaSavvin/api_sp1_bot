import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_YP = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
TEXT_REJECTED = 'К сожалению в работе нашлись ошибки.'
TEXT_REIEWIG = 'Работа взята в ревью'
TEXT_APPROV = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
pages = {
    'rejected': TEXT_REJECTED,
    'reviewing': TEXT_REIEWIG,
    'approved': TEXT_APPROV,
}


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if not homework_name or not status:
        if not homework_name:
            message = 'Не удалось получить имя домашки'
        elif not status:
            message = 'Не удалось получить статус домашки'
        else:
            message = 'Не удалось получить данные по домашке'
        raise Exception(message)
    if status in pages:
        verdict = pages[status]
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            URL_YP, params=params, headers=headers
        )
        return homework_statuses.json()
    except requests.RequestException:
        logging.error("Ошибка get запроса")


def send_message(message, bot_client):
    logging.info('Сообщение отправлено в Telegram')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    logging.debug('Запуск NextBot')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            new_HW = new_homework.get('homeworks')
            if new_HW:
                send_message(parse_homework_status(new_HW[0]), bot_client)
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            send_message(e, bot_client)
            logging.info('Сообщение отправлено')
            time.sleep(5)


if __name__ == '__main__':
    main()
