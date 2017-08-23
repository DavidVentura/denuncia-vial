import os
def replace_line(line, data):
    for d in data:
        if d in line:
            return line.replace("{{%s}}" % d, data[d])

    print(line)
    return line


def render_template(filename, data):
    ret = []
    dname = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(dname, filename)
    print("Opening %s" % target)
    f = open(target, 'r')
    print("Open!")
    lines = f.read().split("\n")
    for line in lines:
        if line is None:
            continue

        if "{{" in line:
            line = replace_line(line, data)

        ret.append(line)

    f.close()
    return "\n".join(ret)
