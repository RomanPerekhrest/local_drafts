from socketserver import TCPServer, StreamRequestHandler
from googletrans import Translator
import socket
import time
import hmac
import os

SECRET_KEY = b'secret_test_key'

def server_authenticate(conn):
    message = os.urandom(32)
    conn.send(message)
    
    hash = hmac.new(SECRET_KEY, message)
    digest = hash.digest()
    response = conn.recv(len(digest))
    return hmac.compare_digest(digest, response)    
    

class MsgHandler(StreamRequestHandler):
    timeout = 5
    rbufsize = 50
    wbufsize = 0
    disable_nagle_algorithm = False
    
    def handle(self):
        if not server_authenticate(self.connection):
            self.wfile.write(b'Error: Authentication failed!')
            self.connection.close()
            return
            
        print('Accepted client connection from', self.client_address)
        translator = Translator()
        
        try:
            for line in self.rfile:
                input_str = line.decode('utf8')
                print('Starting translation process for {} ...'.format(input_str))
                
                # RU-EN translation
                resp = translator.translate(input_str, src='ru').text
                time.sleep(2)
                self.wfile.write(resp.encode())
        except socket.timeout:
            print('socket timed out!')
            
if __name__ == '__main__':
    from threading import Thread
    NWORKERS = 10
    
    serv = TCPServer(('localhost', 20000), MsgHandler)
    serv.allow_reuse_address = True
    
    print('starting threading TCPServer ({} threads)'.format(NWORKERS))
    for n in range(NWORKERS):
        t = Thread(target=serv.serve_forever)
        t.daemon = True
        t.start()
    serv.serve_forever()
    
