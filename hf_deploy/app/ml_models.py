import joblib
import os
import pandas as pd
import numpy as np

#global variables for models
kmeans_model = None
clv_model = None
scaler = None

def load_models():
    """Load all trained ML models"""
    global kmeans_model, clv_model, scaler

    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) 
    models_path = os.path.join(project_root, "models")
    
    print(f"Looking for models in: {models_path}")
    
    if not os.path.exists(models_path):
        print(f"Models folder not found at: {models_path}")
        return False

    try:
        #load K-Means model for customer segmentation
        kmeans_path = os.path.join(models_path, "kmeans_model.pkl")
        if os.path.exists(kmeans_path):
            kmeans_model = joblib.load(kmeans_path)
            print("K-Means model loaded")
        else:
            print(f"File not found: {kmeans_path}")
            kmeans_model = None
    except Exception as e:
        print(f"Could not load K-Means model: {e}")
        kmeans_model = None

    try:
        #load CLV prediction model (FIX 2: Changed 'csv' to 'clv')
        clv_path = os.path.join(models_path, "clv_model.pkl")
        if os.path.exists(clv_path):
            clv_model = joblib.load(clv_path)
            print("CLV model loaded")
        else:
            print(f"File not found: {clv_path}")
            clv_model = None
    except Exception as e:
        print(f"Could not load CLV model: {e}")
        clv_model = None

    try:
        #load scaler
        scaler_path = os.path.join(models_path, "scaler.pkl")
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            print("Scaler loaded")
        else:
            print(f"File not found: {scaler_path}")
            scaler = None
    except Exception as e:
        print(f"Could not load scaler: {e}")
        scaler = None

    return kmeans_model is not None or clv_model is not None

def predict_segment(recency, frequency, monetary):
    """Predict customer segment using K-Means model"""
    if kmeans_model is None or scaler is None:
        return {"error": "Models not loaded"}
    
    #create dataframe with correct feature order
    customer_data = pd.DataFrame({
        'Recency': [recency],
        'Frequency': [frequency],
        'Monetary': [monetary]
    })

    #scale the features
    scaled_data = scaler.transform(customer_data)

    #predict cluster
    cluster = kmeans_model.predict(scaled_data)[0]

    #map cluster to segment name
    segment_map = {
        0: "At-Risk Customers",   # 2,396 customers - high recency, low frequency
        1: "VIP Customers",       # 1,024 customers - very high recency (lost customers)
        2: "Loyal Regulars",      # 145 customers - low recency, high frequency (YOUR BEST!)
        3: "New/Occasional"       # 723 customers - medium recency, medium frequency
    }

    return {
        "cluster": int(cluster),
        "segment": segment_map.get(cluster, "Unknown")
    }

def predict_clv(features_dict):
    """
    Predict Customer Lifetime Value
    features_dict should contain all 9 features
    """
    if clv_model is None:
        return {"error": "CLV model not loaded"}
    
    #expected feature order from your notebook
    feature_columns = [
        'frequency', 'recency', 'avg_quantity', 'avg_unit_price',
        'avg_transaction', 'lifespan_days', 'avg_days_between_purchases',
        'purchases_per_month', 'total_quantity'
    ]
    
    #create list of features in correct order
    features = []
    for col in feature_columns:
        features.append(features_dict.get(col, 0))

    #reshape for prediction (1 sample with 9 features)
    features_array = np.array(features).reshape(1, -1)

    #predict
    prediction = clv_model.predict(features_array)[0]

    #determine value category (adjust bins based on model)
    if prediction < 500:
        category = "Low Value"
    elif prediction < 2000:
        category = "Medium Value"
    elif prediction < 5000:
        category = "High Value"
    else:
        category = "VIP"

    return {
        "predicted_clv": round(prediction, 2),
        "value_category": category
    }