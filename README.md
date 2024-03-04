All source files are under the /src directory. The entire project was implemented in Python.

Requirements to run our python project:

- Ubuntu 20.04
- Python 3

Clone repo and change directory to the source before running:
```bash
git clone https://github.com/ucr-cs206/cs206-project-xyzry.git
cd cs206-project-xyzry
cd src
```

# Create Test Suite
The program to create the test suites is `create_test_suite.py`.

The `create_test_suite.py` script is designed to create a test suite based on specified criteria, prioritization strategies, benchmarks, and verification options.

## Basic Usage
To run the program with default settings, simply execute the script without any arguments:

```shell
python create_test_suite.py 
```
This will run the program using the default options: statement coverage criteria, baseline prioritization, and the `schedule2` benchmark.

## Arguments
The script supports several command-line arguments to customize its execution:

`-c`, `--criteria`: Choose the coverage criteria. Options are `statement` or `branch`. Default is `statement`.

`-p`, `--prioritization`: Select the test case prioritization strategy. Choices are `baseline`, `random`, `total`, `additional`. Default is `baseline`.

`-b`, `--benchmark`: Specify one or more benchmarks to run. Default is schedule2. To run all benchmarks, pass `all`. Choos from [`tcas`, `totinfo`, `schedule`, `schedule2`, `totinfo`, `printtokens`, `printtokens2`, `replace`].

`-v`, `--verify`: Enable verification of the test suite. This does not take any value. Will print verification result. 

`-s`, `--sss`: Create single execution statement coverage statistics. This does not take any value. Will create `single_execution_{criteria}_statistics.json`

## Examples
Here are some examples of how to run the program with different configurations:

- Run with branch coverage criteria:
```shell
python create_test_suite.py -c branch
```

- Use the total prioritization strategy:
```shell
python create_test_suite.py -p total
```

- Run with a specific benchmark (e.g., `tcas`):
```shell
python create_test_suite.py -b tcas
```

- Run with multiple benchmarks (e.g., `tcas`, `totinfo`):
```shell
python create_test_suite.py -b tcas totinfo
```
- Enable test suite verification:
```shell
python create_test_suite.py -v
```

- Generate single execution statement coverage statistics:
```shell
python create_test_suite.py -s
```

- Combine multiple arguments:
```shell
python create_test_suite.py -c branch -p additional -b all
```

## Additional Information
For more details on the usage and options, consult the program's help:
```shell
python create_test_suite.py --help
```

## Created test suites
**The created test suites are located under the each benchmark directory separately.**

Their names have the format: `test_suite_{criteria}_{prioritization}.txt`.

E.g. `test_suite_statement_total.json` represents the test suites created using the statement coverage and total coverage prioritization.

# Evaluation

The program to evaluate is `evaluation.py`.

The `evaluation.py` script facilitates the evaluation of test suites based on specific coverage criteria, prioritization strategies, and benchmarks.


## Basic Usage

To execute the program with its default settings, you can run the script without any additional arguments:

```bash
python evaluation.py
```
By default, this will evaluate using statement coverage criteria, random prioritization, and the `schedule2` benchmark.

## Arguments
The script accepts several command-line arguments to tailor its operation:

`-c`, `--criteria`: Specifies the coverage criteria to be used. Options include `statement` and `branch`, with `statement` being the default.

`-p`, `--prioritization`: Selects the test case prioritization strategy from `random`, `total`, and `additional`. The default is `random`.

`-b`, `--benchmark`: Designates one or more benchmarks to evaluate. The default is `schedule2`. You can specify multiple benchmarks by separating them with spaces or use `all` to select all available benchmarks. Choos from [`tcas`, `totinfo`, `schedule`, `schedule2`, `totinfo`, `printtokens`, `printtokens2`, `replace`].

`-t`, `--baseline_suite`: If set, evaluates the effectiveness of the original test suite in exposing faults.

## Examples
Here are several examples showing how to use the script with various configurations:

- Evaluate using branch coverage criteria:
```bash
python evaluation.py -c branch
```
- Apply the total prioritization strategy:
```bash
python evaluation.py -p total
```
- Evaluate a specific benchmark, such as `tcas`:
```bash
python evaluation.py -b tcas
```
- Evaluate multiple benchmarks, for instance, tcas and `replace`:
```bash
python evaluation.py -b tcas replace
```
- Evaluate with all available benchmarks:
```bash
python evaluation.py -b all
```
- Explore the set of faults exposed by the baseline test suite:
```bash
python evaluation.py -t
```
- Combine various arguments for a comprehensive evaluation:
```bash
python evaluation.py -c branch -r additional -b tcas totinfo -t
```

## Getting Help
For detailed information on all available options and their usage, you can refer to the program's help:
```bash
python evaluation.py --help
```
