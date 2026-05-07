import requests
import time

# Данные для авторизации
CLIENT_ID = 'RqsY1zyFWCdqUKQ_hlIm'
CLIENT_SECRET = 'nk4hXNSamdMPFq9IhYd3hQkSkYgEQawAFWQxU-j5'


def get_token():
    # ОБЯЗАТЕЛЬНО: полный путь и слеш в конце
    url = "https://api.avito.ru/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    response = requests.post(url, data=data)

    # Проверка на статус 200 перед тем как парсить JSON
    if response.status_code != 200:
        print(f"Ошибка API (Статус {response.status_code}):")
        print(response.text)  # Выведет текст ошибки вместо падения программы
        return None

    return response.json().get('access_token')


def get_my_user_id(token):
    if not token: return None
    url = "https://api.avito.ru/core/v1/accounts/self"
    headers = {'Authorization': f'Bearer {token}'}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("Не удалось получить ID пользователя:", res.text)
        return None

    return res.json().get('id')


def send_message(token, user_id, chat_id, text):
    """Отправка сообщения по API Мессенджера v3"""
    url = f"https://api.avito.ru/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages"
    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        "message": {"text": text},
        "type": "text"
    }
    requests.post(url, headers=headers, json=payload)


def handle_chats():
    # 1. Инициализация: получаем токен и свой ID
    token = get_token()
    if token is None:
        print("Критическая ошибка: Токен не получен. Проверьте CLIENT_ID/SECRET.")
        return
    my_id = get_my_user_id(token)
    if my_id is None:
        print("Критическая ошибка: Не удалось получить User ID.")
        return
    print(f"Бот запущен. Ваш User ID: {my_id}")

    processed_chats = set()
    last_token_time = time.time()

    while True:
        # 2. Обновляем токен раз в 30 минут (на всякий случай)
        if time.time() - last_token_time > 1800:
            token = get_token()
            last_token_time = time.time()
            print("Токен обновлен")

        try:
            # 3. Получаем список чатов (Messenger API v2)
            url = f"https://api.avito.ru/messenger/v2/accounts/{my_id}/chats"
            headers = {'Authorization': f'Bearer {token}'}
            res = requests.get(url, headers=headers)
            res = res.json()
            chats = res.get('chats', [])

            # processed_chats = set()  # Сначала создаем пустое множество
            # try:
            #     init_url = f"https://api.avito.ru/messenger/v2/accounts/{my_id}/chats"
            #     init_response = requests.get(init_url, headers={'Authorization': f'Bearer {token}'})
            #
            #     # Проверяем, что запрос прошел успешно (статус 200)
            #     if init_response.status_code == 200:
            #         init_data = init_response.json()
            #         # Проверяем, что в ответе вообще есть ключ 'chats'
            #         chats_list = init_data.get('chats')
            #         if chats_list:
            #             processed_chats = {c['id'] for c in chats_list if 'id' in c}
            #             print(f"Загружено {len(processed_chats)} существующих чатов. В них бот отвечать не будет.")
            #     else:
            #         print(f"Предупреждение: Не удалось предзагрузить чаты (Статус {init_response.status_code}).")
            #
            # except Exception as e:
            #     print(f"Ошибка при первичной загрузке чатов: {e}. Начинаем с чистого листа.")
            for chat in chats:
                try:
                    chat_id = chat['id']
                    last_msg = chat.get('last_message', {})
                except Exception as e:
                    print(f"Ошибка тут: {e}")

                # Если сообщение от другого пользователя и мы еще не отвечали в этой сессии
                if last_msg.get('author_id') != my_id and chat_id not in processed_chats:
                    print(f"Новое сообщение в чате {chat_id}. Отвечаю...")
                    send_message(token, my_id, chat_id, "Здравствуйте! Благодарю за обращение. 🤝\n "
                                                        "Я работаю 24/7, но в данный момент могу быть за рулем, на выезде или выполнять сложный ремонт. \n"
                                                        "📞 Для оперативной связи — ПОЗВОНИТЕ мне прямо сейчас через кнопку в объявлении. Это самый быстрый способ получить консультацию или вызвать меня на место.\n"
                                                        "Если не дозвонились, оставьте здесь краткое описание проблемы (марка авто и что случилось).\n"
                                                        "Я перезвоню вам сразу, как только освобожусь, или попробуйте набрать меня еще раз через полчаса - час.\n"
                                                        "Всегда на связи и готов помочь! 🛠")
                    processed_chats.add(chat_id)

        except Exception as e:
            print(f"Ошибка: {e}")

        time.sleep(30)  # Проверка каждые 30 секунд


if __name__ == "__main__":
    handle_chats()

# {
#     "access_token": "CxVHBz4fRKWOa0elxPKXfASqe_tvw1ykcDXyGzQ3",
#     "expires_in": 86400,
#     "token_type": "Bearer"
#     Ваш User ID: 395700394
# }