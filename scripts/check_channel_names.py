import omero.cli
import re

"""
Just to check if the channel names are all the same for all plates
"""

with omero.cli.cli_login() as c:
    conn = omero.gateway.BlitzGateway(client_obj=c.get_client())

    channel_names = {}
    pattern = re.compile(r".+Plate\d{1,2}$");

    screen = conn.getObject("Screen", attributes={'id': 3255})
    for pl in screen.listChildren():
        if pattern.match(pl.getName()):
            for well in pl.listChildren():
                if well.getWellSample():
                    print(f"Checking {pl.getName()} / {well.row},{well.column}")
                    img = well.getImage(0)
                    for i, ch in enumerate(img.getChannels()):
                        key = str(i)
                        value = ch.getLabel()
                        if key in channel_names and channel_names[key] != value:
                            print(f"Not unique")
                        else:
                            channel_names[key] = value
                    break

    print(channel_names)



