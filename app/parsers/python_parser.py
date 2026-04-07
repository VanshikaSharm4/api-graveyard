import ast
import os  #lets us navigate through file systems
from typing import List
from app.models import Endpoint #our dataclass from models.py, this is what we'll return

def find_python_files(directory: str) -> List[str]:
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root,file)
                python_files.append(full_path)
    
    return python_files

def extract_endpoints_from_file(filepath: str) -> List[Endpoint]:
    endpoints = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Could not read {filepath}: {e}")
        return []
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"Syntax error in {filepath} : {e}")
        return []
    
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) and \
           not isinstance(node, ast.AsyncFunctionDef):
            continue
        for decorator in node.decorator_list:
            method, path = extract_route_info(decorator)
            
            if method and path:
                has_docs = check_has_docstring(node)
                is_dep = check_is_deprecated(node, decorator)
                
                ep = Endpoint(
                    method=method,
                    path=path,
                    source_file=filepath,
                    line_number=node.lineno,
                    has_docstring=has_docs,
                    is_deprecated=is_dep
                )
                endpoints.append(ep)
    return endpoints

def extract_route_info(decorator) -> tuple:
    try:
        # handles: @app.get("/path") or @router.post("/path")
        if isinstance(decorator, ast.Call):
            func = decorator.func
            
            # get the method name (get, post, put, delete, patch)
            if isinstance(func, ast.Attribute):
                method = func.attr.upper()  # "get" → "GET"
                
                # only care about HTTP methods
                if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    return None, None
                
                # get the path — first argument to the decorator
                if decorator.args:
                    first_arg = decorator.args[0]
                    if isinstance(first_arg, ast.Constant):
                        return method, first_arg.value
                        
    except Exception:
        pass
    
    return None, None

def check_has_docstring(func_node)->bool:
    # a docstring is the first statement in a function body
    # and it must be a string expression
    if func_node.body:
        first_stmt = func_node.body[0]
        if isinstance(first_stmt, ast.Expr):
            if isinstance(first_stmt.value, ast.Constant):
                if isinstance(first_stmt.value.value, str):
                    return True
    return False

def check_is_deprecated(func_node, decorator) -> bool:
    # check for @deprecated decorator
    if isinstance(decorator, ast.Name):
        if decorator.id.lower() == 'deprecated':
            return True
    
    # check for deprecated=True argument in route decorator
    if isinstance(decorator, ast.Call):
        for keyword in decorator.keywords:
            if keyword.arg == 'deprecated':
                if isinstance(keyword.value, ast.Constant):
                    if keyword.value.value == True:
                        return True
    
    # check for #deprecated comment in function name
    if 'deprecated' in func_node.name.lower():
        return True
        
    return False

def scan_codebase(directory: str) -> List[Endpoint]:
    print(f"Scanning directory: {directory}")
    
    all_endpoints = []
    python_files = find_python_files(directory)
    
    print(f"Found {len(python_files)} Python files")
    
    for filepath in python_files:
        endpoints = extract_endpoints_from_file(filepath)
        all_endpoints.extend(endpoints)
        
        if endpoints:
            print(f"  {filepath}: {len(endpoints)} endpoints found")
    
    print(f"Total endpoints discovered: {len(all_endpoints)}")
    return all_endpoints