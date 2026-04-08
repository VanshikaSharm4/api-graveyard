from typing import List
from app.models import Endpoint, EndpointStatus

def check_doc_coverage(
    code_endpoints: List[Endpoint],
    postman_endpoints: List[Endpoint]
) -> dict:
    
    # build a set of paths that exist in postman
    # if an endpoint is in postman, it has SOME documentation
    postman_paths = set()
    for ep in postman_endpoints:
        from app.analyzers.dead_detector import normalize_endpoint_key
        key = normalize_endpoint_key(ep.method, ep.path)
        postman_paths.add(key)
    
    documented   = []
    undocumented = []
    
    for endpoint in code_endpoints:
        from app.analyzers.dead_detector import normalize_endpoint_key
        ep_key = normalize_endpoint_key(endpoint.method, endpoint.path)
        
        # an endpoint is documented if it has ANY of these:
        # 1. a docstring in the code
        # 2. an openapi annotation
        # 3. an entry in the postman collection
        is_documented = (
            endpoint.has_docstring or
            endpoint.has_openapi_annotation or
            ep_key in postman_paths
        )
        
        if is_documented:
            documented.append(endpoint)
        else:
            endpoint.status = EndpointStatus.UNDOCUMENTED
            undocumented.append(endpoint)
    
    total = len(code_endpoints)
    coverage_percent = (len(documented) / total * 100) if total > 0 else 0
    
    return {
        'documented':        documented,
        'undocumented':      undocumented,
        'total':             total,
        'coverage_percent':  round(coverage_percent, 2)
    }