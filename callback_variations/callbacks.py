
'''
Supplying callbacks with extra state
'''

def apply_with_callback(func, args, *, callback):
    result = func(*args)
    callback(result)

def add(x, y):
    return x + y
    
# Closure version
def make_callback():
    sequence_num = 0
    def func(result):
        nonlocal sequence_num
        sequence_num += 1
        print('[{}] (closure) Got result: {}'.format(sequence_num, result))
    return func

handler = make_callback()
apply_with_callback(add, (1,3), callback=handler)
apply_with_callback(add, (2,3), callback=handler)
apply_with_callback(add, (4,3), callback=handler)

print('*' * 20)

# Coroutine version
def callback_coroutine():
    sequence_num = 0
    while True:
        result = yield
        sequence_num += 1
        print('[{}] (coroutine) Got result: {}'.format(sequence_num, result))
        
handler = callback_coroutine()
next(handler)
apply_with_callback(add, (1,3), callback=handler.send)
apply_with_callback(add, (2,3), callback=handler.send)
apply_with_callback(add, (4,3), callback=handler.send)
        

'''
callbacks with coroutines
'''

import queue
import multiprocessing
import operator
import collections
import functools
import time

pool = multiprocessing.Pool(3)
apply_with_callback = pool.apply_async

class FunctionParts:
    def __init__(self, func, args):
        self.func = func
        self.args = args
        self.desc = func.__doc__.split(' --')[0]
        

def queued_callback(func):
    @functools.wraps(func)    
    def wrapper(*args):
        gen = func(*args)
        result_queue = queue.Queue()
        result_queue.put(None)
        
        while True:
            try:
                result = result_queue.get()
                func_parts = gen.send(result if result is None 
                                      else (func_parts.desc, 
                                            func_parts.args,
                                            'result: {!r}'.format(result)))
                apply_with_callback(func_parts.func, func_parts.args, 
                                    callback=result_queue.put)
                time.sleep(1)
            except StopIteration:
                break
        
    return wrapper

@queued_callback
def gen_func_parts():
    result = yield FunctionParts(operator.add, (1, 2))
    print(result)
    result = yield FunctionParts(operator.mul, (4, 2))
    print(result)
    result = yield FunctionParts(operator.pow, (2, 8))
    print(result)
    print('End of coroutine. Thanks.')

gen_func_parts()

