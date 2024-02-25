import os
import sys
import argparse
import json
import random

class StatementCoverage:
  def __init__(self, testid=None, total_line_no=None, executed_line_no=None) -> None:
    self.testid = testid
    self.total_line_no = total_line_no if total_line_no is not None else set()
    self.executed_line_no = executed_line_no if executed_line_no is not None else set()

  def statement_coverage(self):
    return len(self.executed_line_no) / len(self.total_line_no)


  def to_dict(self):
    return {
            "testid": self.testid,  
            "total_line_num": len(self.total_line_no),
            "executed_line_num": len(self.executed_line_no),
            "executed_line_no": list(self.executed_line_no),
            "statement_coverage": self.statement_coverage()}

  def __str__(self) -> str:
    return 'test id: ' + str(self.testid) + '\ntotal line num: ' + str(len(self.total_line_no)) + '\nexecuted line num: ' + str(len(self.executed_line_no)) + '\nstatement coverage: ' + str(self.statement_coverage())


def parse_benchmark_list(args):
  
  valid_choices = ['tcas', 'totinfo', 'schedule', 'schedule2', 'printtokens', 'printtokens2', 'replace']

  if 'all' in args.benchmark:
    benchmarks = valid_choices
  else:
    benchmarks = args.benchmark

  return benchmarks


def goto_benchmark_dir_and_clean(bm):
  project = os.path.join('.', bm)
  os.chdir(project)

  os.system("make clean")
  os.system("make")


def single_execution(executable_name, test_path):

  scs = []
  test_count = 0
  with open(test_path, 'r') as f:
    for tid, execution_args in enumerate(f):
      test_count += 1
      os.system(executable_name + " " + execution_args)
      os.system("gcov " + "--json-format " + executable_name + ".c")
      cov_data_file = executable_name + ".c" + ".gcov" + ".json"
      os.system("gunzip " + cov_data_file + '.gz')
      with open(cov_data_file) as cov_f:
        cov_data = json.load(cov_f)
      if len(cov_data["files"]) != 1:
        sys.exit('Too many files(>1) to coverage')
      cov_file = cov_data["files"][0]
      sc = StatementCoverage()
      sc.total_line_no = {x['line_number'] for x in cov_file['lines']}
      sc.executed_line_no = {x['line_number'] for x in cov_file['lines'] if x['count']>=1}
      sc.testid = tid
      scs.append(sc)
      os.remove(executable_name + '.gcda')
      os.remove(cov_data_file)

  return scs, test_count


def save_single_execution_statistics(bm):
  project = os.path.join('.', bm)
  goto_benchmark_dir_and_clean(bm)

  scs, test_count = single_execution(project, 'universe.txt')
  with open("single_execution_statistics.json", 'w') as f:
    total_line_no = list(scs[0].total_line_no)
    d = {'test_count': test_count}
    d['total_line_no'] = total_line_no
    d['single_execution_statement_coverages'] = [sc.to_dict() for sc in scs]
    
    json.dump(d, f, indent=2)
  
  os.chdir('..')


def load_single_execution_statistics():
  try:
    with open("single_execution_statistics.json", 'r') as f:
      d = json.load(f)
      return d['single_execution_statement_coverages'], d['test_count']
  except Exception as e:
    print(e)
    sys.exit('Failed to load single_execution_statistics.json')
    

def load_baseline():
  try:
    with open('baseline.json', 'r') as f:
      return json.load(f)
  except Exception as e:
    print(e)
    sys.exit('Failed to load baseline.json')


