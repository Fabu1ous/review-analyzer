import requests
import json

API_URL = "http://127.0.0.1:8000/analyze"

# Тестовая выборка
test_reviews = [
    "Курьер опоздал на час, пицца холодная, а коробка помята. Ужас.",

    "Здравствуйте. После вашего салата 'Цезарь' я попал в больницу с отравлением. Жду связи.",

    "ВЫ ЗАБЫЛИ ПОЛОЖИТЬ БЕСПЛАТНЫЕ САЛФЕТКИ!!! КАК МНЕ ТЕПЕРЬ ЕСТЬ??? ВЕРНИТЕ ДЕНЬГИ НЕМЕДЛЕННО!!!!"
]

print("Запуск тестирования LLM...\n")

for i, text in enumerate(test_reviews, 1):
    print(f"--- Тест {i} ---")
    print(f"Отзыв: {text}")

    response = requests.post(API_URL, json={"text": text, "temperature": 0.3})

    if response.status_code == 200:
        result = response.json()
        print(f"Тональность: {result['sentiment']}")
        print(f"Срочность: {result['urgency']}/10")
        print(f"Проблемы: {result['issues']}")
        print(f"Ответ ИИ: {result['suggested_reply']}\n")
    else:
        print(f"Ошибка сервера: {response.status_code}")
        # ДОБАВЛЯЕМ ЭТУ СТРОЧКУ, ЧТОБЫ УВИДЕТЬ ПРИЧИНУ:
        print(f"Детали: {response.text}\n")