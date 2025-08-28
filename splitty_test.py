# Copyright (c) 2025 Joseph Marlin
# This code is licensed under the MIT License.
# See the LICENSE file for details.

import io
import os
import pytest
import tempfile
import json
from splitty import parse_csv, main

def make_temp_data_file(contents):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(contents)
        return temp_file.name
        
def make_temp_config_file(contents):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as temp_config_file:
        json.dump(contents, temp_config_file)
        return temp_config_file.name
        

#Tests that the CSV is parsed correctly for a standard case.
def test_parse_csv_basic():
    csv_data = """Location,Amount,Paid By,Paid For
Denny's,62.36,P,"J,P,T,C,E"
Sato Ramen,128.74,P,"J,P,T,C,E"
In-N-Out,48.45,J,"J,P,T,C,E"
Croissant,8,E,J
T Shirt,26.54,E,J
Dumplings,20,J,E
"""
    temp_file_path = make_temp_data_file(csv_data)
    parsed_data = parse_csv(temp_file_path, split_column_index=3)

    # Assert: Define the expected output and compare
    expected_data = [
        {'location': "Denny's", 'amount': 62.36, 'payer': 'P', 'paidfor': ['J', 'P', 'T', 'C', 'E']},
        {'location': 'Sato Ramen', 'amount': 128.74, 'payer': 'P', 'paidfor': ['J', 'P', 'T', 'C', 'E']},
        {'location': 'In-N-Out', 'amount': 48.45, 'payer': 'J', 'paidfor': ['J', 'P', 'T', 'C', 'E']},
        {'location': 'Croissant', 'amount': 8, 'payer': 'E', 'paidfor': ['J']},
        {'location': 'T Shirt', 'amount': 26.54, 'payer': 'E', 'paidfor': ['J']},
        {'location': 'Dumplings', 'amount': 20, 'payer': 'J', 'paidfor': ['E']}
    ]

    assert parsed_data == expected_data

    os.remove(temp_file_path)

# - Test that rows are correctly interpreted despite an empty line
def test_parse_csv_empty_row():
    csv_data = """Location,Amount,Paid By,Paid For
Denny's,62.36,P,"J,P,T,C,E"

In-N-Out,48.45,J,"J,P,T,C,E"
"""

    temp_file_path = make_temp_data_file(csv_data)
    parsed_data = parse_csv(temp_file_path, split_column_index=3)

    # Assert that 
    expected_data = [
        {'location': "Denny's", 'amount': 62.36, 'payer': 'P', 'paidfor': ['J', 'P', 'T', 'C', 'E']},
        {'location': 'In-N-Out', 'amount': 48.45, 'payer': 'J', 'paidfor': ['J', 'P', 'T', 'C', 'E']},
    ]

    assert parsed_data == expected_data

    os.remove(temp_file_path)

# - Test that a row with fewer than 4 columns is skipped
def test_parse_csv_malformed_row():
    csv_data = """Location,Amount,Paid By,Paid For
Denny's,62.36,P,"J,P,T,C,E"
In-N-Out,48.45,J
T Shirt,26.54,E,J
"""

    temp_file_path = make_temp_data_file(csv_data)
    parsed_data = parse_csv(temp_file_path, split_column_index=3)

    expected_data = [
        {'location': "Denny's", 'amount': 62.36, 'payer': 'P', 'paidfor': ['J', 'P', 'T', 'C', 'E']},
        {'location': 'T Shirt', 'amount': 26.54, 'payer': 'E', 'paidfor': ['J']},
    ]

    assert parsed_data == expected_data

    os.remove(temp_file_path)
    
# - Test that a row with an empty 'paidfor' field is skipped 
def test_parse_csv_empty_paidfor():
    """Tests that the function handles a row with an empty Paid For field."""
    csv_data = """Location,Amount,Paid By,Paid For
Trip to Mars,10000,Elon,""
"""
    
    temp_file_path = make_temp_data_file(csv_data)
    parsed_data = parse_csv(temp_file_path, split_column_index=3)

    expected_data = []

    assert parsed_data == expected_data

    os.remove(temp_file_path)
    
# - An empty CSV file should result in an empty list
def test_parse_csv_empty_file():
    """Tests that the function returns an empty list for an empty file."""
    csv_data = """Location,Amount,Paid By,Paid For
"""

    temp_file_path = make_temp_data_file(csv_data)
    parsed_data = parse_csv(temp_file_path, split_column_index=3)

    # Assert: The result 
    assert parsed_data == []

    os.remove(temp_file_path)
    
# - Ensure that an invalid dollar amount (e.g., 'abc') correctly raises an exception
def test_parse_csv_invalid_amount():
    """Tests that the function raises a ValueError for an invalid amount."""
    csv_data = """Location,Amount,Paid By,Paid For
Groceries,not-a-number,P,J
"""

    temp_file_path = make_temp_data_file(csv_data)

    # Act & Assert: This checks that calling parse_csv() with this data will raise a ValueError.
    with pytest.raises(ValueError):
        parse_csv(temp_file_path, split_column_index=3)

    import os
    os.remove(temp_file_path)
    
