from datetime import time
from time import sleep
import json
import dateutil.parser as dp
from crate.client import connect

def isototmst(t):
    parsed_t = dp.parse(t)
    return int(parsed_t.timestamp()*1000)

def get_sf(s):
    return s[s.find("F")+1:s.find("B")]

def get_bw(s):
    return s[s.find("W")+1:]

NODEURL = "http://localhost:4200/"
#DATASET = 'dataset_1&2_original.log'
DATASET = 'dataset_3_original.log'
#DATASET = 'dataset_intrusion.log'
#TABLE = "sensors"
#TABLE = 'intrusions'
TABLE = 'sensors_2'

dfile = open(DATASET, 'r')
data = dfile.readlines()

#wfile = open("out.log", 'w')

connection = connect(NODEURL)
cursor = connection.cursor()

last = 0

count = 1
for line in data:

    json_line = json.loads(line)
    devaddr = json_line["devaddr"]
    tmst = isototmst(json_line["time"])
    datr = json_line["datr"]
    sf = get_sf(datr)
    bw = get_bw(datr)
    payload = json_line["payload"]
    lenpayload = len(payload)
    tmst_dif = 0

    if count == 1:
        last = tmst
    elif count == 2:
        sleep(2)
        cursor.execute(f"DELETE FROM {TABLE} WHERE tmst = {last}")
        atual = tmst

        tmst_dif = atual - last
        last = atual
    else:
        atual = tmst

        tmst_dif = atual - last
        last = atual

    message = json.dumps({
                "tmst": tmst,
                "tmst_dif": tmst_dif,
                "latitude": json_line["latitude"],
                "longitude": json_line["longitude"],
                "sf": sf,
                "bw": bw,
                "lsnr": json_line["lsnr"],
                "rssi": json_line["rssi"],
                "lenpayload": lenpayload,
                "payload": payload,
                "flag": json_line["flag"]
        })
    cursor.execute(f"INSERT INTO {TABLE} (devaddr, tmst, message) VALUES (?,?,?)", (devaddr, tmst, message))
    #wfile.write(f"{message}\n")
    count += 1

connection.close()
dfile.close()
#wfile.close()