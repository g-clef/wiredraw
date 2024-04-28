from typing import Dict, List, Tuple
from pydantic import BaseModel


class EventSummary(BaseModel):
    source_ip: str
    dest_ip: str
    zeek_id: str
    total_bytes: int  # in bytes + out bytes
    direction: int  # in bytes - out bytes


class EventBucket(BaseModel):
    timestamp: int
    events: List[EventSummary]  # source_ip, dest_ip, zeek_id, num_bytes


class Event(BaseModel):
    zeek_id: str
    log_type: str
    log: Dict[any, any]


class EventDetails(BaseModel):
    zeek_id: str
    events: List[Event]

