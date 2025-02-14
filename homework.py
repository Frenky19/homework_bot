import logging
import os
import requests
import time

from dotenv import load_dotenv
from telebot import TeleBot, types

#from constants import RETRY_PERIOD
#from exeptions import NoTokenExeption


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

bot = TeleBot(token=TELEGRAM_TOKEN)


def check_tokens():
    """"""
    required_tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for token in required_tokens:
        if token is None:
            raise Exception(
                f'Отсутствует токен: {token}.'
                'Программа не может продолжать работу.'
            )
    return True


def send_message(bot, message):
    """"""
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message
    )


def get_api_answer(timestamp):
    """"""
    params = {'from_date': timestamp}
    headers = {'Authorization': 'OAuth y0__xCDxc6BAxiRuRgg5P7hoRL7Mcpw71Uojb8HCWn8S6Awt_oZTg'}
    try:
        response = requests.get(ENDPOINT, params=params, headers=headers)
        homework_status = response.json()
        return homework_status
    except requests.exceptions.HTTPError as http_error:
        print(f'Ошибка на стороне клиента или сервера: {http_error}')
    except requests.exceptions.ConnectionError as connection_error:
        print(f'Ошибка соединения: {connection_error}')
    except requests.exceptions.Timeout as timeout_error:
        print(f'Неверная временная метка: {timeout_error}')
    except ValueError as json_error:
        print(f'Ошибка расшифровки JSON объекта: {json_error}')
    return None


def check_response(response):
    """"""
    if not isinstance(response, dict):
        print('Ответ API должен быть словарём.')
        return False
    if 'homeworks' not in response or 'current_date' not in response:
        print('В ответе отсутствуют необходимые ключи.')
        return False
    if not isinstance(response['homeworks'], list):
        print('Значение ключа homeworks должно быть списком.')
        return False
    return True


def parse_status(homework):
    """"""
    if not isinstance(homework, dict):
        print('Некорректный формат данных о домашней работе.')
        return False
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None or homework_status is None:
        print('В данных о домашней работе отсутствует имя или статус.')
        return False
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if verdict is None:
        print(f'Неизвестный статус работы: {homework_status}.')
        return False
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    #...

    # Создаем объект класса бота
    #bot = TeleBot(token=TELEGRAM_TOKEN)
    #timestamp = int(time.time())

    #...

    while True:
        try:
            response = requests.get(PRACTICUM_TOKEN)
            homework_status = response.json()
            if 'homeworks' in homework_status and homework_status['homeworks']:
                for homework in homework_status['homeworks']:
                    status_message = parse_status(homework)
                    if status_message:
                        requests.post(TELEGRAM_TOKEN, data={'chat_id': TELEGRAM_CHAT_ID, 'text': status_message})
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            requests.post(TELEGRAM_TOKEN, data={'chat_id': TELEGRAM_CHAT_ID, 'text': message})
            time.sleep(600)
        #...


if __name__ == '__main__':
    main()
