import os
import re
from typing import Any

from dotenv import load_dotenv
load_dotenv()  # ensure GOOGLE_API_KEY is present before LLM init

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from app.models import TicketExtraction

SYSTEM = (
    "You are a strict information extractor. "
    "Return JSON with EXACTLY these keys: "
    "issue_type, urgency, channel, entities, summary, status_suggestion. "
    "Allowed enums: "
    "issue_type: {{billing, technical, account, general}}; "
    "urgency: {{low, medium, high}}; "
    "channel: {{phone, email, chat, unknown}}; "
    "status_suggestion: {{open, in_progress, resolved}}. "
    "entities must contain: amount (number|null), invoice_period (string|null), "
    "ticket_id (string|null), device (string|null), address_move (boolean|null). "
    "If something is unknown, use null for nested fields or pick the closest enum at the top level. "
    "Do NOT add extra fields. Return JSON only."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "Ticket text:\n{ticket_text}\n\nReturn JSON only.")
])

# Don't hardcode the key; rely on env (GOOGLE_API_KEY) which is already loaded above.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Enforce Pydantic-validated structured output
chain: Runnable = prompt | llm.with_structured_output(TicketExtraction)

def _normalize_amount_like(value: Any):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        m = re.search(r"[-+]?\d+(?:\.\d+)?", value.replace(",", ""))
        return float(m.group(0)) if m else None
    return None

def extract_ticket(ticket_text: str) -> TicketExtraction:
    result: TicketExtraction = chain.invoke({"ticket_text": ticket_text})
    result.entities.amount = _normalize_amount_like(result.entities.amount)
    return result