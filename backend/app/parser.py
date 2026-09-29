import json
from typing import List, Optional, Any, Dict
from .models import Endpoint

def parse_postman_collection(file_path: str) -> List[Endpoint]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    endpoints = []
    
    def extract_items(items):
        for item in items:
            if 'item' in item:
                extract_items(item['item'])
            elif 'request' in item:
                req = item['request']
                method = req.get('method', 'GET')
                
                url_obj = req.get('url', {})
                if isinstance(url_obj, str):
                    url = url_obj
                    query = []
                else:
                    url = url_obj.get('raw', '')
                    if not url:
                        host = ".".join(url_obj.get('host', []))
                        path = "/".join(url_obj.get('path', []))
                        url = f"http://{host}/{path}"
                    query_list = url_obj.get('query', [])
                    query = [q.get('key') for q in query_list if q.get('key')]
                
                # Check auth
                auth = req.get('auth', {})
                auth_required = bool(auth)
                
                headers = {h.get('key'): h.get('value') for h in req.get('header', []) if h.get('key')}
                if not auth_required and headers.get('Authorization'):
                    auth_required = True
                
                body = req.get('body', {}).get('raw')
                if body:
                    try:
                        body = json.loads(body)
                    except:
                        pass

                endpoints.append(Endpoint(
                    method=method,
                    url=url,
                    query_params=query,
                    headers=headers,
                    body=body,
                    auth_required=auth_required
                ))
    
    if 'item' in data:
        extract_items(data['item'])
        
    return endpoints
