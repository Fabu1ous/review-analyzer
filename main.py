import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

app = FastAPI(title="Review Analyzer API")

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="КЛЮЧ"
)

KNOWLEDGE_BASE = [
    "Правило доставки: Если курьер опоздал, принесите извинения и предложите промокод на скидку 15 процентов. Возврат денег запрещен.",
    "Правило качества: Если пицца приехала холодной или коробка помята, предложите бесплатный десерт к следующему заказу.",
    "Правило безопасности: При жалобах на отравление, больницу или здоровье запрещено предлагать скидки. Сообщите, что заявка передана юристам для расследования.",
    "Правило комплектации: Если забыли салфетки, приборы или соус, просто вежливо извинитесь и пообещайте провести беседу со сборщиком заказа."
]


class LexicalRetriever:
    def __init__(self, documents):
        self.documents = documents

    def search(self, query):
        clean_query = set(re.findall(r'\w+', query.lower()))

        best_match = ""
        max_overlap = 0

        for doc in self.documents:
            clean_doc = set(re.findall(r'\w+', doc.lower()))
            overlap = len(clean_query.intersection(clean_doc))

            if overlap > max_overlap:
                max_overlap = overlap
                best_match = doc

        if max_overlap > 0:
            return best_match
        else:
            return "Специфических правил не найдено. Действуйте по общим стандартам вежливости."


retriever = LexicalRetriever(KNOWLEDGE_BASE)


class ReviewAnalysisResponse(BaseModel):
    thought_process: str = Field(..., description="Пошаговые рассуждения")
    sentiment: str = Field(..., description="Тональность: positive, negative или mixed")
    urgency: int = Field(..., description="Срочность от 1 до 10")
    issues: list[str] = Field(..., description="Массив проблем")
    suggested_reply: str = Field(..., description="Черновик ответа клиенту")


class ReviewRequest(BaseModel):
    text: str


@app.post("/analyze", response_model=ReviewAnalysisResponse)
async def analyze_review(request: ReviewRequest):
    relevant_rule = retriever.search(request.text)

    system_prompt = f"""
    Ты аналитик отзывов службы поддержки. Оцени отзыв и подготовь ответ.

    Внутреннее правило компании для данной ситуации:
    {relevant_rule}

    Строго используй это правило при формировании ответа клиенту. Сначала напиши свои рассуждения, затем заполни остальные поля.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Отзыв: {request.text}"}
            ],
            temperature=0.2,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "review_analysis_schema",
                    "strict": True,
                    "schema": ReviewAnalysisResponse.model_json_schema()
                }
            }
        )

        raw_json = response.choices[0].message.content
        return ReviewAnalysisResponse.model_validate_json(raw_json)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))