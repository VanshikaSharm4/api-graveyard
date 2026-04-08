from typing import List, Dict
from app.models import Endpoint, EndpointStatus

def normalize_endpoint_key(method: str, path: str) -> str:
    path = path.rstrip('/')
    if not path:
        path = '/'
    return f"{method.lower()} {path.lower()}"

def detect_dead_endpoints(
    code_endpoints: List[Endpoint],
    traffic: Dict[str, int],
    min_calls_threshold: int = 0
) -> List[Endpoint]:
    
    dead_endpoints = []
    
    # normalize traffic keys to match our normalization
    # traffic keys look like "GET /api/users" → normalize to "get /api/users"
    normalized_traffic = {}
    for key, count in traffic.items():
        parts = key.split(' ', 1)    # split "GET /api/users" into ["GET", "/api/users"]
        if len(parts) == 2:
            normalized_key = normalize_endpoint_key(parts[0], parts[1])
            normalized_traffic[normalized_key] = count
    
    for endpoint in code_endpoints:
        ep_key = normalize_endpoint_key(endpoint.method, endpoint.path)
        call_count = normalized_traffic.get(ep_key, 0)
        
        # update the endpoint with actual traffic data
        endpoint.call_count = call_count
        
        if call_count <= min_calls_threshold:
            endpoint.status = EndpointStatus.DEAD
            dead_endpoints.append(endpoint)
    
    return dead_endpoints