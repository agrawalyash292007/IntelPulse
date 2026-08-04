from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# Request Schema: Data sent BY the client TO your API
class MarketAnalysisRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, json_schema_extra={"example": "NVDA"})
    timeframe_days: int = Field(default=30, ge=1, le=365, description="Historical range in days")
    include_indicators: bool = Field(default=True)

# Response Schema: Data returned BY your API back TO the client
class MarketAnalysisResponse(BaseModel):
    ticker: str
    status: str
    predicted_trend: str
    confidence_score: float
    key_indicators: Dict[str, Any]
    timeframe_days: int
    sentiment_score: Optional[float] = None