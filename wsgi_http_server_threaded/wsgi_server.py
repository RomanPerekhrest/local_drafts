import sys
import os
from threading import Thread
import time
from base64 import b64encode
from http_codes import *

TPL_DIR = os.path.join(os.path.dirname(__file__), 'templates')
IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'images')


def base_math(environ, start_response):
    start_response(HTTP_200, [('Content-type', 'text/html')])
    
    with open(os.path.join(TPL_DIR, 'base_math.html'), 'rt') as fh:
        tpl = fh.read()        
        num = int(environ['params'].get('number', 0))
        tpl = tpl.format(number=num, half=num/2, square=num**2, cube=num**3)
        
    yield tpl.encode('utf8')

    
def localtime(environ, start_response):

    start_response(HTTP_200, [('Content-type', 'application/xml')])
    
    with open(os.path.join(TPL_DIR, 'localtime.xml'), 'rt') as fh:
        tpl = fh.read()        
        tpl = tpl.format(t=time.localtime())
        
    yield tpl.encode('utf8')


def getimage(environ, start_response): 
    
    with open(os.path.join(IMAGE_DIR, 'nebula.jpg'), 'rb') as img:
        image = img.read()    
    
    start_response(HTTP_200, [('Content-type', 'image/jpeg'),
                              ('Content-length', str(len(image)))])
    yield image


def uppercase_file(environ, start_response):
    start_response(HTTP_200, [('Content-type', 'text/plain')])
    
    file_data = environ['params'].get('file', '').decode('utf8').upper()
    yield file_data.encode('utf8')


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    from wsgi_router import Router
    
    router = Router()
    router.register_handler('get', '/base_math', base_math)
    router.register_handler('get', '/localtime', localtime)
    router.register_handler('get', '/getimage', getimage)
    router.register_handler('post', '/uppercase_file', uppercase_file)
    
    addr, port = 'localhost', 8081
    httpd = make_server(addr, port, router)
    
    process_request = httpd.process_request
    
    # make our wsgi(http) server serve connetions in parallel 
    def handle_in_threads(request, addr):
        t = Thread(target=process_request, args=(request, addr))
        t.daemon = True
        t.start()
    
    httpd.process_request = handle_in_threads
    
    print('starting wsgi (http) server on {}:{} ...'.format(addr, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:        
        print('Shutting down wsgi server ...')
        httpd.shutdown()