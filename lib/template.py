def replace_line(line, data):
    for d in data:
        if d in line:
            return line.replace("{{%s}}" % d, data[d])

    print(line)
    return line


def render_template(filename, data):
    ret = []
    f = open(filename, 'r')
    lines = f.read().split("\n")
    for line in lines:
        if line is None:
            continue

        if "{{" in line:
            line = replace_line(line, data)

        ret.append(line)

    f.close()
    return "\n".join(ret)
