

# AlgoTrading Backtesting Engine

Python-based algorithmic trading backtesting engine.


## Current Status

- Completed up to **Step 8**
- Features implemented:
  - Position sizing (>1 share)
  - Next-bar execution (signal at close, execute at next open)
  - Slippage model (fixed bps)
  - Commission model (per share)
- All unit tests rewritten and passing


## Project Structure

project/
│
├── main.py
├── data_loader.py
├── compute_average.py
├── process_1_day.py
├── trend_signal.py
├── mean_rev_signal.py
│
├── data/
│ └── 5_day_input.csv
│
├── tests/
│ ├── test_data_loader.py
│ ├── test_compute_average.py
│ ├── test_process_1_day.py
│ ├── test_trend_signal.py
│ ├── test_mean_rev_signal.py
│ └── test_execution_per_day.py
│
└── .venv/



## Setup


### 1. Create virtual environment (if not already created)

bash:

"python3 -m venv .venv"





### 2. Activate virtual environment

Mac/Linux:

"source .venv/bin/activate"





### 3. Install dependencies

"pip install pytest"





Running Tests from the command line: 

From the project root directory (project/)

Run all tests:

"PYTHONPATH=. pytest tests/"

or (quiet mode):

"PYTHONPATH=. pytest -q tests/"


To run only a specific test file:

"PYTHONPATH=. pytest tests/test_file_name.py"

or:

"PYTHONPATH=. pytest -q tests/test_file_name.py"






Notes:

"PYTHONPATH=. " ensures that the modules are imported correctly when running from root
".venv/"  is local and should not be committed
Only small test datasets are included ("5_day_input.csv")





Next Step
Step 9: Performance Metrics