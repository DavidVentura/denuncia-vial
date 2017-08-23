from base64 import b64encode
from wand.image import Image
from datetime import datetime
import exifread


def filename_to_timestamp(fname):
    f = open(fname, 'rb')
    tags = exifread.process_file(f, details=False)
    dt_tags = ["Image DateTime", "EXIF DateTimeOriginal", "DateTime"]

    times = set()
    for d in dt_tags:
        if d in tags:
            times.add(datetime.strptime(str(tags[d]), '%Y:%m:%d %H:%M:%S'))

    return (list(times)[0]).timestamp()


def orientation_to_rotation(orientation):
    rotation = 0

    if orientation == 6:
        rotation = 90
    if orientation == 3:
        rotation = 180
    if orientation == 8:
        rotation = 270

    return rotation


def fix_and_encode(fname):
    ret = ""
    tag = "exif:Orientation"
    with Image(filename=fname) as i:
        orientation = [v for k, v in i.metadata.items() if k == tag][0]
        i.rotate(orientation_to_rotation(orientation))
        i.compression_quality = 15
        ret = i.make_blob()

    return b64encode(ret).decode('ascii')
