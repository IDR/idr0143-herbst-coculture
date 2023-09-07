import csv
import argparse
import re

row_indices = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

DESC = '''
Fixes well names from format like r01c01 to format needed by metadata plugin A1.
The new well names will be added to a new column '<NAME> 2'.
'''

parser = argparse.ArgumentParser(description=DESC)
parser.add_argument("file", help="Path to the annotation.csv file")
parser.add_argument("-n", "--name", default="Well", help="Name of the well column (default: Well)")
parser.add_argument("-r", "--regex", default="r(?P<row>\d+)c(?P<col>\d+)", help="Regex of the well name (default: r(?P<row>\d+)c(?P<col>\d+))")
parser.add_argument("--rowzero", action="store_true", default=False, help="Row indexes are zero based (default: False)")
parser.add_argument("--colzero", action="store_true", default=False, help="Column indexes are zero based (default: False)")

args = parser.parse_args()

new_name = f"{args.name} 2"

pat = re.compile(args.regex)


buffer = []
header = None
with open(args.file) as infile:
    reader = csv.DictReader(infile, delimiter=",")
    header = reader.fieldnames
    header.insert(header.index(args.name)+1, new_name)
    for i, row in enumerate(reader):
        m = pat.match(row[args.name])
        if m:
            r = int(m.groupdict()["row"])
            if not args.rowzero:
                r -= 1
            c = int(m.groupdict()["col"])
            if args.colzero:
                c += 1
            row[new_name] = f"{row_indices[r]}{c}"
            buffer.append(row)
        else:
            print(f"{args.regex} doesn't match for {row[args.name]} (line {i})")

with open(args.file, "w") as outfile:
        writer = csv.DictWriter(outfile, delimiter=",", fieldnames=header)
        writer.writeheader()
        for row in buffer:
            writer.writerow(row)
