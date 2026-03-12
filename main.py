import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

app = FastAPI(
    title="Review Analyzer API",
    description="API для анализа клиентских отзывов и генерации ответов через LLM"
)

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

class ReviewRequest(BaseModel):
    text: str = Field(..., description="Текст отзыва от клиента")
    temperature: float = Field(0.3, ge=0.0, le=2.0, description="Температура генерации")

class ReviewResponse(BaseModel):
    sentiment: str = Field(..., description="Тональность: positive, negative или neutral")
    urgency: int = Field(..., description="Срочность реакции от 1 до 10")
    issues: list[str] = Field(..., description="Список проблем, упомянутых в отзыве")
    suggested_reply: str = Field(..., description="Предлагаемый текст ответа клиенту от лица компании")

@app.post("/analyze", response_model=ReviewResponse)
async def analyze_review(request: ReviewRequest):
    system_prompt = """
    Ты — AI-помощник отдела заботы о клиентах. 
    Твоя задача — проанализировать отзыв и подготовить ответ.
    Ты ДОЛЖЕН вернуть результат ИСКЛЮЧИТЕЛЬНО в формате валидного JSON.
    Структура JSON:
    {
        "sentiment": "negative",
        "urgency": 8,
        "issues":["проблема 1", "проблема 2"],
        "suggested_reply": "Текст вежливого ответа клиенту..."
    }
    """

    try:
        response = await client.chat.completions.create(
            model="qwen/qwen3-235b-a22b-thinking-2507",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Проанализируй этот отзыв: '{request.text}'"}
            ],
            temperature=request.temperature,
            response_format={"type": "json_object"}
        )

        raw_json = response.choices[0].message.content

        result_data = json.loads(raw_json)
        return result_data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка: модель вернула невалидный JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка API: {str(e)}")