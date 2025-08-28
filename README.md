# Splitty-CLI
A command-line utility for simple group expense tracking: after a long vacation together, settling the books can be a chore. This allows you to enter any number of transactions between you and your friends and calculate who owes who how much. 

# About
The Debt Splitter is a Python command-line utility designed to simplify group expense tracking. It reads a CSV file containing shared transactions and calculates the final net amount each person owes or is owed. The script handles complex scenarios, such as circular debts, by netting out balances to provide a clear, final accounting.

# Features
* Configurable Parsing: Specify a configuration file to define all participants in the expenses.
* Dynamic Calculation: Automatically calculates each person's fair share for every transaction.
* Circular Debt Resolution: Intelligently collapses circular debt between two parties to show a single, clear net balance.
* Robust Error Handling: Provides user-friendly error messages for missing files or invalid data.

# Getting Started
Prerequisites
To run this script, you need Python 3.6 or newer. All required libraries are part of the standard Python distribution.

# Installation
Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/splitty-cli.git
cd splitty-cli
```

# Usage
The script is run from the command line and requires two arguments: the path to the input CSV file and the path to the configuration file.

```bash
python splitty.py --input <path_to_data_file.csv> --config <path_to_conf_file.json>
```

# Example:

```bash
python splitty.py --input example_data.csv --config conf.json
```

# Configuration
The conf.json file is used to define the participants in the expense tracking.

* split_column_index: The column number (starting from 0) that contains the comma-separated strings to be parsed. For the included example_data.csv, this value is 3.
* payers: A comma-separated string of names of all people who can pay for an expense.
* payees: A comma-separated string of names of all people who can be "paid for" in a transaction.

Example conf.json:

```JSON
{
	"split_column_index": 3,
	"payers": "Joseph,Tim,Bob",
	"payees": "Joseph,Tim,Bob"
}
```

# Data Format
The script expects a CSV file with at least four columns.
1. The first column is a note to identify the transaction
2. The second column is the amount that the payer paid in that transaction
3. The third column is the name of the payer for the transaction
4. The fourth column must contain a comma-separated list of names (or other identifiers) for who was paid for in that transaction

Example example_data.csv:

```
Location,Amount,Paid By,Paid For
Jersey Mike's,36.14,Joseph,"Joseph, Tim, Bob"
Uber,32.94,Tim,"Joseph, Tim, Bob"
In-N-Out,24.11,Joseph,"Joseph, Bob"
```

# Tests
To ensure the script works correctly, a suite of tests is included. You can run them using pytest to check for parsing errors, calculation bugs, and proper error handling.

To run all tests, simply use these commands from the project's root directory:

```bash
pip install pytest
pytest
```

# License
This project is licensed under the MIT License - see the LICENSE.md file for details.

# Acknowledgments
This project was developed with the assistance of Gemini AI, which helped me write the tests because otherwise I just wouldn't have written any...
