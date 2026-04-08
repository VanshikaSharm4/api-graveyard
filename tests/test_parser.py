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