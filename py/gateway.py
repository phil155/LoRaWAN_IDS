import socket
import json
import random
import time

def message(RSSI, PAYLOAD, TMST):
    m = {"rxpk":[
	{
		"time":"2013-03-31T16:21:17.528002Z",
		"latitude":51.2339973449707,
		"longitude":4.42610502243042,
		"tmst":int(TMST),
		"chan":2,
		"rfch":0,
		"freq":866.349812,
		"stat":1,
		"modu":"LORA",
		"datr":"SF7BW125",
		"codr":"4/6",
		"rssi":RSSI,
		"lsnr":5.1,
		"size":32,
		"data":PAYLOAD
	}
]}

    return m


HOST, PORT = "192.168.59.132", 9999
DEVICE = "F17DBE49"
TMST = time.time()
NUMMSG = 1

#RSSI = -88
#DEVICE = "AAAAAAAA"
#x = "40F17DBE4900020001954378762B11FF0D"
#y = "QK4TBCaAAAABb4ldmIEHFOMmgpU="

while NUMMSG:
	#print("Message: "+ str(NUMMSG))
	NUMMSG=NUMMSG-1
	
	RSSI = random.randint(-120,-100) #ALTERAR
	PAYLOAD = "40"+DEVICE+"00020001954378762B11FF0D"
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

	data = json.dumps(message(RSSI, PAYLOAD,TMST))
	sock.sendto(bytes(data, "utf-8"), (HOST, PORT))
	#time.sleep(0.1)






'''
TCP connection

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(data,encoding="utf-8"))

finally:
    sock.close()
'''