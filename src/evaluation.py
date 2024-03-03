import argparse
import os
import sys
import re
import subprocess

Compiling_Command = {'tcas': 'gcc -Wno-return-type -g -o tcas tcas.c',
                     'totinfo': 'gcc -Wno-return-type -g -o totinfo totinfo.c -lm',
                     'schedule': 'gcc -Wno-return-type -g -o schedule schedule.c',
                     'schedule2': 'gcc -Wno-return-type -g -o schedule2 schedule2.c',
                     'printtokens': 'gcc -Wno-return-type -g -o printtokens printtokens.c',
                     'printtokens2': 'gcc -Wno-return-type -g -o printtokens2 printtokens2.c',
                     'replace': 'gcc -Wno-return-type -g -o replace replace.c -lm'}


def parse_benchmark_list(args):
  
  valid_choices = ['tcas', 'totinfo', 'schedule', 'schedule2', 'printtokens', 'printtokens2', 'replace']

  if 'all' in args.benchmark:
    benchmarks = valid_choices
  else:
    benchmarks = args.benchmark

  return benchmarks


def evaluate(benchmark, criteria, prioritization, baseline_suite):
  os.chdir(sys.path[0])
  os.chdir('../benchmarks/' + benchmark)

  if not os.path.exists(benchmark):
    os.system(Compiling_Command[benchmark])

  faulty_dirs_pattern = re.compile(r'^v\d+$')
  faulty_dirs = [d for d in os.listdir('.') if faulty_dirs_pattern.match(d)]

  for d in faulty_dirs:
    os.chdir(d)
    if not os.path.exists(benchmark):
      os.system(Compiling_Command[benchmark])
    os.chdir('..')

  if baseline_suite:
    suite = 'universe.txt'
  else:
    suite = 'test_suite_' + criteria + '_' + prioritization + '.txt'

  with open(suite, 'r') as f:
    test_suite = f.readlines()
  
  exposed_faults = []
  exposed_faults_set = set()

  for t in test_suite:
    test_input, file_in, test_file_path = t.rstrip('\n').rpartition('<')
    
    # print('./' + benchmark + ' ' + test_input)
    # print(test_file_path.split(' ')[-1])

    if file_in:
      with open(test_file_path.split(' ')[-1], 'r') as f:
        file_data = f.read()
      origin_output = subprocess.run('./' + benchmark + ' ' + test_input, shell=True, input=file_data, capture_output=True, text=True).stdout
      # print('*'*10)
      # print(f'original output: {origin_output}')
      for d in faulty_dirs:
        faulty_output = subprocess.run(f'./{d}/' + benchmark + ' ' + test_input, shell=True, input=file_data, capture_output=True, text=True, errors='ignore').stdout # error in printtokens2 -t
        
        if origin_output != faulty_output:
          exposed_faults.append({'faulty_version': d.split('v')[1], 'expected_output': origin_output, 'actual_output': faulty_output})
          exposed_faults_set.add(d.split('v')[1])
    else:
      test_input = test_file_path
      origin_output = subprocess.run('./' + benchmark + ' ' + test_input, shell=True, capture_output=True, text=True).stdout
      # print('*'*10)
      # print(f'original output: {origin_output}')
      for d in faulty_dirs:
        faulty_output = subprocess.run(f'./{d}/' + benchmark + ' ' + test_input, shell=True, capture_output=True, text=True, errors='ignore').stdout
        
        if origin_output != faulty_output:
          exposed_faults.append({'faulty_version': d.split('v')[1], 'expected_output': origin_output, 'actual_output': faulty_output})
          exposed_faults_set.add(d.split('v')[1])

      
      # print(f'faulty output: {faulty_output}')

  print(f'Exposed faults for {benchmark}: {exposed_faults_set}')
  print(f'Number of exposed faults: {len(exposed_faults_set)}')

def main():
  arg_parser = argparse.ArgumentParser()

  arg_parser.add_argument('-c', '--criteria', 
                          choices=['statement', 'branch'], 
                          default='statement',
                          help='Choose coverage criteria from "statement" or "branch".')

  arg_parser.add_argument('-p', '--prioritization',
                          choices=['baseline', 'random', 'total', 'additional'],
                          default='baseline',
                          help='Choose from "baseline", "random", "total", "additional". Default is "baseline".')

  arg_parser.add_argument('-b', '--benchmark',
                          nargs='+',
                          default='schedule2',
                          help='Choose a benchmark to run. Default is "schedule2". Can pass "all".')

  arg_parser.add_argument('-t', '--baseline_suite',
                          action='store_true',
                          help='Explore the set of faults exposed by the original test suite.')
  
  args = arg_parser.parse_args()
  benchmarks = parse_benchmark_list(args)

  for bm in benchmarks:
    evaluate(bm, args.criteria, args.prioritization, args.baseline_suite)

if __name__ == '__main__':
  main()
  
