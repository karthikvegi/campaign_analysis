#-------------------------------------------------------------------------------
# Author: Karthik Vegi
# Email: karthikvegi@outlook.com
# Python Version: 3.6
#-------------------------------------------------------------------------------
import math
from datetime import datetime

def write_to_destination(record, destination, delimiter):
    destination.write(delimiter.join(record) + "\n")

def empty_fields(fields):
    if any(map(lambda x: not x.strip(), fields)):
        return True

def malformed_field(field, ideal_length):
    if len(field) < ideal_length:
        return True

def invalid_date(field, format):
    try:
        datetime.strptime(field, format)
    except Exception as e:
        return True

def print_summary_statistics(stats):
    print("***** Data Pipeline Complete *****")
    print("Records Processed: ", stats[0])
    print("Records Skipped: ", stats[1])

def compute_percentile(donations, percentile):
    # Nearest-rank method
    donations.sort()
    idx = math.ceil(percentile * 0.01 * len(donations))
    return donations[idx-1]