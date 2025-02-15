import logging
import os
import requests
import time

from dotenv import load_dotenv
from telebot import TeleBot


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')
RETRY_PERIOD = 600

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


def check_tokens():
    """Проверяет наличие токенов."""
    required_tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for token in required_tokens:
        if token is None:
            logger.critical(
                f'Отсутствует токен: {token}.'
                'Программа не может продолжать работу.'
            )
            raise Exception(
                f'Отсутствует токен: {token}.'
                'Программа не может продолжать работу.'
            )
    return True


def get_api_answer(timestamp):
    """Делает запрос к API и возвращает ответ от сервера в виде словаря."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            logger.error(
                f'Ошибка {response.status_code}'
                'при запросе к API: {response.text}'
            )
            raise requests.HTTPError(
                f'Ошибка {response.status_code}'
                'при запросе к API: {response.text}'
            )
        return response.json()
    except requests.HTTPError as error:
        logger.error(f'Ошибка HTTP при запросе к API: {error}')
        raise RuntimeError(f'Ошибка HTTP при запросе к API: {error}')
    except requests.RequestException as error:
        logger.error(f'Ошибка при запросе к API: {error}')
        raise RuntimeError(f'Ошибка при запросе к API: {error}')
    except ValueError as error:
        logger.error(f'Ошибка при расшифровке JSON: {error}')
        raise ValueError(f'Ошибка при расшифровке JSON: {error}')


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        logger.critical('Ответ API должен быть словарём.')
        raise TypeError('Ответ API должен быть словарём.')
    if 'homeworks' not in response or 'current_date' not in response:
        logger.critical(
            'В ответе API отсутствуют ключи: "homeworks" и "current_date".'
        )
        raise KeyError(
            'В ответе API отсутствуют ключи: "homeworks" и "current_date".'
        )
    if not isinstance(response['homeworks'], list):
        logger.critical(
            'Ключ "homeworks" в ответе API должен содержать список.'
        )
        raise TypeError(
            'Ключ "homeworks" в ответе API должен содержать список.'
        )
    if not response['homeworks']:
        logger.debug('В ответе API нет новых домашних работ.')
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус из конкретной домашней работы."""
    if not isinstance(homework, dict):
        logger.critical('Данные о домашней работе не являются словарём.')
        raise TypeError('Данные о домашней работе не являются словарём.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None or homework_status is None:
        logger.critical('Отсутствует название или статус домашней работы.')
        raise KeyError('Отсутствует название или статус домашней работы.')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if verdict is None:
        logger.error(f'Неизвестный статус домашней работы: {homework_status}.')
        raise ValueError(
            f'Неизвестный статус домашней работы: {homework_status}.'
        )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug(f'Сообщение успешно отправлено: {message}')
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения: {error}')


def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    if not check_tokens():
        logger.critical('Отсутствует один или несколько обязательных токенов.')
        raise SystemExit('Программа завершена из-за отсутствия токенов.')
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)
            timestamp = response.get('current_date', timestamp)
        except Exception as error:
            send_message(bot, f'Сбой в работе программы: {error}')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
