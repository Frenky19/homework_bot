# Telegram Bot для проверки статуса домашней работы на Яндекс.Практикуме

Этот бот периодически проверяет статус домашней работы на платформе Яндекс.Практикум и отправляет уведомления в Telegram при изменении статуса. В случае ошибок бот также отправляет сообщения с описанием проблемы.

## Технологии

- **Язык:** Python 3.7+
- **Библиотеки:**
  - `requests` — HTTP-запросы к API
  - `pyTelegramBotAPI` — интеграция с Telegram Bot API
  - `python-dotenv` — загрузка переменных окружения
- **Тестирование:**
  - `pytest` — фреймворк для тестов
  - `pytest-timeout` — тесты с таймаутами
- **Линтинг:**
  - `flake8` — проверка стиля кода (PEP8)
  - `flake8-docstrings` — валидация докстрингов
- **Работа с API:**
  - Яндекс.Практикум API (через `ENDPOINT`)
  - Telegram Bot API (через библиотеку)
- **Логирование:** Встроенная библиотека `logging`
- **Конфигурация:**
  - `.env`-файлы для токенов
  - Системные переменные окружения
- **Дополнительно:**
  - Обработка HTTP-статусов (модуль `http`)

## Основные функции

- Автоматическая проверка статуса домашней работы каждые 10 минут
- Отправка уведомлений в Telegram при изменении статуса
- Обработка и логирование ошибок при запросах к API
- Уведомление об ошибках в Telegram при возникновении сбоев

## Установка и настройка

### Предварительные требования

- Python 3.7+
- Учетная запись на Яндекс.Практикуме
- Telegram-бот (для получения `TELEGRAM_TOKEN` и `TELEGRAM_CHAT_ID`)

### Зависимости

```text
requests==2.26.0
python-dotenv==0.20.0
pyTelegramBotAPI==4.14.1
flake8==5.0.4
flake8-docstrings==1.6.0
pytest==7.1.3
pytest-timeout==2.1.0
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка переменных окружения

Создайте файл .env в корне проекта.
Заполните его данными:

```text
PRACTICUM_TOKEN=<ваш_токен_Яндекс.Практикума>
TOKEN=<ваш_Telegram_токен>
CHAT_ID=<ваш_Telegram_ID>
```

Как получить PRACTICUM_TOKEN:

    - Авторизуйтесь на Яндекс.Практикуме.
    - Перейдите в раздел API-доступа в личном кабинете.
    - Сгенерируйте токен.

Как получить Telegram-токен и ID чата:

    - Создайте бота через BotFather для получения TOKEN.
    - Узнайте свой CHAT_ID через бота @userinfobot.

## Запуск бота

```bash
python homework_bot.py
```

Бот начнет проверять статус домашней работы каждые 10 минут. Убедитесь, что файл .env корректно настроен.

### Пример работы

При изменении статуса домашней работы вы получите сообщение вида:
- Изменился статус проверки работы "Имя домашней работы". Работа проверена: ревьюеру всё понравилось. Ура!

В случае ошибок бот отправит уведомление:
- Сбой в работе программы: Ошибка при запросе к API...

### Логирование

Бот ведет логирование в консоль. Пример лога:
- 2023-10-01 12:00:00 - DEBUG - Сообщение успешно отправлено...
- 2023-10-01 12:00:05 - ERROR - Сбой в работе программы...

### Обработка ошибок

- Проверка наличия всех необходимых токенов при старте.

- Повторная отправка сообщений об ошибках при их изменении.

- Обработка сетевых сбоев и ошибок API.

### Тестирование

Для запуска тестов выполните:
```bash
pytest
```
или
```bash
python -m pytest
```

## Автор  
[Андрей Головушкин / Andrey Golovushkin](https://github.com/Frenky19)