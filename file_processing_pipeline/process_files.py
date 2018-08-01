import os
import fnmatch
import re

def gen_get_filenames(file_pattern, dir_name):
    for dir_path, dir_list, file_list in os.walk(dir_name):
        for fn in fnmatch.filter(file_list, file_pattern):
            yield os.path.join(dir_path, fn)
            

def gen_open_files(filenames):
    '''
    Generates file objects from passed filenames
    '''
    for fn in filenames:
        f = open(fn, 'rt')
        yield f
        f.close()
        
        
def gen_file_getline(file_objects):
    for f in file_objects:
        yield from f

        
def grep_lines(pattern, lines):
    pat = re.compile(pattern)
    
    for line in lines:
        if pat.search(line):
            yield line
        

fname_pattern = '*.csv'
dir_name = '<your_directory>'

filenames = gen_get_filenames(fname_pattern, dir_name)
lines = gen_file_getline(gen_open_files(filenames))
moves_lines = grep_lines('^The', lines)

for l in moves_lines:
    print(l)