#Tests the end-to-end functionality of the main script with sample data.
def test_main_basic_functionality(capsys, monkeypatch):
    csv_data = """Location,Amount,Paid By,Paid For
Denny's,62.36,P,"J,P,T,C,E"
Sato Ramen,128.74,P,"J,P,T,C,E"
In-N-Out,48.45,J,"J,P,T,C,E"
Croissant,8,E,J
T Shirt,26.54,E,J
Dumplings,20,J,E
"""
    temp_csv_file_path = make_temp_data_file(csv_data)

    config_data = {
        "split_column_index": 3,
        "payers": "P,J,T,C,E",
        "payees": "P,J,T,C,E"
    }
    temp_config_file_path = make_temp_config_file(config_data)

    # Act: Mock command-line arguments and run the main function.
    # We use monkeypatch to temporarily change sys.argv
    monkeypatch.setattr('sys.argv', ['script_name', '--input', temp_csv_file_path, '--config', temp_config_file_path])
    
    # Run the main function
    main()

    # Assert: Capture the output and check if it matches the expected result.
    captured = capsys.readouterr()
    expected_output = (
        "J owes P $ 28.53\n"
        "T owes P $ 38.22\n"
        "C owes P $ 38.22\n"
        "E owes P $ 38.22\n"
        "T owes J $ 9.69\n"
        "C owes J $ 9.69\n"
        "J owes E $ 4.85\n"
    )
    assert captured.out.strip() == expected_output.strip()

    # Clean up the temporary files
    os.remove(temp_csv_file_path)
    os.remove(temp_config_file_path)
    

#Tests the end-to-end functionality of the main script with sample data - simple version that can be calculated in your head.
# Bob pays $10 total for Joseph and Mike, thus Mike owes Bob 5
# Joseph pays $10 total for Bob and Mike, thus Mike also owes Joseph 5
def test_main_basic_functionality_simple(capsys, monkeypatch):
    csv_data = """Location,Amount,Paid By,Paid For
Place A,10,Bob,"Joseph,Mike"
Place B,10,Joseph,"Bob,Mike"
"""
    temp_csv_file_path = make_temp_data_file(csv_data)

    config_data = {
        "split_column_index": 3,
            "payers": "Bob,Joseph,Mike",
            "payees": "Bob,Joseph,Mike"
    }
    temp_config_file_path = make_temp_config_file(config_data)

    # Act: Mock command-line arguments and run the main function.
    # We use monkeypatch to temporarily change sys.argv
    monkeypatch.setattr('sys.argv', ['script_name', '--input', temp_csv_file_path, '--config', temp_config_file_path])
    
    # Run the main function
    main()

    # Assert: Capture the output and check if it matches the expected result.
    captured = capsys.readouterr()
    expected_output = (
        "Mike owes Bob $ 5.00\n"
        "Mike owes Joseph $ 5.00\n"
    )
    assert captured.out.strip() == expected_output.strip()

    # Clean up the temporary files
    os.remove(temp_csv_file_path)
    os.remove(temp_config_file_path)
    
    
#Tests a case where two people each cover a meal and it all cancels out
def test_main_basic_functionality_canceled(capsys, monkeypatch):
    csv_data = """Location,Amount,Paid By,Paid For
Place A,10,Bob,"Joseph"
Place B,10,Joseph,"Bob"
"""
    temp_csv_file_path = make_temp_data_file(csv_data)

    config_data = {
        "split_column_index": 3,
            "payers": "Bob,Joseph",
            "payees": "Bob,Joseph"
    }
    temp_config_file_path = make_temp_config_file(config_data)
    
    # Act: Mock command-line arguments and run the main function.
    # We use monkeypatch to temporarily change sys.argv
    monkeypatch.setattr('sys.argv', ['script_name', '--input', temp_csv_file_path, '--config', temp_config_file_path])
    
    # Run the main function
    main()

    # Assert: Capture the output and check if it matches the expected result.
    captured = capsys.readouterr()
    expected_output = ("")
    assert captured.out.strip() == expected_output.strip()

    # Clean up the temporary files
    os.remove(temp_csv_file_path)
    os.remove(temp_config_file_path)
    
#Tests that the script exits gracefully if the input file is not found.
def test_main_nonexistent_input_file(capsys, monkeypatch):

    config_data = {
        "split_column_index": 3,
            "payers": "Bob,Joseph",
            "payees": "Bob,Joseph"
    }
    temp_config_file_path = make_temp_config_file(config_data)
        
    # Arrange: Mock the command-line arguments with a non-existent file path
    non_existent_path = "non_existent_file.csv"
    monkeypatch.setattr('sys.argv', ['script_name', '--input', non_existent_path, '--config', temp_config_file_path])

    # Act: Run the main function
    main()

    # Assert: Capture the output and check for the "not found" error message
    captured = capsys.readouterr()
    assert "Error: The file 'non_existent_file.csv' was not found." in captured.out    
    
#Tests that the script exits gracefully if the input file is not found.
def test_main_nonexistent_conf_file(capsys, monkeypatch):
    csv_data = """Location,Amount,Paid By,Paid For
Place A,10,Bob,"Joseph"
Place B,10,Joseph,"Bob"
"""
    temp_csv_file_path = make_temp_data_file(csv_data)
        
    # Arrange: Mock the command-line arguments with a non-existent file path
    non_existent_path = "non_existent_file.json"
    monkeypatch.setattr('sys.argv', ['script_name', '--input', temp_csv_file_path, '--config', non_existent_path])

    # Act: Run the main function
    main()

    # Assert: Capture the output and check for the "not found" error message
    captured = capsys.readouterr()
    assert "Error: The configuration file 'non_existent_file.json' was not found." in captured.out
        
#Tests that the script handles an invalid JSON config file.
def test_main_invalid_config_file(capsys, monkeypatch):
    # Arrange: Create a temporary file with invalid JSON content
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as temp_config_file:
        temp_config_file.write("this is not valid json")
        temp_config_file_path = temp_config_file.name

    # Mock command-line arguments to use the invalid config file.
    monkeypatch.setattr('sys.argv', ['script_name', '--input', 'dummy.csv', '--config', temp_config_file_path])

    # Act: Run the main function
    main()

    # Assert: Capture the output and check for the error message
    captured = capsys.readouterr()
    assert "Error: The configuration file is not valid JSON." in captured.out

    # Clean up the temporary file
    os.remove(temp_config_file_path)