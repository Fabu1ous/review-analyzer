import requests
import csv

API_URL = "http://127.0.0.1:8000/analyze"

dataset = [
    "Курьер опоздал на час, пицца холодная, а коробка помята. Ужас.",
    "Здравствуйте. После вашего салата 'Цезарь' я попал в больницу с отравлением. Жду связи.",
    "ВЫ ЗАБЫЛИ ПОЛОЖИТЬ БЕСПЛАТНЫЕ САЛФЕТКИ!!! КАК МНЕ ТЕПЕРЬ ЕСТЬ??? ВЕРНИТЕ ДЕНЬГИ НЕМЕДЛЕННО!!!!",
    "Всё было супер! Очень вкусная паста, привезли вовремя. Спасибо!",
    "Еда нормальная, но курьер не мог найти подъезд минут 15. В целом пойдет."
]

results_table = []

print("Начинаем автоматическое тестирование API...\n")

for text in dataset:
    try:
        response = requests.post(API_URL, json={"text": text, "temperature": 0.3})

        if response.status_code == 200:
            result_json = response.json()

            formatted_result = (
                f"Тональность: {result_json.get('sentiment')} | "
                f"Срочность: {result_json.get('urgency')}/10 | "
                f"Проблемы: {', '.join(result_json.get('issues', []))} | "
                f"Ответ ИИ: {result_json.get('suggested_reply')}"
            )

            results_table.append({"запрос": text, "результат": formatted_result})
            print(f"Обработан отзыв: '{text[:30]}...'")
        else:
            results_table.append({"запрос": text, "результат": f"Ошибка API: {response.text}"})
            print(f"Ошибка для отзыва: '{text[:30]}...'")

    except Exception as e:
        results_table.append({"запрос": text, "результат": f"Системная ошибка: {str(e)}"})
        print(f"Ошибка сети при обработке: '{text[:30]}...'")

csv_filename = "evaluation_results.csv"
with open(csv_filename, mode="w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["запрос", "результат"], delimiter=";")
    writer.writeheader()
    for row in results_table:
        writer.writerow(row)

print(f"\nТестирование завершено! Таблица сохранена в файл: {csv_filename}")

print("\n" + "=" * 50)

print("### Таблица результатов автоматического тестирования\n")
print("| Запрос (Входные данные) | Результат (Ответ API) |")
print("|---|---|")
for row in results_table:
    clean_req = row['запрос'].replace('\n', ' ')
    clean_res = row['результат'].replace('\n', '<br>')
    print(f"| {clean_req} | {clean_res} |")