from fastapi import APIRouter, HTTPException, Response
from typing import List
from bson import ObjectId

from database import get_collection
from models import AccountCreate, AccountResponse, AccountUpdate

router = APIRouter()

def serialize_account(account) -> dict:
    if account and "_id" in account:
        account["id"] = str(account.pop("_id"))
    return account

@router.get("/api/accounts", response_model=List[AccountResponse])
async def get_accounts():
    collection = get_collection("accounts")
    cursor = collection.find({})
    items = await cursor.to_list(length=1000)
    return [serialize_account(item) for item in items]

@router.post("/api/accounts", status_code=201, response_model=AccountResponse)
async def create_account(account: AccountCreate):
    collection = get_collection("accounts")
    doc = account.dict()
    result = await collection.insert_one(doc)
    created = await collection.find_one({"_id": result.inserted_id})
    return serialize_account(created)

@router.put("/api/accounts/{id}", response_model=AccountResponse)
async def update_account(id: str, account: AccountUpdate):
    collection = get_collection("accounts")
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_data = {k: v for k, v in account.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    await collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )

    updated = await collection.find_one({"_id": object_id})
    if not updated:
        raise HTTPException(status_code=404, detail="Account not found")
        
    return serialize_account(updated)

@router.delete("/api/accounts/{id}", status_code=204)
async def delete_account(id: str):
    collection = get_collection("accounts")
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    result = await collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return Response(status_code=204)
