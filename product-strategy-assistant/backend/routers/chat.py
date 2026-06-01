from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic
import json

router = APIRouter()
client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"


class ChatRequest(BaseModel):
    message: str
    analysis_context: dict = {}
    history: list = []


@router.post("/message")
async def chat(req: ChatRequest):
    """Interactive chat with context-aware product strategy assistant."""
    system = """You are a senior Product Strategy Advisor with 20 years of experience.
You have access to the analysis results from a multi-agent system that analyzed the user's business data.
Use this context to answer questions about their products, strategy, market, customers, and roadmap.
Be concise, specific, and actionable. Format your response in clean markdown."""

    context_msg = ""
    if req.analysis_context:
        context_msg = f"\n\n<analysis_context>\n{json.dumps(req.analysis_context, indent=2)[:3000]}\n</analysis_context>\n\n"

    messages = req.history[-10:] + [
        {"role": "user", "content": context_msg + req.message}
    ]

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system=system,
            messages=messages,
        )
        return {"reply": response.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
