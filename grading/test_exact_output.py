import os
import pytest
import pandas as pd
import re
import requests
from cryptography.fernet import Fernet

DECIMAL_PLACES = 5
N_MISMATCHES = 5


def test_exact_output(answer_path, files, cols):

    filelist = [s.strip() for s in files.replace(
        "[", "").replace("]", "").split(",")]

    try:
        response = requests.get(answer_path)
        if response.status_code == 200:
            file_key = response.text
    except:
        assert False, "Issue connecting to answer key."

    fernet = Fernet(file_key)

    # Logic to handle reading from CSV or reading from sas7bdat:
    csvs = []
    sass = []
    for fl in filelist:
        if os.path.exists(f"output/{fl}.sas7bdat"):
            sass.append(fl)
        elif os.path.exists(f"output/{fl}.csv"):
            csvs.append(fl)

    sas_answer_paths = [
        f"grading/encrypted/{f}.sas7bdat_encrypted" for f in sass
    ]

    csv_answer_paths = [
        f"grading/encrypted/{f}.csv_encrypted" for f in csvs
    ]

    answer_paths = sas_answer_paths + csv_answer_paths
    student_paths = [
        f"output/{f}.sas7bdat" for f in sass] + [f"output/{f}.csv" for f in csvs]

    # TODO: this logic is flawed when filelist is more than 1 file long (lists could be different)
    for i, ans in enumerate(filelist):

        assert os.path.exists(
            answer_paths[i]), f"Answer path {answer_paths[i]} does not exist. This is an autograder issue."

        with open(answer_paths[i], 'rb') as enc_file:
            encrypted = enc_file.read()

        decrypted = fernet.decrypt(encrypted)

        assert os.path.exists(
            student_paths[i]), f"Dataset {ans} does not exist. Does the sas7bdat dataset exist in the output folder?"

        if answer_paths[i].endswith(".sas7bdat_encrypted"):
            with open("temp_sas.sas7bdat", 'wb') as tempfile:
                tempfile.write(decrypted)
            answer_key = pd.read_sas(
                "temp_sas.sas7bdat", format='sas7bdat').round(DECIMAL_PLACES)
            os.remove("temp_sas.sas7bdat")
            answer_student = pd.read_sas(
                student_paths[i], format='sas7bdat').round(DECIMAL_PLACES)
            print(f"##########\nReading {ans} as sas7bdat\n##########")

        elif answer_paths[i].endswith(".csv_encrypted"):
            with open("temp.csv", 'wb') as tempfile:
                tempfile.write(decrypted)
            answer_key = pd.read_csv("temp.csv").round(DECIMAL_PLACES)
            os.remove("temp.csv")
            answer_student = pd.read_csv(
                student_paths[i]).round(DECIMAL_PLACES)
            print(f"##########\nReading {ans} as csv\n##########")
        else:
            assert False, f"Answer path {answer_paths[i]} is an invalid format. This is an autograder issue."

        # Finally, check the answers.
        # First, check that all the columns are present.
        # Alteration 2023-09-19: case insensitive input needed.
        # Alteration 2023-11-19: added columns to check
        if cols is None:
            cols_to_check = answer_key.columns.str.lower()
        else:
            cols_to_check = [s.strip() for s in cols.replace(
                "[", "").replace("]", "").split(",")]

        answer_student_columns = set(answer_student.columns.str.lower())
        assert all(
            col in answer_student_columns for col in cols_to_check), f"Not all columns are present in {ans}: {set(cols_to_check) - answer_student_columns}."

        # Reassign column names to get around capitalization issues.
        answer_key.columns = answer_key.columns.str.lower()
        answer_key_to_check = answer_key[cols_to_check]

        answer_student.columns = answer_student.columns.str.lower()

        # Subset to the relevant columns
        answer_student_to_check = answer_student[answer_key_to_check.columns]

        # Find where errors exist, and identify the rows and columns of interest.
        row_matches = answer_key_to_check.isin(answer_student_to_check)
        mismatched_cols = ~row_matches.all(axis=0)
        mismatched_rows = ~row_matches.all(axis=1)

        # Subset for better printing of exactly where the issues arise.
        expected_answer = answer_key_to_check.loc[mismatched_rows,
                                                  mismatched_cols]
        mismatched_student = answer_student_to_check.loc[mismatched_rows,
                                                         mismatched_cols]

        result = answer_key[~row_matches.all(axis=1)]

        assert result.empty, f"Records were miscoded in {ans}. The first {min(N_MISMATCHES, len(mismatched_student))} mismatches:\n\nYour answer:\n{mismatched_student[0:min(N_MISMATCHES, len(mismatched_student))]}\n\nExpected answer:\n{expected_answer[0:min(N_MISMATCHES, len(mismatched_student))]}\n\n"
