from pydantic import BaseModel, Field
from typing import Optional, List

#request models
class CustomerFeatures(BaseModel):
    """Features for customer segmentation"""
    recency: int = Field(..., description="Days since last purchase", ge=0)
    frequency: int = Field(..., description="Number of purchases", ge=1)
    monetary: float = Field(..., description="Total amount spent", ge=0)

class CLVFeatures(BaseModel):
    """Features for CLV prediction"""
    frequency: int = Field(..., ge=1)
    recency: int = Field(..., ge=0)
    avg_quantity: float = Field(..., ge=0)
    avg_unit_price: float = Field(..., ge=0)
    avg_transaction: float = Field(..., ge=0)
    lifespan_days: int = Field(..., ge=0)
    avg_days_between_purchases: float = Field(..., ge=0)
    purchases_per_month: float = Field(..., ge=0)
    total_quantity: int = Field(..., ge=0)

    class Config:
        schema_extra = {
            "example": {
                "frequency": 12,
                "recency": 7,
                "avg_quantity": 3.5,
                "avg_unit_price": 25.0,
                "avg_transaction": 87.5,
                "lifespan_days": 180,
                "avg_days_between_purchases": 15,
                "purchases_per_month": 2,
                "total_quantity": 42
            }
        }

#response models
class SegmentResponse(BaseModel):
    customer_id: Optional[int] = None
    cluster: int
    segment: str
    recency: Optional[int] = None
    frequency: Optional[int] = None
    monetary: Optional[float] = None

class CLVResponse(BaseModel):
    predicted_clv: float
    value_category: str

class CustomerInfo(BaseModel):
    customer_id: int
    segment: str
    value_category: str
    total_orders: Optional[int] = None
    total_revenue: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    models_loaded: dict
    database: str