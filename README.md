# Тг бот black jack


## Содержание

- [Описание](#описание)
- [Установка](#установка)
- [Использование](#использование)

## Описание

Black jack в телеграмме



## Установка
1. Установите python
    
    Python должен быть уже установлен. Если его нет, проследуйте инструкциям [статья по установке python](https://docs.python.org/3/using/windows.html) Python от Microsoft.
    
2. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/eshkere1/black-jack.git
    ```

3. Перейдите в директорию проекта:

    ```bash
    cd путь к проекту
    ```

4. Создайте виртуальное окружение и активируйте его (опционально, но рекомендуется):

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
    ```

5. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

6. Создайте файл .env и добавьте ваш токен Telegram Bot API:
    
    ```
    TELEGRAM_KEY="ваш_токен"
    ```
    Для того чтобы получить телеграмм токен вам нужно обратится к [BotFather](https://telegram.me/BotFather) в телеграмм

7. Запустите бота:

    ```bash
    python black_jack.py
    ```

## Использование

1. Добавьте бота в Telegram.
2. Воспользуйтесь командой /start для запуска.
3. Ответьте да или нет на вопрос "Сыграем в black jack?"
4. Выбирайте брать еще карту или нет