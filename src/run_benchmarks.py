import os
import sys
import argparse
import json

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-c', '--criteria', 
                        choices=['statement', 'branch'], 
                        default='statement',
                        help='Choose coverage criteria from "statement" or "branch".')
arg_parser.add_argument('-p', '--prioritization',
                        choices=['baseline', 'random', 'total_cov', 'additional_cov'],
                        default='baseline',
                        help='Choose from "baseline", "random", "total_cov", "additional_cov". Default is "baseline".')

arg_parser.add_argument('-b', '--benchmark',
                        nargs='+',
                        default='schedule2',
                        help='Choose a benchmark to run. Default is "schedule2". Can pass "all".')

args = arg_parser.parse_args()

os.chdir(sys.path[0])

bm_relative_path = "../benchmarks"

os.chdir(bm_relative_path)
# benchmarks = os.listdir(".")

# # for bm in benchmarks:

# #   project = os.path.join(".", bm)
# #   os.chdir(project)
# #   os.system("make clean")
# #   os.system("make")

# #   with open("universe.txt", 'r') as f:
# #     for execution_args in f:
# #       os.system(project + " " + execution_args)


# #   os.chdir("..")


# exmaple
# schedule2
# statement
# total coverage

class StatementCoverage:
  def __init__(self, testid=None, total_line_no=None, executed_line_no=None) -> None:
    self.testid = testid
    self.total_line_no = total_line_no if total_line_no is not None else set()
    self.executed_line_no = executed_line_no if executed_line_no is not None else set()

  def statement_coverage(self):
    return len(self.executed_line_no) / len(self.total_line_no)


  def to_dict(self):
    return {
            # "total_line_no": list(self.total_line_no),
            # "executed_line_no": list(self.executed_line_no),
            "testid": self.testid,
            "statement_cov_rate": self.statement_coverage()}

  def __str__(self) -> str:
    return str(self.testid) + str(self.total_line_no) + '%' + str(self.executed_line_no) + '%' + str(self.statement_coverage())



valid_choices = ['tcas', 'totinfo', 'schedule2', 'schedule', 'print_tokens', 'replace', 'print_tokens2']

if 'all' in args.benchmark:
  benchmarks = valid_choices
else:
  benchmarks = args.benchmark

for bm in benchmarks:
  bm_src = bm + '.c'
  project = os.path.join('.', bm)
  os.chdir(project)
  os.system("make clean")
  os.system("make")
  test_coverages = []
  test_count = 0
  with open("universe.txt", 'r') as f:
    for tid, execution_args in enumerate(f):
      test_count += 1
      os.system(project + " " + execution_args)
      os.system("gcov " + "--json-format " + bm_src)
      cov_data_file = bm_src + ".gcov" + ".json"
      os.system("gunzip " + cov_data_file + '.gz')
      # parse json
      with open(cov_data_file) as cov_f:
        cov_data = json.load(cov_f)

      if len(cov_data["files"]) == 1:
        file = cov_data["files"][0]
        sc = StatementCoverage()
        sc.total_line_no = {x['line_number'] for x in file['lines']}
        sc.executed_line_no = {x['line_number'] for x in file['lines'] if x['count']>=1}
        sc.testid = tid
      else:
        sys.exit('Too many files(>1) to coverage')

      test_coverages.append(sc)
      # delete gcda, json files
      os.remove(bm + '.gcda')
      os.remove(cov_data_file)

  dp = test_coverages[0].total_line_no
  for j in range(1, len(test_coverages)):
    if dp != test_coverages[j].total_line_no:
      sys.exit(f'Program total line numbers difference. dp:{len(dp)}, test_coverages[{j}]:{len(test_coverages[j].total_line_no)}')
  print(f'All test cases have the same total line numbers: {len(dp)}')

  # sort by statement coverage
  test_coverages.sort(key=lambda x: x.statement_coverage())
  test_suite = [test_coverages[0].testid]
  coverd_lines = test_coverages[0].executed_line_no
  for idx in range(1, len(test_coverages)):

    if len(coverd_lines) == len(dp):
      break

    if coverd_lines < test_coverages[idx].executed_line_no:
      test_suite.append(test_coverages[idx].testid)
      coverd_lines = coverd_lines.union(test_coverages[idx].executed_line_no)

  with open("universe.txt", 'r') as f:
    lines = f.readlines()
    new_tests = [lines[i] for i in test_suite]
    with open("my_test_suite.txt", 'w') as f:
      f.writelines(new_tests)
    



# print(f'test_suite len: {len(test_suite)}, test_count: {test_count}')
# print (f'test_suite: {test_suite}')