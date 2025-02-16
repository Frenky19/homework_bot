import logging
import os
import time
from http import HTTPStatus

from dotenv import load_dotenv
import requests
from telebot import TeleBot

from exeptions import ApiRequestError, ApiTelebotError, NoTokenError
from variables import unknown_status

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
    required_tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    missing_tokens = []
    for token_name, token_value in required_tokens.items():
        if token_value is None:
            logger.critical(
                f'Отсутствует токен: {token_name}. '
                'Программа не может продолжать работу.'
            )
            missing_tokens.append(token_name)
    if missing_tokens:
        missing_tokens_message = ', '.join(missing_tokens)
        raise NoTokenError(
            f'Отсутствуют необходимые токены: {missing_tokens_message}. '
            'Программа не может продолжать работу.'
        )


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    logger.debug('Попытка отправить сообщение')
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug(f'Сообщение успешно отправлено: {message}.')
        return True
    except (ApiTelebotError, ApiRequestError) as error:
        logger.error(f'Ошибка при отправке сообщения: {error}.')
    return False


def get_api_answer(timestamp):
    """Делает запрос к API и возвращает ответ от сервера в виде словаря."""
    logger.debug('Подготовка к запросу к серверу API')
    prepared_request = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    logger.info(
        'Запрос к API: URL={url}, headers={headers}, '
        'params={params}.'.format(**prepared_request)
    )
    try:
        response = requests.get(**prepared_request)
    except requests.RequestException as error:
        raise ConnectionError(f'Ошибка при запросе к API: {error}.')
    if response.status_code != HTTPStatus.OK:
        raise ApiRequestError(
            f'Ошибка {response.status_code}'
            'при запросе к API: {response.text}'
        )
    try:
        return response.json()
    except ValueError as error:
        raise ValueError(f'Ошибка при расшифровке JSON: {error}.')


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError(
            f'Ответ API должен быть словарём, '
            f'а получен тип: {type(response).__name__}.'
        )
    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError(
            'В ответе API отсутствуют ключи: "homeworks" и "current_date".'
        )
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError(
            f'Ключ "homeworks" в ответе API должен содержать список, '
            f'а получен тип: {type(homeworks).__name__}.'
        )
    return homeworks


def parse_status(homework):
    """Извлекает статус из конкретной домашней работы."""
    if not isinstance(homework, dict):
        raise TypeError('Данные о домашней работе не являются словарём.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None or homework_status is None:
        raise KeyError('Отсутствует название или статус домашней работы.')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if verdict is None:
        logger.info(f'{unknown_status} {homework_status}.')
        raise ValueError(f'{unknown_status} {homework_status}.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    check_tokens()
    timestamp = int(time.time())
    last_error_message = None
    last_homework_message = None
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                if message != last_homework_message:
                    if send_message(bot, message):
                        timestamp = response.get('current_date', timestamp)
                        last_homework_message = message
            else:
                logger.debug('В ответе API нет новых домашних работ.')
        except Exception as error:
            error_message = f'Сбой в работе программы: {error}.'
            logger.error(error_message)
            if error_message != last_error_message:
                if send_message(bot, error_message):
                    last_error_message = error_message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
