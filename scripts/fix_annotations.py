import csv

row_indices = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

with open("../screenA/idr0143-screenA-annotation.csv") as infile:
    with open("../screenA/idr0143-screenA-annotation.csv", "w") as outfile:
        reader = csv.DictReader(infile, delimiter=",")
        writer = csv.DictWriter(outfile, delimiter=",", fieldnames=reader.fieldnames)
        writer.writeheader()
        for i, row in enumerate(reader):
            r = int(row["Well"][1:3])-1
            c = int(row["Well"][4:6])
            row["Well"] = f"{row_indices[r]}{c}"
            writer.writerow(row)
