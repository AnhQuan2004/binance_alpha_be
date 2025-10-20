from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from bson import ObjectId
from typing import List

from database import get_token_collection
from models import TokenCreate, TokenUpdate, TokenResponse
from utils import serialize_token

router = APIRouter()


@router.post("/api/tokens", status_code=201, response_model=TokenResponse)
async def create_token(token: TokenCreate):
    """Create a new token"""
    collection = get_token_collection()
    
    doc = token.dict()
    
    result = await collection.insert_one(doc)
    
    created = await collection.find_one({"_id": result.inserted_id})
    return serialize_token(created)


@router.get("/api/tokens", response_model=List[TokenResponse])
async def get_all_tokens():
    """Get all tokens"""
    collection = get_token_collection()
    
    cursor = collection.find({})
    items = await cursor.to_list(length=1000)
    
    return [serialize_token(item) for item in items]


@router.put("/api/tokens/{id}", response_model=TokenResponse)
async def update_token(id: str, token: TokenUpdate):
    """Update an existing token"""
    collection = get_token_collection()
    
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    existing = await collection.find_one({"_id": object_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Token not found")
    
    update_data = {k: v for k, v in token.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    await collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )
    
    updated = await collection.find_one({"_id": object_id})
    return serialize_token(updated)


@router.delete("/api/tokens/{id}", status_code=204)
async def delete_token(id: str):
    """Delete a token"""
    collection = get_token_collection()
    
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    result = await collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Token not found")
    
    return Response(status_code=204)
