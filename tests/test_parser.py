import sys
sys.path.append('.')

from app.parsers.python_parser import scan_codebase

# scan our own project!
endpoints = scan_codebase('./tests/fixtures')

print("\n=== RESULTS ===")
for ep in endpoints:
    print(f"{ep.method} {ep.path} | docs:{ep.has_docstring} | deprecated:{ep.is_deprecated}")
    
from app.parsers.postman_parser import parse_postman_collection

print("\n=== POSTMAN RESULTS ===")
postman_endpoints = parse_postman_collection('./tests/fixtures/sample_collection.json')

for ep in postman_endpoints:
    print(f"{ep.method} {ep.path} | docs:{ep.has_docstring} | source:{ep.source_file}")
    


from app.parsers.log_parser import get_endpoint_traffic, get_error_rates

print("\n=== LOG PARSER RESULTS ===")

traffic = get_endpoint_traffic('./tests/fixtures/sample_access.log')
print("\nTraffic counts:")
for endpoint, count in sorted(traffic.items(), key=lambda x: x[1], reverse=True):
    print(f"  {endpoint}: {count} calls")

error_rates = get_error_rates('./tests/fixtures/sample_access.log')
print("\nError rates:")
for endpoint, stats in error_rates.items():
    print(f"  {endpoint}: {stats['error_rate']}% errors ({stats['total_calls']} total calls)")
    
    
from app.parsers.python_parser import scan_codebase
from app.parsers.postman_parser import parse_postman_collection
from app.parsers.log_parser import get_endpoint_traffic
from app.analyzers.engine import run_full_analysis

print("\n\n=== FULL ANALYSIS ===")

code_eps    = scan_codebase('./tests/fixtures')
postman_eps = parse_postman_collection('./tests/fixtures/sample_collection.json')
traffic     = get_endpoint_traffic('./tests/fixtures/sample_access.log')

results = run_full_analysis(code_eps, postman_eps, traffic)

s = results['summary']
print(f"\nTotal endpoints:      {s['total_endpoints']}")
print(f"Dead endpoints:       {s['dead_count']}")
print(f"Undocumented:         {s['undocumented_count']}")
print(f"Doc coverage:         {s['doc_coverage_percent']}%")
print(f"Dangerous deprecated: {s['deprecated_dangerous']}")
print(f"Breaking changes:     {s['breaking_changes']}")
print(f"Health Score:         {s['health_score']}/100")

print("\nDead endpoints:")
for ep in results['dead']:
    print(f"  🔴 {ep.method} {ep.path} ({ep.call_count} calls)")

print("\nUndocumented endpoints:")
for ep in results['doc_coverage']['undocumented']:
    print(f"  🔵 {ep.method} {ep.path}")