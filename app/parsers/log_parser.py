import re
import pandas as pd
from typing import List, Dict
from datetime import datetime


NGINX_LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+)'          # IP address
    r'.+?'                                   # anything in between
    r'\[(?P<timestamp>[^\]]+)\]'             # [timestamp]
    r'\s+"(?P<method>[A-Z]+)'               # "GET
    r'\s+(?P<path>[^\s"]+)'                 # /api/users
    r'\s+HTTP/[\d.]+"'                       # HTTP/1.1"
    r'\s+(?P<status>\d{3})'                 # 200
    r'\s+(?P<size>\d+)'                     # 1234
)

def parse_log_line(line : str) -> dict:
    match = NGINX_LOG_PATTERN.match(line)
    
    if not match:
        return None
    
    path = match.group('path')
    path = path.split('?')[0]
    path = path.rstrip('/')
    if not path:
        path = '/'
    
    return {
        'ip':        match.group('ip'),
        'method':    match.group('method'),
        'path':      path,
        'status':    int(match.group('status')),
        'size':      int(match.group('size')),
        'timestamp': match.group('timestamp')
    }
    
def parse_log_file(filepath: str) -> pd.DataFrame:
    print(f"Parsing log file: {filepath}")
    
    parsed_rows = []
    skipped = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                result = parse_log_line(line)
                if result:
                    parsed_rows.append(result)
                else:
                    skipped += 1
    except FileNotFoundError:
        print(f"Log file not found: {filepath}")
        return pd.DataFrame()
    
    print(f"Parsed {len(parsed_rows)} lines, skipped {skipped} lines")
    
    if not parsed_rows:
        return pd.DataFrame()
    
    return pd.DataFrame(parsed_rows)

def get_endpoint_traffic(filepath: str) -> Dict[str, int]:
    df = parse_log_file(filepath)
    
    # if parsing failed or file was empty
    if df.empty:
        return {}
    
    # create a key combining method + path
    # e.g. "GET /api/users" → we count how many times this appears
    df['endpoint_key'] = df['method'] + ' ' + df['path']
    
    # count occurrences of each unique endpoint_key
    # this is like SQL: SELECT endpoint_key, COUNT(*) GROUP BY endpoint_key
    traffic = df['endpoint_key'].value_counts().to_dict()
    
    # traffic now looks like:
    # {
    #   "GET /api/users": 1523,
    #   "POST /api/auth/login": 892,
    #   "GET /api/v1/old-data": 3
    # }
    
    return traffic

def get_error_rates(filepath: str) -> Dict[str, dict]:
    df = parse_log_file(filepath)
    
    if df.empty:
        return {}
    
    df['endpoint_key'] = df['method'] + ' ' + df['path']
    
    results = {}
    
    for endpoint_key, group in df.groupby('endpoint_key'):
        total = len(group)
        errors = len(group[group['status'] >= 400])
        
        results[endpoint_key] = {
            'total_calls':  total,
            'error_count':  errors,
            'error_rate':   round((errors / total) * 100, 2),
            'status_codes': group['status'].value_counts().to_dict()
        }
    
    return results
