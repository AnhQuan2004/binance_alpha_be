from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from datetime import datetime
from bson import ObjectId
from typing import List, Optional, Dict, Any
import os
import secrets
import re

from database import get_collection
from models import AirdropCreate, AirdropUpdate, AirdropResponse
from utils import serialize_airdrop, compute_time_fields

router = APIRouter()


def verify_admin():
    """Simple password protection for admin routes - DISABLED FOR TESTING"""
    return "admin_test"


def apply_schedule_fields(data: Dict[str, Any], existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Ensure event_date/event_time/timezone fields are normalized and time_iso derived."""
    merged = dict(data)

    def resolved_value(key: str):
        if key in data:
            return data[key]
        if existing:
            return existing.get(key)
        return None

    event_date_value = resolved_value("event_date")
    event_time_value = resolved_value("event_time")
    timezone_value = resolved_value("timezone")

    if event_date_value is None and existing and existing.get("time_iso"):
        try:
            derived_dt = datetime.fromisoformat(existing["time_iso"].replace('Z', '+00:00'))
            event_date_value = derived_dt.date()
            if event_time_value is None:
                event_time_value = derived_dt.time()
        except Exception:
            pass

    if event_date_value is None:
        raise HTTPException(status_code=400, detail="event_date is required")

    try:
        normalized_date, normalized_time, time_iso = compute_time_fields(
            event_date_value,
            event_time_value,
            timezone_value
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    merged["event_date"] = normalized_date
    merged["event_time"] = normalized_time
    merged["time_iso"] = time_iso
    if "timezone" not in merged and (timezone_value is not None or existing):
        merged["timezone"] = timezone_value

    return merged


@router.post("/api/airdrops", status_code=201, response_model=AirdropResponse)
async def create_airdrop(
    airdrop: AirdropCreate,
    _: str = Depends(verify_admin)
):
    """Create or update an airdrop (upsert)"""
    collection = get_collection()
    
    now = datetime.utcnow()
    doc = airdrop.dict()
    doc = apply_schedule_fields(doc)

    project_name = doc.get("project")
    if not project_name:
        raise HTTPException(status_code=400, detail="Project name is required")

    # Case-insensitive search for existing project
    project_name_regex = re.compile(f"^{re.escape(project_name.strip())}$", re.IGNORECASE)
    existing = await collection.find_one({"project": project_name_regex})

    if existing:
        # Update existing document
        update_data = doc
        update_data["updated_at"] = now
        await collection.update_one(
            {"_id": existing["_id"]},
            {"$set": update_data}
        )
        updated_doc = await collection.find_one({"_id": existing["_id"]})
        return serialize_airdrop(updated_doc)
    else:
        # Create new document
        doc.update({
            "created_at": now,
            "updated_at": now,
            "deleted": False
        })
        result = await collection.insert_one(doc)
        created_doc = await collection.find_one({"_id": result.inserted_id})
        return serialize_airdrop(created_doc)


@router.put("/api/airdrops/{id}", response_model=AirdropResponse)
async def update_airdrop(
    id: str,
    airdrop: AirdropCreate,
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
    
    # Use the full airdrop object for the update
    update_data = airdrop.dict(exclude_unset=True)
    update_data = apply_schedule_fields(update_data, existing)
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
    """Permanently delete an airdrop"""
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
    
    result = await collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Airdrop not found")
    
    return Response(status_code=204)


@router.get("/api/admin/airdrops", response_model=List[AirdropResponse])
async def get_all_airdrops(_: str = Depends(verify_admin)):
    """Get all airdrops"""
    collection = get_collection()
    
    cursor = collection.find({})
    items = await cursor.to_list(length=1000)
    
    return [serialize_airdrop(item) for item in items]


@router.get("/api/admin/airdrops/deleted", response_model=List[AirdropResponse])
async def get_deleted_airdrops(_: str = Depends(verify_admin)):
    """Legacy endpoint for soft-deleted airdrops (always empty with hard deletes)"""
    collection = get_collection()
    
    cursor = collection.find({"deleted": True})
    items = await cursor.to_list(length=1000)
    
    return [serialize_airdrop(item) for item in items]
