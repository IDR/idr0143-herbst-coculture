import xml.etree.ElementTree as ET
import re
import sys
import omero
from omero.cli import cli_login
from omero.gateway import BlitzGateway
from omero.rtypes import (
    rdouble,
    rint,
    rstring
)

"""
Creates ROIs from the ObjectList_.*.xml files. Just call it with the
xml file as first and only argument.

E.g. /uod/idr/filesets/idr0143-herbst-coculture/20220822-ftp/Screen_180508_Plate4_Day3__2018-05-11T12_51_03-Measurement 1/Evaluation2/ObjectList_00000476.xml

They are in subfolders called "Evaluation.*", but not all plates seem to have them.
"""

TABLE_NAME = "Population - CLL cell nuclei"
NS = {'n': 'http://www.perkinelmer.com/Acapella/AcapellaV1.xsd'}


def create_rect(x, y, w, h, text=None):
    rect = omero.model.RectangleI()
    rect.x = rdouble(x)
    rect.y = rdouble(y)
    rect.width = rdouble(w)
    rect.height = rdouble(h)
    if text:
        rect.textValue = rstring(text)
    rect.theZ = rint(0)
    rect.theT = rint(0)
    return rect


def create_point(x, y, text=None):
    p = omero.model.PointI();
    p.x = rdouble(x)
    p.y = rdouble(y)
    if text:
        p.textValue = rstring(text)
    p.theZ = rint(0)
    p.theT = rint(0)
    return p


def create_roi(img, p_x, p_y, x, y, w, h, text):
    roi = omero.model.RoiI()
    roi.setImage(img._obj)
    roi.addShape(create_point(p_x, p_y, text))
    roi.addShape(create_rect(x, y, w, h))
    return roi


def getImage(plate, row, col, field):
    for well in plate.listChildren():
        if well.row == row and well.column == col:
            return well.getImage(field)


def process_file(file, conn):
    root = ET.parse(file).getroot()
    plate_name = root.findtext("n:PlateName", namespaces=NS)

    plate_name = re.sub(r"_Day.+$", "", plate_name)
    print(f"Plate: {plate_name}")
    plate = conn.getObject('Plate', attributes={'name': plate_name})
    print(plate)

    for rt_el in root.findall("n:ResultTable", NS):
        type = rt_el.findtext("n:Name", namespaces=NS)
        if type == TABLE_NAME:
            row = int(rt_el.get("Row"))
            col = int(rt_el.get("Col"))
            field = int(rt_el.get("FieldID"))
            print(f"Row: {row}, Col: {col}, Field: {field}")
            image = getImage(plate, row-1, col-1, field-1)
            if image:
                for t_el in rt_el.findall("n:table/n:tr", NS):
                    n = t_el.get("n")
                    p_x = int(t_el.get("x"))
                    p_y = int(t_el.get("y"))
                    bb = t_el.get("BB")
                    bb = re.sub(r"\[|\]", "", bb)
                    bb = bb.split(",")
                    x = int(bb[0])
                    y = int(bb[1])
                    w = int(bb[2])
                    h = int(bb[3])
                    print(f"Object: {n}, Point: X: {p_x}, Y: {p_y}")
                    print(f"Box: x: {x}, Y: {y}, w: {w}, h: {h}")
                    roi = create_roi(image, p_x, p_y, x, y, w, h, n)
                    roi = conn.getUpdateService().saveAndReturnObject(roi, conn.SERVICE_OPTS)
                    if roi:
                        print("ROI saved.")
                    else:
                        print("ROI saving failed.")
            else:
                print("Image not found")



object_file = sys.argv[1] # "ObjectList_00000169.xml"
with cli_login() as c:
    conn = omero.gateway.BlitzGateway(client_obj=c.get_client())
    process_file(object_file, conn)
