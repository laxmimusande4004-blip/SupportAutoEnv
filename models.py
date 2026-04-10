from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SupportObservation(BaseModel):
    ticket_text: str = Field(..., description="The text of the customer support ticket.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the ticket.")

class SupportAction(BaseModel):
    classification: Optional[str] = Field(None, description="Category: 'Technical', 'Billing', or 'Account'.")
    order_id: Optional[str] = Field(None, description="Extracted Order ID (e.g., #12345).")
    sentiment: Optional[str] = Field(None, description="Customer sentiment: 'Frustrated' or 'Neutral'.")
    resolution_steps: Optional[List[str]] = Field(None, description="List of proposed resolution steps.")

class SupportReward(BaseModel):
    score: float = Field(..., description="A score between 0.0 and 1.0.")
    feedback: str = Field(..., description="Reasoning for the score.")
    done: bool = Field(default=False, description="Whether the episode is complete.")
