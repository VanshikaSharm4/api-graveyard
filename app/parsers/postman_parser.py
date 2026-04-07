import json
import re
from typing import List, Optional
from app.models import Endpoint

def clean_url_path(raw_url: str) -> str:
    # remove {{variable}} template placeholders
    # e.g. "{{baseUrl}}/api/users" → "/api/users"
    cleaned = re.sub(r'\{\{.*?\}\}', '', raw_url)
    
    # remove protocol and domain
    # e.g. "https://api.example.com/api/users" → "/api/users"
    cleaned = re.sub(r'https?://[^/]+', '', cleaned)
    
    # make sure path starts with /
    if cleaned and not cleaned.startswith('/'):
        cleaned = '/' + cleaned
    
    # remove query strings
    # e.g. "/api/users?page=1" → "/api/users"
    cleaned = cleaned.split('?')[0]
    
    return cleaned.strip() or '/'

def extract_items_recursively(items: list, 
                               collection_name: str) -> List[Endpoint]:
    endpoints = []
    
    for item in items:
        # if this item HAS "item" inside it, it's a FOLDER not an endpoint
        # folders contain more items, so we go deeper (recursion)
        if 'item' in item:
            nested = extract_items_recursively(
                item['item'], 
                collection_name
            )
            endpoints.extend(nested)
            continue
        
        # if we reach here, this item is an actual request (endpoint)
        request = item.get('request', {})
        if not request:
            continue
            
        method = request.get('method', '').upper()
        if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            continue
        
        # url can be a string OR an object with a "raw" field
        url_data = request.get('url', '')
        if isinstance(url_data, dict):
            raw_url = url_data.get('raw', '')
        else:
            raw_url = url_data
        
        path = clean_url_path(raw_url)
        if not path:
            continue
        
        # check if it has documentation
        description = request.get('description', '')
        has_docs = bool(description and description.strip())
        
        ep = Endpoint(
            method=method,
            path=path,
            source_file=f"postman:{collection_name}",
            line_number=0,        # postman has no line numbers
            has_docstring=has_docs,
            has_postman_entry=True  # this came from postman!
        )
        endpoints.append(ep)
    
    return endpoints

def parse_postman_collection(filepath: str) -> List[Endpoint]:
    print(f"Parsing Postman collection: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            collection = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {filepath}: {e}")
        return []
    
    # get collection name for labeling endpoints
    collection_name = collection.get('info', {}).get('name', 'unknown')
    print(f"Collection name: {collection_name}")
    
    # get top level items
    items = collection.get('item', [])
    if not items:
        print("No items found in collection")
        return []
    
    endpoints = extract_items_recursively(items, collection_name)
    print(f"Found {len(endpoints)} endpoints in Postman collection")
    
    return endpoints