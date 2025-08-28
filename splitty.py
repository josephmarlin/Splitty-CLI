# Copyright (c) 2025 Joseph Marlin
# This code is licensed under the MIT License.
# See the LICENSE file for details.

import argparse
import csv
import json

def parse_csv(file_path, split_column_index):
    """
    Parses a CSV file based on the specified parameters.
    """
    parsed_data = []
    
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            
            for row in reader:
                # Ensure the row has enough columns
                if len(row) <= split_column_index:
                    print(f"Skipping malformed row: {row}")
                    continue
                
                # Split the specified column
                column_to_split = row[split_column_index]
                split_list = column_to_split.replace(" ", "").split(',')
                
                if split_list == ['']:
                    print(f"Skipping malformed row (missing \"paid-for\": {row}")
                    continue
                
                # Build and add the new row
                try:
                    parsed_data.append({"location": row[0], "amount": float(row[1]), "payer": row[2], "paidfor":  split_list})
                except ValueError:
                    print(f"Error: Could not convert amount '{row[1]}' to a number.")
                    raise ValueError
                
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit
        
    return parsed_data

def main():
    parser = argparse.ArgumentParser(description='Parse a CSV file with configurable options.')
    parser.add_argument('--input', '-i', dest='input_file', help='Path to the input CSV file.', required=True)
    parser.add_argument('--config', '-c', dest='config_file', help='Path to a JSON configuration file.', required=True)

    args = parser.parse_args()

    # Load configuration from the JSON file
    try:
        with open(args.config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: The configuration file '{args.config_file}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The configuration file is not valid JSON.")
        return None

    # Call the parsing function with the provided arguments and config settings
    split_column_index = config.get('split_column_index', 3)
    data = parse_csv(args.input_file, split_column_index)
    
    # Get settings from the config file, with default values if not specified
    payers = config.get('payers', "")
    payees = config.get('payees', "")
    
    # Parse the payers and the payees
    payers = payers.replace(" ", "").split(',')
    payees = payees.replace(" ", "").split(',')
    
    #Generate our 2D dictionary of payers to payees
    owe_matrix = {payer: {payee: 0 for payee in payees} for payer in payers}
    
    # Do the math of who owes who how much
    for row in data:
        if row["payer"] not in owe_matrix:
            print(f"Warning: Payer '{row['payer']}' not in configured payers. Skipping row.")
            continue
            
        fairshare = float(row["amount"])/len(row["paidfor"])
        
        for ower in row["paidfor"]:
            # This is a defensive check to avoid KeyErrors
            if ower not in owe_matrix[row["payer"]]:
                print(f"Warning: Payee '{ower}' for payer '{row['payer']}' not in configured payees. Skipping.")
                continue
            owe_matrix[row["payer"]][ower] = owe_matrix[row["payer"]][ower] + fairshare
            
    # Now we have to collapse the dictionary - right now it might say A owes B $5 and B owes A $3. We need a final accounting. 
    for payer in payers:
        for payee in payees:
            #if the two people don't BOTH owe each other some amount, we're done and can move on
            if payer != payee and (owe_matrix[payer][payee] == 0 or owe_matrix[payee][payer] == 0):
                continue
                
            #uh oh, the two people owe each other.
            if owe_matrix[payer][payee] > owe_matrix[payee][payer]:
                owe_matrix[payer][payee] = owe_matrix[payer][payee] - owe_matrix[payee][payer]
                owe_matrix[payee][payer] = 0
            else:
                owe_matrix[payee][payer] = owe_matrix[payee][payer] - owe_matrix[payer][payee]
                owe_matrix[payer][payee] = 0

            
    # If someone is owed something, print it:
    for payer in owe_matrix:
        for payee in owe_matrix[payer]:
            if owe_matrix[payer][payee] != 0 and payee != payer:
                print(f"{payee} owes {payer} $ {round(owe_matrix[payer][payee],2):.2f}")


if __name__ == "__main__":
    main()