import json
from pydantic import BaseModel, Field
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="ВАШ_КЛЮЧ"
)

agent_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_order",
            "description": "Ищет информацию о заказе по его номеру",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_rule",
            "description": "Ищет регламент компании по описанию проблемы",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_promo",
            "description": "Генерирует промокод для клиента",
            "parameters": {
                "type": "object",
                "properties": {
                    "discount_percent": {"type": "integer"},
                    "phone": {"type": "string"}
                },
                "required": ["discount_percent", "phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_ticket",
            "description": "Переводит заявку на живого оператора",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                    "urgency": {"type": "integer"}
                },
                "required": ["reason", "urgency"]
            }
        }
    }
]

evaluation_dataset = [
    {
        "name": "Стандартное опоздание",
        "review": "Заказ 101 опоздал на час! Мой телефон 89991234567.",
        "expected_tools": ["search_order", "retrieve_rule", "generate_promo"]
    },
    {
        "name": "Критический инцидент",
        "review": "Я отравился салатом из заказа 102 и еду в больницу!",
        "expected_tools": ["retrieve_rule", "escalate_ticket"]
    },
    {
        "name": "Неполные данные без телефона",
        "review": "Заказ 103 опоздал на два часа, жду компенсацию.",
        "expected_tools": ["search_order"]
    }
]


def evaluate_agent():
    print("Начинаем автоматическую оценку агента...\n")

    successful_tests = 0
    total_tests = len(evaluation_dataset)

    for item in evaluation_dataset:
        print(f"Тест: {item['name']}")
        print(f"Ожидаемые инструменты: {', '.join(item['expected_tools'])}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Ты автономный агент поддержки. Вызови нужные инструменты для решения проблемы."},
                {"role": "user", "content": item["review"]}
            ],
            tools=agent_tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        actual_tools = []
        if response_message.tool_calls:
            actual_tools = [call.function.name for call in response_message.tool_calls]

        print(f"Фактические инструменты: {', '.join(actual_tools)}")

        if set(actual_tools) == set(item['expected_tools']):
            print("Результат: Успех\n")
            successful_tests += 1
        else:
            print("Результат: Ошибка. Инструменты не совпадают.\n")

    accuracy = (successful_tests / total_tests) * 100
    print(f"Итоговая точность выбора инструментов: {accuracy:.1f} процентов.")


if __name__ == "__main__":
    evaluate_agent()