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