from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from datetime import datetime
from bson import ObjectId
from typing import List
import os
import secrets

from database import get_collection
from models import AirdropCreate, AirdropUpdate, AirdropResponse
from utils import serialize_airdrop

router = APIRouter()


def verify_admin():
    """Simple password protection for admin routes - DISABLED FOR TESTING"""
    return "admin_test"


@router.post("/api/airdrops", status_code=201, response_model=AirdropResponse)
async def create_airdrop(
    airdrop: AirdropCreate,
    _: str = Depends(verify_admin)
):
    """Create new airdrop"""
    collection = get_collection()
    
    now = datetime.utcnow()
    doc = airdrop.dict()
    doc.update({
        "created_at": now,
        "updated_at": now,
        "deleted": False
    })
    
    result = await collection.insert_one(doc)
    
    created = await collection.find_one({"_id": result.inserted_id})
    return serialize_airdrop(created)


@router.put("/api/airdrops/{id}", response_model=AirdropResponse)
async def update_airdrop(
    id: str,
    airdrop: AirdropUpdate,
    _: str = Depends(verify_admin)
):
    """Update existing airdrop"""
    collection = get_collection()
    
    # Validate ObjectId
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Check if exists
    existing = await collection.find_one({"_id": object_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Airdrop not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in airdrop.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    await collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )
    
    updated = await collection.find_one({"_id": object_id})
    return serialize_airdrop(updated)


@router.delete("/api/airdrops/{id}", status_code=204)
async def delete_airdrop(
    id: str,
    _: str = Depends(verify_admin)
):
    """Soft delete airdrop"""
    collection = get_collection()
    
    # Validate ObjectId
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Check if exists
    existing = await collection.find_one({"_id": object_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Airdrop not found")
    
    # Soft delete
    await collection.update_one(
        {"_id": object_id},
        {"$set": {"deleted": True, "updated_at": datetime.utcnow()}}
    )
    
    return Response(status_code=204)


@router.get("/api/admin/airdrops", response_model=List[AirdropResponse])
async def get_all_airdrops(_: str = Depends(verify_admin)):
    """Get all airdrops including deleted ones"""
    collection = get_collection()
    
    cursor = collection.find({})
    items = await cursor.to_list(length=1000)
    
    return [serialize_airdrop(item) for item in items]


@router.get("/api/admin/airdrops/deleted", response_model=List[AirdropResponse])
async def get_deleted_airdrops(_: str = Depends(verify_admin)):
    """Get only soft-deleted airdrops"""
    collection = get_collection()
    
    cursor = collection.find({"deleted": True})
    items = await cursor.to_list(length=1000)
    
    return [serialize_airdrop(item) for item in items]
