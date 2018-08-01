#!/usr/bin/env python3

import asyncio
import websockets
import json
import logging
import signal
from googletrans import Translator

logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())

connected = set()
translator = Translator()

def prepare_response(websocket, msg):
    client_info = '({}:{})'.format(*websocket.remote_address)
    
    # translation process
    src_lang = translator.detect(msg).lang
    dest_lang = 'en' if src_lang != 'en' else 'ru'
    translated = translator.translate(msg, dest=dest_lang).text
    
    return json.dumps({'client_info': client_info, 
                       'original': msg, 'translated': translated})

async def process(websocket, path):
    connected.add(websocket)
    
    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            if 'message' in data:
                response = prepare_response(websocket, data['message'])
                await asyncio.wait([client.send(response) for client in connected])
            else:
                logging.error('Client {}:{}, "message" key missing!'
                              .format(*websocket.remote_address), data)
        except websockets.exceptions.ConnectionClosed:
            connected.remove(websocket)
            
            exit_msg = json.dumps({'service_info':'Client ({}:{}) disconnected'
                                   .format(*websocket.remote_address)})
            await asyncio.wait([client.send(exit_msg) for client in connected])
            
            break
            

if __name__ == '__main__':
    addr, port = 'localhost', 5995
    
    async def run_server(addr, port, stop):
        async with websockets.serve(process, addr, port):
            print(f'Starting websocket server on {addr}:{port}')
            await stop
            print('Shutting down websocket server ...') 
    
    loop = asyncio.get_event_loop()
    
    # Unix-only approach (handling signals)
    stop = asyncio.Future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    loop.run_until_complete(run_server(addr, port, stop))    
    