import omero.cli
import re

"""
There has been a problem with the companion file for 180213_Plate1_MIP:
Images were assigned to the wrong wells (but still had the correct row/col/field
in their name). This is just a script which checks one image for each well if
it is in the correct well, just to check if other companions had similar issues.
"""

with omero.cli.cli_login() as c:
    conn = omero.gateway.BlitzGateway(client_obj=c.get_client())

    pattern = re.compile(r".+\[(?P<row>\d\d)\|(?P<col>\d\d)\|(?P<field>\d\d)\]");

    status = {}

    screen = conn.getObject("Screen", attributes={'id': 3255})
    for plate in screen.listChildren():
        name = plate.getName()
        if "_MIP" in name:
            print(f"Checking {name} {plate.getId()} ...")
            if name not in status:
                status[name] = True
            for well in plate.listChildren():
                for ws in well.listChildren():
                    img_name = ws.getImage().getName()
                    m = pattern.match(img_name)
                    er = int(m['row'])
                    ec = int(m['col'])
                    ar = well.getRow()+1
                    ac = well.getColumn()+1
                    print(f"{img_name} - well row: {ar} , well col: {ac} - ", end="")
                    if er == ar and ec == ac:
                        print("OK")
                    else:
                        print("ERROR!!")
                        status[name] = False
                    break

print("Passed:")
for plate, status in status.items():
    print(f"{plate} - {status}")
