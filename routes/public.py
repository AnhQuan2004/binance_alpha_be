from fastapi import APIRouter, Query, Request, Response, HTTPException
from typing import Literal, List
from datetime import datetime
from database import get_collection, get_coin_collection
from models import CoinData, CoinDataResponse
from utils import filter_by_range, serialize_airdrop, generate_etag, serialize_coin

router = APIRouter()


@router.get("/api/airdrops")
async def get_airdrops(
    request: Request,
    response: Response,
    range: Literal["today", "upcoming", "all"] = Query("all")
):
    """
    Public endpoint to get airdrops
    Supports ETag caching and 304 responses
    """
    collection = get_collection()
    
    # Fetch non-deleted airdrops
    cursor = collection.find({"deleted": False})
    items = await cursor.to_list(length=1000)
    
    # Serialize items
    items = [serialize_airdrop(item) for item in items]
    
    # Filter by range
    filtered_items = filter_by_range(items, range)
    
    # Sort by time_iso (newest first)
    try:
        filtered_items.sort(
            key=lambda x: datetime.fromisoformat(x["time_iso"].replace('Z', '+00:00')),
            reverse=True
        )
    except Exception:
        pass
    
    # Generate ETag
    etag = generate_etag(filtered_items)
    
    # Get Last-Modified from latest updated_at
    last_modified = None
    if filtered_items:
        latest = max(filtered_items, key=lambda x: x.get("updated_at", datetime.min))
        last_modified = latest.get("updated_at")
    
    # Check If-None-Match header
    if_none_match = request.headers.get("if-none-match")
    if if_none_match == etag:
        response.status_code = 304
        return Response(status_code=304, headers={
            "ETag": etag,
            "Cache-Control": "public, max-age=5, must-revalidate, stale-while-revalidate=30"
        })
    
    # Set cache headers
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=5, must-revalidate, stale-while-revalidate=30"
    
    if last_modified:
        response.headers["Last-Modified"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    return {
        "items": filtered_items,
        "etag": etag
    }


@router.post("/api/coins", status_code=201)
async def save_coin_data(coin_data: CoinData):
    """Save coin data"""
    collection = get_coin_collection()
    
    doc = coin_data.dict()
    
    await collection.insert_one(doc)
    
    return {"status": "success", "data": doc}


@router.get("/api/coins/{coin_id}", response_model=List[CoinDataResponse])
async def get_coin_data(coin_id: str):
    """Get all data for a specific coin"""
    collection = get_coin_collection()
    
    cursor = collection.find({"coin_id": coin_id})
    items = await cursor.to_list(length=1000)
    
    return [serialize_coin(item) for item in items]
