import re

# база знаний
KNOWLEDGE_BASE = [
    "Правило доставки: Если курьер опоздал, принесите извинения и предложите промокод на скидку 15 процентов. Возврат денег запрещен.",
    "Правило качества: Если пицца приехала холодной или коробка помята, предложите бесплатный десерт к следующему заказу.",
    "Правило безопасности: При жалобах на отравление, больницу или здоровье запрещено предлагать скидки. Сообщите, что заявка передана юристам для расследования.",
    "Правило комплектации: Если забыли салфетки, приборы или соус, просто вежливо извинитесь и пообещайте провести беседу со сборщиком заказа."
]


# лексический ретривер
class LexicalRetriever:
    def __init__(self, documents):
        self.documents = documents

    def search(self, query):
        clean_query = set(re.findall(r'\w+', query.lower()))
        best_match = None
        max_overlap = 0
        best_index = -1

        for i, doc in enumerate(self.documents):
            clean_doc = set(re.findall(r'\w+', doc.lower()))
            overlap = len(clean_query.intersection(clean_doc))

            if overlap > max_overlap:
                max_overlap = overlap
                best_match = doc
                best_index = i

        return best_index


# Каждому тестовому отзыву жестко привязан индекс правильного документа
evaluation_dataset = [
    {"query": "Курьер ужасно опоздал, ждали два часа!", "expected_doc_id": 0},
    {"query": "Коробка была помята, а сама пицца холодная.", "expected_doc_id": 1},
    {"query": "У меня сильное отравление после вашего супа, еду в больницу.", "expected_doc_id": 2},
    {"query": "В заказе нет ни салфеток, ни приборов, чем мне есть соус?", "expected_doc_id": 3},
    {"query": "Доставщик задержался в пути на полчаса.", "expected_doc_id": 0}
]


# 2. Вычисление метрик и запуск оценки
def evaluate_retriever():
    retriever = LexicalRetriever(KNOWLEDGE_BASE)
    print("Начинаем оценку ретривера...\n")

    hits = 0
    total = len(evaluation_dataset)

    print(f"{'Запрос':<55} | {'Ожидалось':<10} | {'Найдено':<10} | {'Результат'}")
    print("-" * 100)

    for item in evaluation_dataset:
        query = item["query"]
        expected_id = item["expected_doc_id"]

        # Получаем предсказание ретривера
        found_id = retriever.search(query)

        # Проверяем совпадение
        if found_id == expected_id:
            hits += 1
            status = "Успех"
        else:
            status = "Ошибка"

        found_text = str(found_id) if found_id != -1 else "Нет"
        print(f"{query:<55} | Doc ID: {expected_id:<2} | Doc ID: {found_text:<3} | {status}")

    # Считаем итоговую метрику Hit Rate
    hit_rate = hits / total

    print("-" * 100)
    print(f"\nИтоговая метрика Hit Rate: {hit_rate * 100:.1f} процентов")
    print(f"Успешных поисков: {hits} из {total}")


if __name__ == "__main__":
    evaluate_retriever()