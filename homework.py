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
TEXT_REIEWIG = ' взята в ревью'
TEXT_APPROV = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
pages = {
    'rejected': TEXT_REJECTED,
    'reviewing': TEXT_REIEWIG,
    'approved': TEXT_APPROV,
}
dictionary = {
    'rejected': 'У вас проверили работу "{name}"!\n\n{verdict}',
    'reviewing': 'Работа "{name}"!\n\n{verdict}',
    'approved': 'У вас проверили работу "{name}"!\n\n{verdict}',
}
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
    try:
        verdict = pages[status]
    except KeyError:
        verdict = None
        logger.error('status=None или status не найден в словаре')
    if status in dictionary:
        message_user = dictionary[status].format(
            name=homework_name, verdict=verdict
        )
    else:
        message_user = (
            'Статус работы "{name}" неизвестен'.format(name=homework_name)
        )
    return message_user


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            URL_YP, params=params, headers=headers
        )
        return homework_statuses.json()
    except requests.RequestException as error:
        logger.exception("Произошло исключение")
        raise error


def send_message(message, bot_client):
    logger.info('Сообщение отправлено в Telegram')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    logger.debug('Запуск NextBot')

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
            send_message(e, bot_client)
            logger.error('Ошибка при получении данных')
            time.sleep(5)


if __name__ == '__main__':
    main()
