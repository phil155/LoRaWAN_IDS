import json
import socket

DATASET = '2_dev_3.log'
NODEURL = "http://localhost:4200/"
HOST, PORT = "172.20.10.10", 9999


dfile = open(DATASET, 'r')
data = dfile.readlines()

#connection = connect(NODEURL)
#cursor = connection.cursor()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP


NUM_PACKETS = 1
count = 0
for line in data:
    count +=1
    #print(line)
    json_line = json.loads(line)
 
    payload = json_line["payload "]
    lenpayload = len(payload)

    message = json.dumps({"rxpk":[
        {
                "time": json_line["time"],
                "latitute": json_line["latitute"],
                "longitude": json_line["longitude"],
                "chan": json_line["chan"],
                "datr": json_line["datr"],
                "lsnr": json_line["lsnr"],
                "rssi": json_line["rssi"],
                "data": payload
        }]})
    #cursor.execute("INSERT INTO sensors (devaddr, tmst, message) VALUES (?,?,?)", (devaddr, tmst, message))
    #print(message)
    sock.sendto(bytes(message, "utf-8"), (HOST, PORT))

    if count == NUM_PACKETS:
        break

sock.close()
dfile.close()