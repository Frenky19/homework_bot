class NoTokenError(Exception):
    """Отсутствует один или нескольно необходимых токенов."""


class ApiTelebotError(Exception):
    """Ошибка со стороны телеграма."""


class ApiRequestError(Exception):
    """Ошибка выполнения HTTP-запроса к API."""
