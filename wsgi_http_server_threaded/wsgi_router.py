import cgi
from http_codes import *

def not_found_404(environ, start_response):
    start_response(HTTP_404, [('Content-type', 'text/plain')])
    return [b'Not Found']


class Router:
    
    def __init__(self):
        self.route_map = {}
        
    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD'].lower()
        path = environ['PATH_INFO']
        params = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
        environ['params'] = {key: params.getvalue(key) for key in params}
        handler = self.route_map.get((method, path), not_found_404)
        
        return handler(environ, start_response)
    
    def register_handler(self, method, path, func):
        self.route_map[method.lower(), path] = func
        return func
        
              