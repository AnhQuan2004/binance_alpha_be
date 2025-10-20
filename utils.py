from datetime import datetime, date, time as dt_time
import pytz
import hashlib
import json
from typing import List, Dict, Any, Tuple, Optional
from pytz.tzinfo import BaseTzInfo


def _ensure_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return date.fromisoformat(value.strip())
    raise ValueError("Invalid date value")


def _ensure_time(value: Any) -> Optional[dt_time]:
    if value is None:
        return None
    if isinstance(value, dt_time):
        return value.replace(microsecond=0)
    if isinstance(value, datetime):
        return value.time().replace(microsecond=0)
    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            return None
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(candidate, fmt).time()
            except ValueError:
                continue
        raise ValueError("Invalid time format, expected HH:MM or HH:MM:SS")
    raise ValueError("Invalid time value")


def compute_time_fields(event_date: Any, event_time: Any, timezone: Optional[str]) -> Tuple[str, Optional[str], str]:
    """Normalize date/time inputs and produce ISO strings (with timezone applied)."""
    date_obj = _ensure_date(event_date)
    time_obj = _ensure_time(event_time)
    time_for_dt = time_obj or dt_time(0, 0)

    tz_name = timezone or "UTC"
    tz = pytz.timezone(tz_name)

    dt_local = tz.localize(datetime.combine(date_obj, time_for_dt))
    return (
        date_obj.isoformat(),
        time_obj.isoformat() if time_obj else None,
        dt_local.isoformat()
    )


def _coerce_datetime(time_iso: Optional[str], event_date: Any, event_time: Any, timezone: Optional[str]) -> Tuple[datetime, BaseTzInfo]:
    """Resolve the stored schedule fields to a timezone-aware datetime for filtering."""
    tz_name = timezone or "UTC"
    tz = pytz.timezone(tz_name)

    if event_date is not None:
        try:
            date_obj = _ensure_date(event_date)
            time_obj = _ensure_time(event_time) or dt_time(0, 0)
            dt_local = tz.localize(datetime.combine(date_obj, time_obj))
            return dt_local, tz
        except Exception:
            pass

    if time_iso:
        dt = datetime.fromisoformat(time_iso.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        else:
            dt = dt.astimezone(tz)
        return dt, tz

    raise ValueError("Missing event schedule information")


def generate_etag(data: Any) -> str:
    """Generate ETag from data"""
    json_str = json.dumps(data, sort_keys=True, default=str)
    return f'W/"{hashlib.md5(json_str.encode()).hexdigest()}"'


def is_today(time_iso: Optional[str], event_date: Any, event_time: Any, timezone: Optional[str]) -> bool:
    """Check if datetime is today in given timezone"""
    try:
        dt, tz = _coerce_datetime(time_iso, event_date, event_time, timezone)

        # FOR TESTING: The line below fakes the current date to match sample data.
        # now_tz = tz.localize(datetime(2025, 10, 8, 12, 0, 0))
        # FOR PRODUCTION: Use the real current time.
        now_tz = datetime.now(tz)

        is_same_date = dt.date() == now_tz.date()
        print(f"TODAY CHECK - DB: {dt.date()}, NOW: {now_tz.date()}, Match: {is_same_date}")
        return is_same_date
    except Exception as e:
        print(f"Error in is_today: {str(e)}")
        return False


def is_upcoming(time_iso: Optional[str], event_date: Any, event_time: Any, timezone: Optional[str]) -> bool:
    """Check if datetime is after today in given timezone"""
    try:
        dt, tz = _coerce_datetime(time_iso, event_date, event_time, timezone)
        # FOR TESTING: The line below fakes the current date to match sample data.
        # now_tz = tz.localize(datetime(2025, 10, 8, 12, 0, 0))
        # FOR PRODUCTION: Use the real current time.
        now_tz = datetime.now(tz)

        is_future_date = dt.date() > now_tz.date()
        print(f"UPCOMING CHECK - DB: {dt.date()}, NOW: {now_tz.date()}, Match: {is_future_date}")
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
        event_date = item.get("event_date")
        event_time = item.get("event_time")
        timezone = item.get("timezone")
        project = item.get("project", "unknown")
        
        if not event_date and not time_iso:
            print(f"Skipping item {project} - missing event_date/time_iso")
            continue
        
        tz_dbg = timezone or "UTC"
        debug_time = event_time or "00:00:00"
        print(f"Processing item: {project}, date: {event_date}, time: {debug_time}, iso: {time_iso}, timezone: {tz_dbg}")
            
        if range_type == "today" and is_today(time_iso, event_date, event_time, timezone):
            print(f"✅ Item {project} is TODAY")
            filtered.append(item)
        elif range_type == "upcoming" and is_upcoming(time_iso, event_date, event_time, timezone):
            print(f"✅ Item {project} is UPCOMING")
            filtered.append(item)
        else:
            print(f"❌ Item {project} does not match filter {range_type}")
    
    print(f"Total items after filtering: {len(filtered)}")
    return filtered


def serialize_airdrop(doc: Dict) -> Dict:
    """Convert MongoDB document to API response format"""
    doc["id"] = str(doc.pop("_id"))
    if "event_date" in doc and doc["event_date"]:
        value = doc["event_date"]
        if isinstance(value, (datetime, date)):
            doc["event_date"] = value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
        else:
            doc["event_date"] = str(value)
    elif doc.get("time_iso"):
        try:
            doc["event_date"] = datetime.fromisoformat(doc["time_iso"].replace('Z', '+00:00')).date().isoformat()
        except Exception:
            doc["event_date"] = None

    if "event_time" in doc:
        value = doc["event_time"]
        if isinstance(value, (datetime, dt_time)):
            doc["event_time"] = value.time().isoformat() if isinstance(value, datetime) else value.isoformat()
        elif value is not None:
            doc["event_time"] = str(value)
    elif doc.get("time_iso"):
        try:
            doc["event_time"] = datetime.fromisoformat(doc["time_iso"].replace('Z', '+00:00')).time().isoformat()
        except Exception:
            doc["event_time"] = None

    if "x" in doc and doc["x"]:
        doc["x"] = str(doc["x"])
    if "source_link" in doc and doc["source_link"]:
        doc["source_link"] = str(doc["source_link"])
    if "raised" in doc and doc["raised"] is not None:
        doc["raised"] = str(doc["raised"])
    return doc


def serialize_coin(doc: Dict) -> Dict:
    """Convert coin document to API response format"""
    doc["id"] = str(doc.pop("_id"))
    return doc


def serialize_token(doc: Dict) -> Dict:
    """Convert token document to API response format"""
    doc["id"] = str(doc.pop("_id"))
    return doc


def serialize_alpha_insight(doc: Dict) -> Dict:
    """Convert alpha insight document to API response format"""
    doc["id"] = str(doc.pop("_id"))
    return doc
