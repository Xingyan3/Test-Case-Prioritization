import re
import os
import sys

bms = ['tcas', 'totinfo', 'schedule', 'schedule2', 'printtokens', 'printtokens2', 'replace']

os.chdir(sys.path[0])


with open('../.gitignore', 'a') as f:
  for bm in bms:

    faulty_dirs_pattern = re.compile(r'^v\d+$')
    faulty_dirs = [d for d in os.listdir(f'../benchmarks/{bm}') if faulty_dirs_pattern.match(d)]

    for d in faulty_dirs:
      f.write(f'\n/benchmarks/{bm}/{d}/{bm}')
