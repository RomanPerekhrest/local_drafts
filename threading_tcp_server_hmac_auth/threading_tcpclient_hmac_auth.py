from socket import socket, AF_INET, SOCK_STREAM
import sys
import hmac
import os

def client_authenticate(conn, secret_key):
    message = conn.recv(32)
    
    hash = hmac.new(secret_key, message)
    digest = hash.digest()
    conn.send(digest) 


sock = socket(AF_INET, SOCK_STREAM)

try:
    words_to_trans = ' '.join(sys.argv[1:])
    data = bytes(words_to_trans + '\n', 'utf-8')    
    secret_key = bytes(input('enter secret-key:'), 'utf-8')
    
    sock.connect(('localhost', 20000))
    client_authenticate(sock, secret_key)
    sock.sendall(data)
    
    resp = sock.recv(100).decode('utf8')
    if 'Error' in resp:
        print(resp)
    else:
        print('Got translation result for "{before}": {after}'
              .format(before=words_to_trans, after=resp))
        
except Exception as e:
    print(e)
finally:
    sock.close()

