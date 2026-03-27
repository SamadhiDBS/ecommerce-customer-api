from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.database import get_db
from app.models import CustomerInfo

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/", response_model=List[CustomerInfo])
def get_all_customers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get list of all customers with their segments"""
    
    query = text("""
        SELECT 
            t."CustomerID" as customer_id,
            s."Segment" as segment,
            v."value_category" as value_category,
            COUNT(DISTINCT t."InvoiceNo") as total_orders,
            SUM(t."TotalPrice") as total_revenue
        FROM transactions t
        LEFT JOIN customer_segments s ON t."CustomerID" = s."CustomerID"
        LEFT JOIN clv_predictions v ON t."CustomerID" = v."CustomerID"
        GROUP BY t."CustomerID", s."Segment", v."value_category"
        ORDER BY total_revenue DESC
        LIMIT :limit OFFSET :skip
    """)
    
    result = db.execute(query, {"limit": limit, "skip": skip}).fetchall()
    
    customers = []
    for row in result:
        customers.append({
            "customer_id": row[0],
            "segment": row[1] or "Unknown",
            "value_category": row[2] or "Unknown",
            "total_orders": row[3],
            "total_revenue": float(row[4]) if row[4] else 0
        })
    
    return customers

@router.get("/{customer_id}", response_model=CustomerInfo)
def get_customer_by_id(customer_id: int, db: Session = Depends(get_db)):
    """Get customer details by ID"""
    
    query = text("""
        SELECT 
            t."CustomerID" as customer_id,
            s."Segment" as segment,
            v."value_category" as value_category,
            COUNT(DISTINCT t."InvoiceNo") as total_orders,
            SUM(t."TotalPrice") as total_revenue
        FROM transactions t
        LEFT JOIN customer_segments s ON t."CustomerID" = s."CustomerID"
        LEFT JOIN clv_predictions v ON t."CustomerID" = v."CustomerID"
        WHERE t."CustomerID" = :customer_id
        GROUP BY t."CustomerID", s."Segment", v."value_category"
    """)
    
    result = db.execute(query, {"customer_id": customer_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "customer_id": result[0],
        "segment": result[1] or "Unknown",
        "value_category": result[2] or "Unknown",
        "total_orders": result[3],
        "total_revenue": float(result[4]) if result[4] else 0
    }

@router.get("/{customer_id}/transactions")
def get_customer_transactions(
    customer_id: int, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """Get transaction history for a customer"""
    
    query = text("""
        SELECT 
            "InvoiceNo",
            "InvoiceDate",
            "StockCode",
            "Description",
            "Quantity",
            "UnitPrice",
            "TotalPrice"
        FROM transactions
        WHERE "CustomerID" = :customer_id
        ORDER BY "InvoiceDate" DESC
        LIMIT :limit
    """)
    
    result = db.execute(query, {"customer_id": customer_id, "limit": limit}).fetchall()
    
    transactions = []
    for row in result:
        transactions.append({
            "invoice_no": row[0],
            "date": str(row[1]),
            "stock_code": row[2],
            "description": row[3],
            "quantity": row[4],
            "unit_price": float(row[5]),
            "total_price": float(row[6])
        })
    
    return {
        "customer_id": customer_id,
        "transaction_count": len(transactions),
        "transactions": transactions
    }
