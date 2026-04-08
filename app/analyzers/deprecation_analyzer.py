from typing import List, Dict
from app.models import Endpoint, EndpointStatus
from app.analyzers.dead_detector import normalize_endpoint_key

def analyze_deprecated_endpoints(
    code_endpoints: List[Endpoint],
    traffic: Dict[str, int]
) -> dict:
    
    # normalize traffic the same way as dead detector
    normalized_traffic = {}
    for key, count in traffic.items():
        parts = key.split(' ', 1)
        if len(parts) == 2:
            norm_key = normalize_endpoint_key(parts[0], parts[1])
            normalized_traffic[norm_key] = count
    
    safe_to_delete    = []   # deprecated AND zero traffic
    dangerous_to_delete = [] # deprecated BUT still has traffic
    
    for endpoint in code_endpoints:
        if not endpoint.is_deprecated:
            continue
            
        ep_key = normalize_endpoint_key(endpoint.method, endpoint.path)
        call_count = normalized_traffic.get(ep_key, 0)
        endpoint.call_count = call_count
        endpoint.status = EndpointStatus.DEPRECATED
        
        if call_count == 0:
            safe_to_delete.append(endpoint)
        else:
            dangerous_to_delete.append(endpoint)
    
    return {
        'safe_to_delete':     safe_to_delete,
        'dangerous_to_delete': dangerous_to_delete
    }
    
