import json
from pydantic import BaseModel, Field
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="-"
)


class OrderSearchArgs(BaseModel):
    order_id: str = Field(..., description="Номер заказа клиента")


class RetrieverArgs(BaseModel):
    query: str = Field(..., description="Суть проблемы для поиска по базе знаний")


class PromoGeneratorArgs(BaseModel):
    discount_percent: int = Field(..., description="Размер скидки в процентах")
    phone: str = Field(..., description="Номер телефона клиента")


class EscalateTicketArgs(BaseModel):
    reason: str = Field(..., description="Причина перевода на оператора")
    urgency: int = Field(..., description="Срочность от 1 до 10")


def search_order(order_id: str):
    print(f"Вызван инструмент: Поиск заказа {order_id}")
    return json.dumps({"order_id": order_id, "status": "delivered", "delay_minutes": 60})


def retrieve_rule(query: str):
    print(f"Вызван инструмент: Поиск по базе знаний")
    if "отравлен" in query.lower():
        return "Угроза здоровью. Скидки запрещены. Эскалировать тикет на юристов."
    return "При опоздании курьера выдать промокод ровно на 15 процентов."


def generate_promo(discount_percent: int, phone: str):
    print(f"Вызван инструмент: Генерация промокода {discount_percent}% для {phone}")
    # Реализация политики безопасности
    if discount_percent > 15:
        return json.dumps({"error": "ОТКАЗ: Политика безопасности запрещает скидки более 15%!"})
    return json.dumps({"status": "success", "promo_code": f"SORRY-{discount_percent}"})


def escalate_ticket(reason: str, urgency: int):
    print(f"Вызван инструмент: Эскалация тикета. Срочность {urgency}")
    # Реализация Human-in-the-Loop
    if urgency >= 5:
        return json.dumps({"status": "HITL_TRIGGERED", "message": "Ожидается ручное подтверждение менеджером"})
    return json.dumps({"status": "escalated"})


tools_mapping = {
    "search_order": search_order,
    "retrieve_rule": retrieve_rule,
    "generate_promo": generate_promo,
    "escalate_ticket": escalate_ticket
}

agent_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_order",
            "description": "Ищет информацию о заказе по его номеру",
            "parameters": OrderSearchArgs.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_rule",
            "description": "Ищет регламент компании по описанию проблемы",
            "parameters": RetrieverArgs.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_promo",
            "description": "Генерирует промокод для клиента",
            "parameters": PromoGeneratorArgs.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_ticket",
            "description": "Переводит сложную заявку на живого оператора",
            "parameters": EscalateTicketArgs.model_json_schema()
        }
    }
]


def run_agent(user_review: str):
    print(f"\nНовый отзыв: {user_review}")

    messages = [
        {"role": "system",
         "content": "Ты автономный агент поддержки. Используй доступные инструменты для проверки фактов, поиска правил и помощи клиенту. Если скидка выпущена, напиши извинения."},
        {"role": "user", "content": user_review}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=agent_tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    messages.append(response_message)

    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            function_to_call = tools_mapping[function_name]
            function_response = function_to_call(**function_args)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        print(f"Ответ агента: {final_response.choices[0].message.content}")


if __name__ == "__main__":
    # Сценарий А: Рутинная жалоба
    run_agent("Заказ номер 101 опоздал на час! Мой телефон 89991234567. Что за дела?")

    # Сценарий Б: Критический инцидент
    run_agent("Заказ 102. Я отравился вашим салатом и еду в больницу! Жду ответа от руководства.")