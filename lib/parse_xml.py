import xmltodict
valid_ret_keys = ['faultstring']


def traverse(odict):
    ret = {}
    for key in odict.keys():
        if key.startswith('soap'):
            # recurse
            ret.update(traverse(odict[key]))

        if key in valid_ret_keys:
            ret[key] = odict[key]

    return ret


def xml_to_dict(xml):
    d = xmltodict.parse(xml)
    return traverse(d)


if __name__ == '__main__':
    xml = '''<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><soap:Fault><faultcode>soap:Server</faultcode><faultstring>PREGUNTA: Ingresá la patentente del vehículo (Por ej, ABC123 o AB123CD)|||RESPUESTA: asdasdasd|||ERROR: La longitud del texto ingresado debe contener entre 6 y 7 caracteres.</faultstring><detail/></soap:Fault></soap:Body></soap:Envelope>'''
    print(xml_to_dict(xml))
