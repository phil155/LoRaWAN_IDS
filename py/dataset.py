import json
import base64

##################################################
###### TRANSFORM DATASET_raw TO DATASET_json #####
##################################################

FILE = "out.log"

DATASET = 'dataset/rxpk_20200603.log'
DEVADDR1 = "A01063D9"
DEVADDR2 = "0000BF53"
LAT = 38.72380635165497
LONG = -9.16139236365605

def to_hex(data):
    return base64.b64decode(data).hex().upper()

dfile = open(DATASET, 'r')
data = dfile.readlines()

f0 = open(FILE, "w")

out = []
for line in data:
    if '"totalrxpk":1' in line and (not '"jver"'in line):
        line = line.replace("[","")
        line = line.replace("]","")
        json_line = json.loads(line)
        try:
                devaddr = json_line["rxpk"]["DevAddr"]
                if devaddr == DEVADDR2:
                        #devaddr == DEVADDR1 or 
                        #out.append(json_line)
                        #print(devaddr)
                        latitude = LAT
                        longitude = LONG

                        message = json.dumps({
                                "devaddr": DEVADDR2,             ###FOI ALTERADO PARA QUE O DEV1 TENHA CONTEUDO DO DEV2
                                "time": json_line["rxpk"]["time"],
                                "latitude": LAT,
                                "longitude": LONG,
                                "datr": json_line["rxpk"]["datr"],
                                "lsnr": json_line["rxpk"]["lsnr"],
                                "rssi": json_line["rxpk"]["rssi"],
                                "payload": to_hex(json_line["rxpk"]["data"]),
                                "flag": 0
                        })
                        f0.write(message + "\n")
        except:
                continue

dfile.close()
f0.close()