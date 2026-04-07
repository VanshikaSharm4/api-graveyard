import sys
sys.path.append('.')

from app.parsers.python_parser import scan_codebase

# scan our own project!
endpoints = scan_codebase('./tests/fixtures')

print("\n=== RESULTS ===")
for ep in endpoints:
    print(f"{ep.method} {ep.path} | docs:{ep.has_docstring} | deprecated:{ep.is_deprecated}")