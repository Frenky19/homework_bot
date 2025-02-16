from requests.exceptions import RequestException
from telebot.apihelper import ApiException


class NoTokenError(Exception):
    """Отсутствует один или нескольно необходимых токенов."""


class ApiTelebotError(ApiException):
    """Ошибка со стороны телеграма."""


class ApiRequestError(RequestException):
    """Ошибка выполнения HTTP-запроса к API."""
