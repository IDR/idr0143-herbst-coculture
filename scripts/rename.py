import omero
from omero.cli import cli_login
from omero.gateway import BlitzGateway

with cli_login() as c:
    conn = omero.gateway.BlitzGateway(client_obj=c.get_client())
    screen = conn.getObject('Screen', attributes={'name': "idr0143-herbst-coculture/screenA"})
    for plate in screen.listChildren():
        name = plate.getName()
        if "_Day3" in name:
            plate.setName(name.replace("_Day3", ""))
            conn.getUpdateService().saveAndReturnObject(plate._obj)
