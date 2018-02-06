##
# crux data manipulation
# @author Patrick Kage

import io
import csv

def reorder_csv(tablestr, headers):
    """Re-order columns in tabular data

    :param tablestr: a string of tabular data
    :param headers: new header arrangement
    :returns: a new string
    """

    # based on https://stackoverflow.com/questions/33001490/python-re-ordering-columns-in-a-csv
    # prepare IO streams
    inp = io.StringIO(tablestr)
    out = io.StringIO()

    # output dict needs a list for new column ordering
    writer = csv.DictWriter(out, fieldnames=headers)
    # reorder the header first
    writer.writeheader()
    for row in csv.DictReader(inp):
        # writes the reordered rows to the new file
        writer.writerow(row)

    return out.getvalue()

