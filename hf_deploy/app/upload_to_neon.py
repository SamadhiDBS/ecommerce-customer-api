import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://neondb_owner:npg_meVF3arI6qWv@ep-gentle-frog-a170mdjt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print("Connecting to Neon...")
engine = create_engine(DATABASE_URL)

print("Loading CSV files...")

transactions = pd.read_csv('C:/Users/User/Desktop/ecommerce/hf_deploy/data/online_retail_cleaned.csv')
segments = pd.read_csv('C:/Users/User/Desktop/ecommerce/hf_deploy/data/customer_segments.csv')
clv = pd.read_csv('C:/Users/User/Desktop/ecommerce/hf_deploy/data/clv_predictions.csv')
rfm = pd.read_csv('C:/Users/User/Desktop/ecommerce/hf_deploy/data/features_rfm.csv')
daily = pd.read_csv('C:/Users/User/Desktop/ecommerce/hf_deploy/data/features_daily_sales.csv')

print(f"transactions: {len(transactions)} rows")
print(f"segments: {len(segments)} rows")
print(f"clv: {len(clv)} rows")
print(f"rfm: {len(rfm)} rows")
print(f"daily: {len(daily)} rows")

print("Uploading to Neon...")

transactions.to_sql('transactions', engine, if_exists='replace', index=False, chunksize=5000)
segments.to_sql('customer_segments', engine, if_exists='replace', index=False)
clv.to_sql('clv_predictions', engine, if_exists='replace', index=False)
rfm.to_sql('customer_rfm', engine, if_exists='replace', index=False)
daily.to_sql('daily_sales', engine, if_exists='replace', index=False)

print("ALL DATA UPLOADED!")