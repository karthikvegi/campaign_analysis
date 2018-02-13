#-------------------------------------------------------------------------------
# Author: Karthik Vegi
# Email: karthikvegi@outlook.com
# Python Version: 3.6
#-------------------------------------------------------------------------------
import sys
import math
from utils import *
from collections import defaultdict

def clean_up():
    source.close()
    destination.close()
    percentile_source.close()

def valid_record(record):
    check_empty_fields = [record['transaction_dt'], record['zip_code'], record['donor'], record['recipient'], record['transaction_amt']]
    if record['other_id'].strip() == "" \
            and not empty_fields(check_empty_fields) \
            and not malformed_field(record['zip_code'], 5) \
            and not invalid_date(record['transaction_dt'], '%m%d%Y'):
        return True

def ingest_record(row):
    cols = row.split("|")
    record = {}
    # Create a dictionary with fields for easy access
    record['recipient'] = cols[0]
    record['donor'] = cols[7]
    record['zip_code'] = cols[10][:5]
    record['transaction_dt'] = cols[13]
    record['transaction_yr'] = cols[13][4:]
    record['transaction_amt'] = cols[14]
    record['other_id'] = cols[15]
    record['donor_id'] = record['donor'] + record['zip_code']
    record['recipient_id'] = record['recipient'] + record['zip_code'] + str(record['transaction_yr'])
    if valid_record(record):
        process_record(record)

def process_record(record):
    transaction_yr = int(record['transaction_yr'])
    transaction_amt = int(round(float(record['transaction_amt'])))
    # New Donor
    if record['donor_id'] not in donor_dict:
        donor_dict[record['donor_id']] = transaction_yr
    # update transaction_yr if you come across donation from a previous year
    elif transaction_yr < donor_dict[record['donor_id']]:
        donor_dict[record['donor_id']] = transaction_yr
    # Repeat Donor
    elif transaction_yr > donor_dict[record['donor_id']]:
        donation_dict[record['recipient_id']].append(transaction_amt)
        compute_stats(record)

def compute_stats(record):
    trans_cnt = len(donation_dict[record['recipient_id']])
    total_donation = sum(donation_dict[record['recipient_id']])
    pct = compute_percentile(donation_dict[record['recipient_id']], percentile)
    output = [record['recipient'], record['zip_code'], str(record['transaction_yr']), str(pct), str(total_donation), str(trans_cnt)]
    write_to_destination(output, destination, '|')

if __name__ == "__main__":
    try:
        if len(sys.argv) < 4:
            raise Exception("Missing args! Correct Usage: <program.py> <inp_file> <pct_file> <out_file>")
        source = open(sys.argv[1], "r")
        destination = open(sys.argv[3], "w")
        percentile_source = open(sys.argv[2], "r")
        percentile = float(percentile_source.read())
        if  percentile < 0 or percentile > 100:
            raise ValueError("Invalid Percentile: Percentile value should between 1 to 100")
    except Exception as e:
        print(e)
        sys.exit(1)
    # Data Structures
    donor_dict = {} # Key: donor_id | Value: transaction_yr
    donation_dict = defaultdict(list) # Key: recipient | Value: list of transactions
    for row in source.read().splitlines():
        ingest_record(row)

    clean_up()
