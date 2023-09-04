import re
import subprocess
from ome_model.experimental import Plate, Image, create_companion

# Create companion files for screenC

# 20221222-ftp/180213_Plate1/r08c08f01-ch1.tiff
#     ^.+/(?P<plate_name>.+)/r(?P<row>\D{2})c(?P<col>\D{2})f(?P<field>\D{2})-ch(?P<channel>\D{1}).tiff
pat = re.compile(r"^.+\/(?P<plate_name>.+)\/r(?P<row>\d{2})c(?P<col>\d{2})f(?P<field>\d{2})-ch(?P<channel>\d{1}).tiff")

file_list = '143_files.txt'
order = "XYCZT"
img_x = 2160
img_y = 2160
pix_type = "uint16"

channel_names = {"0": "HOECHST 33342", "1": "Lysosomal dye NIR", "2": "Calcein"}

files = {}
with open(file_list, 'r') as read:
    for line in read.readlines():
        line = line.strip()
        if pat.match(line):
            m = pat.match(line).groupdict()
            if m['plate_name'] not in files:
                files[m['plate_name']] = []
            files[m['plate_name']].append(line)

for plate_name, tifs in files.items():
    # Get total numbers
    n_rows = set()
    n_cols = set()
    n_fields = set()
    n_c = set()
    for i, file in enumerate(tifs):
        m = pat.match(file).groupdict()
        n_rows.add(m['row'])
        n_cols.add(int(m['col']))
        n_fields.add(int(m['field']))
        n_c.add(int(m['channel']))
    n_rows = len(n_rows)
    n_cols = len(n_cols)
    n_fields = len(n_fields)
    n_c = len(n_c)

    # assemble images (key: wellrow|wellcol|field)
    images = {}
    for file in tifs:
        m = pat.match(file).groupdict()
        key = f"{m['row']}|{m['col']}|{m['field']}"
        if not key in images:
            images[key] = Image(key, img_x, img_y, 1, n_c, 1, order=order, type=pix_type)
            for i in range(0, n_c):
                chn = str(i)
                if chn in channel_names:
                    chn = channel_names[chn]
                else:
                    print(f" channel name {i} not found ({plate_name})")
                images[key].add_channel(samplesPerPixel=1, name=f"{chn}")
        images[key].add_plane(c=int(m['channel'])-1, z=0, t=0)
        rel_path = re.sub(r"^.+-ftp\/", "", file)
        images[key].add_tiff(rel_path, c=int(m['channel'])-1, z=0, t=0, planeCount=1)

    # assemble plate
    plate = Plate(plate_name, n_rows, n_cols)
    wells = {}
    for well_pos, image in images.items():
        row = int(well_pos.split("|")[0])-1
        col = int(well_pos.split("|")[1])-1
        field = int(well_pos.split("|")[2])-1
        key = f"{row}|{col}"
        if not key in wells:
            wells[key] = plate.add_well(row, col)
        wells[key].add_wellsample(field, image)

    # write companion file
    companion_file = "{}.companion.ome".format(plate_name)
    create_companion(plates=[plate], out=companion_file)

    # Indent XML for readability
    proc = subprocess.Popen(
        ['xmllint', '--format', '-o', companion_file, companion_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    (output, error_output) = proc.communicate()
