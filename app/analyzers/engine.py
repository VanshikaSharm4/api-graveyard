from typing import List, Dict
from app.models import Endpoint
from app.analyzers.dead_detector import detect_dead_endpoints
from app.analyzers.deprecation_analyzer import analyze_deprecated_endpoints
from app.analyzers.doc_coverage import check_doc_coverage
from app.analyzers.breaking_change_differ import find_breaking_changes

def run_full_analysis(
    code_endpoints: List[Endpoint],
    postman_endpoints: List[Endpoint],
    traffic: Dict[str, int],
    previous_endpoints: List[Endpoint] = None
) -> dict:
    
    print("\n🔍 Running full analysis...")
    
    # run all four analyzers
    dead = detect_dead_endpoints(code_endpoints, traffic)
    
    deprecation = analyze_deprecated_endpoints(code_endpoints, traffic)
    
    doc_coverage = check_doc_coverage(code_endpoints, postman_endpoints)
    
    breaking = []
    if previous_endpoints:
        breaking = find_breaking_changes(previous_endpoints, code_endpoints)
    
    # build summary
    total = len(code_endpoints)
    
    summary = {
        'total_endpoints':      total,
        'dead_count':           len(dead),
        'deprecated_safe':      len(deprecation['safe_to_delete']),
        'deprecated_dangerous': len(deprecation['dangerous_to_delete']),
        'undocumented_count':   len(doc_coverage['undocumented']),
        'doc_coverage_percent': doc_coverage['coverage_percent'],
        'breaking_changes':     len(breaking),
        'health_score':         calculate_health_score(total, dead, deprecation, doc_coverage)
    }
    
    return {
        'summary':    summary,
        'dead':       dead,
        'deprecation': deprecation,
        'doc_coverage': doc_coverage,
        'breaking':   breaking
    }
    
def calculate_health_score(total, dead, deprecation, doc_coverage) -> int:
    if total == 0:
        return 100
    
    score = 100
    
    # each dead endpoint loses 3 points
    dead_penalty = (len(dead) / total) * 30
    score -= dead_penalty
    
    # poor doc coverage loses up to 30 points
    doc_penalty = (1 - doc_coverage['coverage_percent'] / 100) * 30
    score -= doc_penalty
    
    # dangerous deprecated endpoints lose 5 points each (max 20)
    deprecated_penalty = min(len(deprecation['dangerous_to_delete']) * 5, 20)
    score -= deprecated_penalty
    
    return max(0, round(score))