def statement_total(bm):

  project = os.path.join('.', bm)

  os.chdir(project)
  os.system('rm -rf test_suite_statement_total.txt')
  
  baseline = load_baseline()

  baseline_executed_line_num = baseline['executed_line_num']

  test_coverages, test_count = load_single_execution_statistics()

  # check if all test cases have the same total line numbers
  # for j in range(1, len(test_coverages)):
  #   if total_line_num != len(test_coverages[j]['total_line_no']):
  #     sys.exit(f'Program total line numbers difference. total_line_num:{total_line_num}, test_coverages[{j}]:{len(test_coverages[j]['total_line_no'])}')
  # print(f'All test cases have the same total line numbers: {total_line_num}')

  # sort by statement coverage
  
  test_coverages.sort(key=lambda x: len(x['executed_line_no']), reverse=True)
  test_suite = [test_coverages[0]['testid']]
  coverd_lines = set(test_coverages[0]['executed_line_no'])
  for idx in range(1, len(test_coverages)):
    # with open('log.txt', 'a') as f:
    #   f.write(f'coverd_lines: {len(coverd_lines)}, baseline_executed_line_num: {baseline_executed_line_num}\n')
    if len(coverd_lines) >= baseline_executed_line_num:
      # print(f'coverd_lines: {len(coverd_lines)}, baseline_executed_line_num: {baseline_executed_line_num}')
      break
    
    diff = set(test_coverages[idx]['executed_line_no']).difference(coverd_lines)
    if len(diff) > 0:
      test_suite.append(test_coverages[idx]['testid'])
      coverd_lines = coverd_lines.union(diff)

  with open("universe.txt", 'r') as f:
    lines = f.readlines()
    new_tests = [lines[i] for i in test_suite]
    with open("test_suite_statement_total.txt", 'w') as f:
      f.writelines(new_tests)

  print(f'test_suite len: {len(test_suite)}, total_test_count: {test_count}')
  print (f'test_suite: {test_suite}')
  print(f'coverd_lines: {len(coverd_lines)}, baseline_executed_line_num: {baseline_executed_line_num}')
  os.chdir('..')
    

def accumulate_execution(executable_name, test_path):
  test_count = 0
  with open(test_path, 'r') as f:
    for line in f:
      test_count += 1
      os.system(executable_name + " " + line)
    
  os.system("gcov " + "--json-format " + executable_name + ".c")
  cov_data_file = executable_name + ".c" + ".gcov" + ".json"
  os.system("gunzip " + cov_data_file + '.gz')
  with open(cov_data_file) as cov_f:
    cov_data = json.load(cov_f)
  if len(cov_data["files"]) != 1:
    sys.exit('Too many files(>1) to coverage')
  cov_file = cov_data["files"][0]
  sc = StatementCoverage() 
  sc.total_line_no = {x['line_number'] for x in cov_file['lines']}
  sc.executed_line_no = {x['line_number'] for x in cov_file['lines'] if x['count']>=1}

  os.remove(executable_name + '.gcda')
  os.remove(cov_data_file)

  return sc, test_count


def baseline_statement_coverage(bm):
  
  project = os.path.join('.', bm)

  goto_benchmark_dir_and_clean(bm)
  os.remove('baseline.json')

  sc, test_count = accumulate_execution(project, 'universe.txt')
  
  print(f'Baseline statement coverage for {bm}: {sc.statement_coverage()}')
  with open("baseline.json", 'w') as f:
    d = sc.to_dict()
    d['test_count'] = test_count
    json.dump(d, f, indent=2)
    # f.write('\n' + str(test_count) + ' test cases\n')

  os.chdir('..')


def verify(bm, criteria, prioritization):

  project = os.path.join('.', bm)

  os.chdir(project)
  os.system('rm -rf ' + bm + '.gcda')

  test_suite_name = 'test_suite_' + criteria + '_' + prioritization + '.txt'

  sc, _ = accumulate_execution(project, test_suite_name)

  with open('baseline.json', 'r') as f:
    baseline = json.load(f)
  
  baseline_cov = baseline['statement_coverage']

  if round(sc.statement_coverage(), 2) != round(baseline_cov, 2):
    sys.exit(f'Failed to cover all lines. statement_coverage: {sc.statement_coverage()}, baseline_cov: {baseline_cov}')
  
  print(f'Verified {criteria}_{prioritization} coverage for {bm}:\n execution_cov: {sc.statement_coverage()}, baseline_cov: {baseline_cov}')

  os.chdir('..')


