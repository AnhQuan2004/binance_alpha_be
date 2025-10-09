from datetime import datetime
import pytz
import hashlib
import json
from typing import List, Dict, Any


def generate_etag(data: Any) -> str:
    """Generate ETag from data"""
    json_str = json.dumps(data, sort_keys=True, default=str)
    return f'W/"{hashlib.md5(json_str.encode()).hexdigest()}"'


def is_today(time_iso: str, timezone: str) -> bool:
    """Check if datetime is today in given timezone"""
    try:
        dt = datetime.fromisoformat(time_iso.replace('Z', '+00:00'))
        tz = pytz.timezone(timezone)
        
        # FOR TESTING: The line below fakes the current date to match sample data.
        # now_tz = tz.localize(datetime(2025, 10, 8, 12, 0, 0))
        # FOR PRODUCTION: Use the real current time.
        now_tz = datetime.now(tz)

        dt_tz = dt.astimezone(tz)
        
        is_same_date = dt_tz.date() == now_tz.date()
        print(f"TODAY CHECK - DB: {dt_tz.date()}, NOW: {now_tz.date()}, Match: {is_same_date}")
        return is_same_date
    except Exception as e:
        print(f"Error in is_today: {str(e)}")
        return False


def is_upcoming(time_iso: str, timezone: str) -> bool:
    """Check if datetime is after today in given timezone"""
    try:
        dt = datetime.fromisoformat(time_iso.replace('Z', '+00:00'))
        tz = pytz.timezone(timezone)

        # FOR TESTING: The line below fakes the current date to match sample data.
        # now_tz = tz.localize(datetime(2025, 10, 8, 12, 0, 0))
        # FOR PRODUCTION: Use the real current time.
        now_tz = datetime.now(tz)

        dt_tz = dt.astimezone(tz)

        is_future_date = dt_tz.date() > now_tz.date()
        print(f"UPCOMING CHECK - DB: {dt_tz.date()}, NOW: {now_tz.date()}, Match: {is_future_date}")
        return is_future_date
    except Exception as e:
        print(f"Error in is_upcoming: {str(e)}")
        return False


def filter_by_range(items: List[Dict], range_type: str) -> List[Dict]:
    """Filter items by range (today/upcoming/all)"""
    print(f"Filtering by range: {range_type}")
    print(f"Total items before filtering: {len(items)}")
    
    if range_type == "all":
        return items
    
    filtered = []
    for item in items:
        time_iso = item.get("time_iso")
        timezone = item.get("timezone")
        project = item.get("project", "unknown")
        
        if not time_iso or not timezone:
            print(f"Skipping item {project} - missing time_iso or timezone")
            continue
        
        print(f"Processing item: {project}, time: {time_iso}, timezone: {timezone}")
            
        if range_type == "today" and is_today(time_iso, timezone):
            print(f"✅ Item {project} is TODAY")
            filtered.append(item)
        elif range_type == "upcoming" and is_upcoming(time_iso, timezone):
            print(f"✅ Item {project} is UPCOMING")
            filtered.append(item)
        else:
            print(f"❌ Item {project} does not match filter {range_type}")
    
    print(f"Total items after filtering: {len(filtered)}")
    return filtered


def serialize_airdrop(doc: Dict) -> Dict:
    """Convert MongoDB document to API response format"""
    doc["id"] = str(doc.pop("_id"))
    if "x" in doc and doc["x"]:
        doc["x"] = str(doc["x"])
    if "source_link" in doc and doc["source_link"]:
        doc["source_link"] = str(doc["source_link"])
    return doc
