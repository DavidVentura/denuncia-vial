from base64 import b64encode
from wand.image import Image
from datetime import datetime
import exifread


def filename_to_timestamp(fname):
    print("open %s" % fname)
    f = open(fname, 'rb')
    print("open!!")
    dateformat = '%Y:%m:%d %H:%M:%S'
    tags = exifread.process_file(f, details=False)
    dt_tags = ["Image DateTime", "EXIF DateTimeOriginal", "DateTime"]

    times = set()
    for d in dt_tags:
        if d in tags:
            times.add(datetime.strptime(str(tags[d]), dateformat))

    l = list(times)
    if len(l) > 0:
        ret = l[0]
    else:
        ret = datetime.now()

    return ret.timestamp()


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
        orientations = [v for k, v in i.metadata.items() if k == tag]
        if len(orientations) > 0:
            orientation = orientations[0]
            i.rotate(orientation_to_rotation(orientation))

        i.compression_quality = 15
        ret = i.make_blob()

    return b64encode(ret).decode('ascii')
