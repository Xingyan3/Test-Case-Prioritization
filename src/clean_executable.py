import sys
import os
import re

benchmark = sys.argv[1]

os.chdir(sys.path[0])
os.chdir('../benchmarks/' + benchmark)

faulty_dirs_pattern = re.compile(r'^v\d+$')
faulty_dirs = [d for d in os.listdir('.') if faulty_dirs_pattern.match(d)]

for d in faulty_dirs:
  os.chdir(d)
  os.system(f'rm -rf {benchmark}')
  os.chdir('..')