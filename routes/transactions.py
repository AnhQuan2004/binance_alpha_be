from fastapi import APIRouter, HTTPException, Response
from typing import List
from bson import ObjectId

from database import get_collection
from models import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter()

def serialize_transaction(transaction) -> dict:
    if transaction and "_id" in transaction:
        transaction["id"] = str(transaction.pop("_id"))
    
    # Convert datetime to string if present
    if "date" in transaction:
        from datetime import datetime
        if isinstance(transaction["date"], datetime):
            transaction["date"] = transaction["date"].strftime("%Y-%m-%d")
    
    return transaction

@router.get("/api/transactions", response_model=List[TransactionResponse])
async def get_transactions():
    collection = get_collection("transactions")
    cursor = collection.find({})
    items = await cursor.to_list(length=1000)
    return [serialize_transaction(item) for item in items]

@router.post("/api/transactions", status_code=201, response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate):
    # Create the transaction
    transactions_collection = get_collection("transactions")
    doc = transaction.dict()
    result = await transactions_collection.insert_one(doc)
    created = await transactions_collection.find_one({"_id": result.inserted_id})

    # Update the account
    accounts_collection = get_collection("accounts")
    try:
        object_id = ObjectId(transaction.accountId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid account ID format")

    await accounts_collection.update_one(
        {"_id": object_id},
        {"$set": {"balance": transaction.finalBalance, "alphaPoints": transaction.alphaPoints}}
    )

    return serialize_transaction(created)

@router.put("/api/transactions/{id}", response_model=TransactionResponse)
async def update_transaction(id: str, transaction: TransactionUpdate):
    transactions_collection = get_collection("transactions")
    accounts_collection = get_collection("accounts")
    
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Check if transaction exists
    existing = await transactions_collection.find_one({"_id": object_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in transaction.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    await transactions_collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )
    
    # Get updated transaction
    updated = await transactions_collection.find_one({"_id": object_id})
    
    # Update account balance and alpha points if they changed
    if "finalBalance" in update_data or "alphaPoints" in update_data:
        account_id = ObjectId(existing["accountId"])
        account_updates = {}
        if "finalBalance" in update_data:
            account_updates["balance"] = update_data["finalBalance"]
        if "alphaPoints" in update_data:
            account_updates["alphaPoints"] = update_data["alphaPoints"]
        
        if account_updates:
            await accounts_collection.update_one(
                {"_id": account_id},
                {"$set": account_updates}
            )
    
    return serialize_transaction(updated)

@router.delete("/api/transactions/{id}", status_code=204)
async def delete_transaction(id: str):
    collection = get_collection("transactions")
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    result = await collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return Response(status_code=204)
