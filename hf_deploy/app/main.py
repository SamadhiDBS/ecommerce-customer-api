from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.ml_models import load_models
from app.routes import customers, predictions
from sqlalchemy import text

# load ML models on startup
models_loaded = load_models()

# create fastapi app
app = FastAPI(
    title="E-Commerce Customer Intelligence API",
    description="""
    This API provides customer insights from your e-commerce data.
    
    ## Features
    * **Customer Segmentation** - Predict customer segments using K-Means
    * **CLV Prediction** - Predict Customer Lifetime Value
    * **Customer Data** - Access customer information from database
    
    ## Models
    * K-Means Clustering (4 segments)
    * Random Forest CLV Predictor (95% accuracy)
    """,
    version="1.0.0",
    contact={
        "name": "Your Name",
        "email": "your.email@example.com",
    },
)

#add CORS middleware (allows frontend apps to call your API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#include routers
app.include_router(customers.router)
app.include_router(predictions.router)

@app.get("/", tags=["Root"])
def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to E-Commerce Customer Intelligence API",
        "docs": "/docs",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Check if API and database are working"""
    db_status = "unknown"
    
    try:
        #test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "models_loaded": {
            "kmeans": models_loaded,
            "clv": models_loaded
        },
        "database": db_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/info", tags=["Info"])
def api_info():
    """Get API information and available endpoints"""
    return {
        "name": "E-Commerce Customer Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Welcome message",
            "GET /health": "Health check",
            "GET /info": "This information",
            "GET /customers": "List all customers",
            "GET /customers/{id}": "Get customer by ID",
            "GET /customers/{id}/transactions": "Get customer transactions",
            "POST /predict/segment": "Predict customer segment from RFM",
            "POST /predict/clv": "Predict Customer Lifetime Value"
        },
        "models": {
            "customer_segmentation": "K-Means (4 clusters)",
            "clv_prediction": "Random Forest (95% accuracy)"
        }
    }

#run with: uvicorn app.main:app --reload