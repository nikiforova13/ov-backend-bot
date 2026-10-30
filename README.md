# O&V Backend Bot

Telegram-бот, который отправляет пользователям обучающие материалы по backend-разработке
в виде файлов и сохраняет сведения о пользователях, запустивших бота.

## Возможности

- команда `/start` регистрирует или обновляет пользователя в SQLite;
- кнопка «Получить гайд по Python-разработке» отправляет Markdown-файл;
- команда `/python_guide` отправляет тот же гайд;
- повторный запуск обновляет профиль, время последнего запуска и счетчик запусков;
- токен и пути настраиваются через переменные окружения.

## Технологии

- Python 3.11+;
- aiogram 3;
- SQLite и aiosqlite;
- pydantic-settings;
- Pytest и Ruff.

## Структура проекта

```text
ov-backend-bot/
├── documents/
│   └── python-development-guide.md  # Файл, который отправляет бот
├── src/ov_backend_bot/
│   ├── handlers/
│   │   ├── guides.py                # Выдача гайда
│   │   └── start.py                 # Обработка /start
│   ├── config.py                    # Настройки окружения
│   ├── keyboards.py                 # Inline-кнопки
│   ├── main.py                      # Точка входа
│   └── storage.py                   # Работа с SQLite
├── tests/
│   └── test_storage.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Быстрый запуск

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/nikiforova13/ov-backend-bot.git
   cd ov-backend-bot
   ```

2. Создайте и активируйте виртуальное окружение:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Установите проект:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

4. Создайте бота через [@BotFather](https://t.me/BotFather) и скопируйте его токен.

5. Создайте локальный `.env` из примера и укажите токен:

   ```powershell
   Copy-Item .env.example .env
   ```

   ```dotenv
   BOT_TOKEN=ваш_токен
   DATABASE_PATH=data/bot.db
   GUIDE_PATH=documents/python-development-guide.md
   ```

6. Запустите бота:

   ```powershell
   ov-backend-bot
   ```

   Альтернативный запуск:

   ```powershell
   python -m ov_backend_bot.main
   ```

## Хранение пользователей

При команде `/start` бот сохраняет в `data/bot.db`:

- Telegram ID;
- username;
- имя и фамилию;
- код языка;
- наличие Telegram Premium;
- время первого и последнего запуска;
- количество запусков.

Telegram ID служит уникальным ключом, поэтому повторный `/start` не создает дубликат.
Каталог `data/` исключен из Git.

Перед публичным запуском добавьте пользователю уведомление о сборе данных и подготовьте
политику конфиденциальности с учетом требований вашей юрисдикции.

## Проверка проекта

```powershell
ruff check .
pytest
```

## Как добавить новый материал

1. Положите файл в `documents/`.
2. Добавьте кнопку и callback в `keyboards.py`.
3. Добавьте обработчик отправки файла в `handlers/guides.py`.
4. Зарегистрируйте новую команду в `main.py`, если она нужна.

## Безопасность

- не добавляйте `.env` и настоящий токен в Git;
- храните production-токен в секретах платформы развертывания;
- ограничьте доступ к базе пользователей;
- регулярно создавайте резервные копии базы.
