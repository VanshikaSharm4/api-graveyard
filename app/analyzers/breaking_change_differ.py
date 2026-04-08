from typing import List, Dict
from app.models import Endpoint, EndpointStatus
from app.analyzers.dead_detector import normalize_endpoint_key

def find_breaking_changes(
    old_endpoints: List[Endpoint],
    new_endpoints: List[Endpoint]
) -> List[dict]:
    
    breaking_changes = []
    
    # build lookup dictionaries keyed by normalized endpoint key
    old_map = {
        normalize_endpoint_key(ep.method, ep.path): ep
        for ep in old_endpoints
    }
    new_map = {
        normalize_endpoint_key(ep.method, ep.path): ep
        for ep in new_endpoints
    }
    
    old_keys = set(old_map.keys())
    new_keys = set(new_map.keys())
    
    # endpoints that existed before but are GONE now
    removed = old_keys - new_keys
    for key in removed:
        ep = old_map[key]
        breaking_changes.append({
            'type':     'ENDPOINT_REMOVED',
            'severity': 'HIGH',
            'endpoint': key,
            'message':  f"{ep.method} {ep.path} was removed — existing clients will get 404"
        })
    
    # endpoints that are NEW — not breaking but worth knowing
    added = new_keys - old_keys
    for key in added:
        ep = new_map[key]
        breaking_changes.append({
            'type':     'ENDPOINT_ADDED',
            'severity': 'INFO',
            'endpoint': key,
            'message':  f"{ep.method} {ep.path} is a new endpoint"
        })
    
    return breaking_changes

