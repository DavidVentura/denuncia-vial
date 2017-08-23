#!/usr/bin/env python3
import json
import requests
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime
from image import fix_and_encode, filename_to_timestamp
from template import render_template
from parse_xml import xml_to_dict

valid_plate = re.compile(r'^([a-z]{3}[0-9]{3})|([a-z]{2}[0-9]{3}[a-z]{2})$',
                         re.I)
token_url = "http://suaci-gcba.buenosaires.gob.ar/suaci/services/operadorCiudadano?op=obtenerToken"
submit_url = 'http://suaci-gcba.buenosaires.gob.ar/suaci/services/suaciWebServices?op=crearOReiterarContacto'


def get_token(data):
    offline_testing = True
    if not valid_plate.match(data["PATENTE"]):
        print("Patente invalida")
        # IMPORANT: these idiots only check for the string length to be {6,7}.
        return None
    token_body = render_template("templates/get_token.xml", data)
    if offline_testing:
        response = open('templates/response_token.xml', 'r')
    else:
        r = requests.post(token_url, data=token_body)
        response = r.text
    parsed = BeautifulSoup(response, "xml")
    return parsed.find("obtenerToken").text.strip()


def post_data(template):
    r = requests.post(submit_url, data=template)
    resp = r.text
    print(resp)
    print(xml_to_dict(resp))


def populate_data(user_data, filename1, filename2):
    ts = max(filename_to_timestamp(filename1),
             filename_to_timestamp(filename2))
    date = datetime.fromtimestamp(ts)

    RET_DATA = user_data.copy()

    RET_DATA["FILE1"] = fix_and_encode(filename1)
    RET_DATA["FILE2"] = fix_and_encode(filename2)
    RET_DATA["FECHA"] = date.strftime("%d/%m/%Y")
    RET_DATA["HORA"] = date.strftime("%H:%M:%S")

    return RET_DATA


def complaint(obs, plate, filename1, filename2):
    user_data = json.loads(open('data.json').read())

    if not os.path.exists(filename1) or not os.path.exists(filename2):
        print("invalid filenames")
        return

    user_data["OBSERVACION"] = obs
    user_data["PATENTE"] = plate
    token = get_token(user_data)

    if token is None:
        print("Invalid token")
        return

    user_data["TOKEN"] = token

    data = populate_data(user_data, filename1, filename2)
    template = render_template("templates/request.xml", data)
    post_data(template)
