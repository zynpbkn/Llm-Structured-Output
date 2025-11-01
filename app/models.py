from typing import Optional, Literal
from pydantic import BaseModel, Field

class Entities(BaseModel):
    amount: Optional[float] = Field(default=None, description="Numeric amount, e.g., 49.99")
    invoice_period: Optional[str] = None
    ticket_id: Optional[str] = None
    device: Optional[str] = None
    address_move: Optional[bool] = None

class TicketExtraction(BaseModel):
    issue_type: Literal["billing","technical","account","general"]
    urgency: Literal["low","medium","high"]
    channel: Literal["phone","email","chat","unknown"]
    entities: Entities
    summary: str
    status_suggestion: Literal["open","in_progress","resolved"]