from fastapi import APIRouter, HTTPException
from app.models import CustomerFeatures, CLVFeatures, SegmentResponse, CLVResponse
from app.ml_models import predict_segment, predict_clv

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("/segment", response_model=SegmentResponse)
def segment_customer(features: CustomerFeatures):
    """Predict customer segment based on RFM features"""
    
    result = predict_segment(
        features.recency,
        features.frequency,
        features.monetary
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "cluster": result["cluster"],
        "segment": result["segment"],
        "recency": features.recency,
        "frequency": features.frequency,
        "monetary": features.monetary
    }

@router.post("/clv", response_model=CLVResponse)
def predict_customer_value(features: CLVFeatures):
    """Predict Customer Lifetime Value"""
    
    # convert features to dictionary
    features_dict = features.dict()
    
    result = predict_clv(features_dict)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.get("/segment/{customer_id}")
def get_customer_segment_from_db(customer_id: int):
    """
    Get pre-computed segment for a customer from database
    This endpoint connects to PostgreSQL to get the segment
    """
    # this will be implemented with database dependency
    # for now, return a placeholder
    return {"customer_id": customer_id, "message": "To be implemented with database"}