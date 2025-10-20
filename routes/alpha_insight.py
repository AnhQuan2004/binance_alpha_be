from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from bson import ObjectId
from typing import List

from database import get_alpha_insight_collection
from models import AlphaInsightCreate, AlphaInsightUpdate, AlphaInsightResponse
from utils import serialize_alpha_insight

router = APIRouter()


@router.post("/api/alpha-insights", status_code=201, response_model=AlphaInsightResponse)
async def create_alpha_insight(insight: AlphaInsightCreate):
    """Create a new alpha insight"""
    collection = get_alpha_insight_collection()
    
    doc = insight.dict()
    
    result = await collection.insert_one(doc)
    
    created = await collection.find_one({"_id": result.inserted_id})
    return serialize_alpha_insight(created)


@router.get("/api/alpha-insights", response_model=List[AlphaInsightResponse])
async def get_all_alpha_insights():
    """Get all alpha insights"""
    collection = get_alpha_insight_collection()
    
    cursor = collection.find({})
    items = await cursor.to_list(length=1000)
    
    return [serialize_alpha_insight(item) for item in items]


@router.put("/api/alpha-insights/{id}", response_model=AlphaInsightResponse)
async def update_alpha_insight(id: str, insight: AlphaInsightUpdate):
    """Update an existing alpha insight"""
    collection = get_alpha_insight_collection()
    
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    existing = await collection.find_one({"_id": object_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Alpha insight not found")
    
    update_data = {k: v for k, v in insight.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    await collection.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )
    
    updated = await collection.find_one({"_id": object_id})
    return serialize_alpha_insight(updated)


@router.delete("/api/alpha-insights/{id}", status_code=204)
async def delete_alpha_insight(id: str):
    """Delete an alpha insight"""
    collection = get_alpha_insight_collection()
    
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    result = await collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alpha insight not found")
    
    return Response(status_code=204)