def statement_random(bm):

  os.chdir('./' + bm)
  os.system('rm -rf test_suite_statement_random.txt')

  baseline = load_baseline()
  
  scs, test_count = load_single_execution_statistics()

  random.seed(42)
  indices = list(range(test_count))
  random.shuffle(indices)

  test_suite = [scs[indices[0]]['testid']]
  coverd_lines = set(scs[indices[0]]['executed_line_no'])

  for i in indices[1:]:
    sc = scs[i]

    if len(coverd_lines) >= baseline['executed_line_num']:
      break
    
    diff = set(sc['executed_line_no']).difference(coverd_lines)
    if len(diff) > 0:
      test_suite.append(sc['testid'])
      coverd_lines = coverd_lines.union(diff)

  with open('universe.txt', 'r') as f:
    lines = f.readlines()
    new_tests = [lines[i] for i in test_suite]
    with open('test_suite_statement_random.txt', 'w') as f:
      f.writelines(new_tests) 
  
  print('*'*10)
  print(f'test_suite len: {len(test_suite)}, total_test_count: {test_count}')
  print (f'test_suite: {test_suite}')
  print(f'coverd_lines: {len(coverd_lines)}, baseline_executed_line_num: {baseline['executed_line_num']}')

  os.chdir('..')


def statement_additional(bm): 

  os.chdir('./' + bm)
  os.system('rm -rf test_suite_statement_random.txt')

  baseline = load_baseline()
  
  scs, test_count = load_single_execution_statistics()

  max_cov_test = max(scs, key=lambda x: x['executed_line_num'])
  test_suite = [max_cov_test['testid']]
  coverd_lines = set(max_cov_test['executed_line_no'])
  
  scs.remove(max_cov_test)

  while len(coverd_lines) < baseline['executed_line_num'] and len(scs) > 0:

    all_diffs = [set(x['executed_line_no']).difference(coverd_lines) for x in scs]
    max_diff = max(all_diffs, key=lambda y: len(y))
    max_diff_idx = all_diffs.index(max_diff)

    if len(max_diff) > 0:
      test_suite.append(scs[max_diff_idx]['testid'])
      coverd_lines = coverd_lines.union(max_diff)
      scs.pop(max_diff_idx)

  with open('universe.txt', 'r') as f:
    lines = f.readlines()
    new_tests = [lines[i] for i in test_suite]
    with open('test_suite_statement_additional.txt', 'w') as f:
      f.writelines(new_tests)

  print(f'test_suite len: {len(test_suite)}, total_test_count: {test_count}')
  print (f'test_suite: {test_suite}')
  print(f'coverd_lines: {len(coverd_lines)}, baseline_executed_line_num: {baseline['executed_line_num']}')
  os.chdir('..')


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

  arg_parser.add_argument('-v', '--verify',
                          action='store_true',
                          help='Verify the test suite.')
  
  arg_parser.add_argument('-s', '--sss',
                        action='store_true',
                        help='Create single execution statement coverage statistics.')

  args = arg_parser.parse_args()

  os.chdir(sys.path[0])

  os.chdir('../benchmarks')
  benchmarks = parse_benchmark_list(args)

  if args.sss:
    for bm in benchmarks:
      save_single_execution_statistics(bm)
    sys.exit('Single execution statement coverage statistics created')
  
  if args.verify:
    if args.prioritization == 'baseline':
      sys.exit('Cannot verify baseline statement coverage')
    for bm in benchmarks:
      verify(bm, args.criteria, args.prioritization)
    sys.exit('Test suite verified')

  if args.criteria == 'statement':
    if args.prioritization == 'baseline':
      for bm in benchmarks:
        baseline_statement_coverage(bm)
    elif args.prioritization == 'total':
      for bm in benchmarks:
        statement_total(bm)
    elif args.prioritization == 'random':
      for bm in benchmarks:
        statement_random(bm) 
    elif args.prioritization == 'additional':
      for bm in benchmarks:
        statement_additional(bm)
  elif args.criteria == 'branch':
    if args.prioritization == 'baseline':
      pass
    elif args.prioritization == 'total':
      pass
    elif args.prioritization == 'random':
      pass 
    elif args.prioritization == 'additional':
      pass 


if __name__ == '__main__':
  main()