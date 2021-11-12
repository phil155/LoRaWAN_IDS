from crate.client import connect
import numpy as np
import sys
import pickle
import base64
import io
import time
import json

import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.metrics import average_precision_score

NODEURL = "http://localhost:4200/"
BLOB = "modeltable"
DEVADDR = '0000BF53'

#TABLE = "BF53_with_content_of_A010"
#TABLE = "intrusions"
TABLE = 'sensors_2'
#TABLE = "original"

DELETE = True

def decode(data):
    out = base64.b64decode(data) 
    return pickle.loads(out)

def insert_doubts(tmst, prob):
    cursor.execute(f"INSERT INTO doubts SELECT * FROM {TABLE} WHERE message['tmst'] = {tmst};")
    time.sleep(1)
    cursor.execute(f"UPDATE doubts SET message['flag'] = {prob*100} WHERE message['tmst'] = {tmst};")

def decision(pred, packet):
    if 0 < pred < 0.5:
        insert_doubts(int(packet[0]["tmst"]), pred)
        return f", DUVIDAS {pred}"
    elif pred == 0:
        return ", NORMAL"
    else:
        return ". INTRUSION"

def create_table ():
    FILE = "result_pred.txt"
    f0 = open(FILE, "w")
    f0.write(f"AVERAGE PRECISION = {average_precision} \n")
    f0.write("lat, long, sf, bw, lsnr, RSSI, len, tmst_dif, TESTE, PREDICT, PROB, DECISION \n")

    if DELETE:
        cursor.execute("DELETE FROM doubts")
        time.sleep(3)

    for i in range(len(X_test)):
        message = f'{X[i]} \t\t, {Y[i]} , {y_pred[i]} , {y_pred_prob[i]}\t'

        message = message + decision(y_pred_prob[i,1], p[i])

        f0.write(message + "\n")
    
    f0.close()

connection = connect(NODEURL)
cursor = connection.cursor()
blob_container = connection.get_blob_container(BLOB)

cursor.execute(f"SELECT message FROM {TABLE} WHERE devaddr = '{DEVADDR}' ORDER BY tmst")
p = cursor.fetchall()


X = []
Y = []
for i in range(len(p)):
    line = []
    line.append(float(p[i][0]["latitude"]))
    line.append(float(p[i][0]["longitude"]))
    line.append(int(p[i][0]["sf"]))
    line.append(int(p[i][0]["bw"]))
    line.append(float(p[i][0]["lsnr"]))
    line.append(float(p[i][0]["rssi"]))
    line.append(int(p[i][0]["lenpayload"]))
    line.append(int(p[i][0]["tmst_dif"]))
    X.append(line)
    Y.append(int(p[i][0]["flag"]))


cursor.execute(f"SELECT model FROM models WHERE devaddr = '{DEVADDR}'") #GET KEY OF MODEL
res = cursor.fetchone()
key = res[0]["model"]
scaler = decode(res[0]["scaler"])


blob_content = b''          #GET BLOB
index = 0 
for chunk in blob_container.get(key):
    index +=1
    blob_content += chunk

cls = decode(blob_content)
classifier = cls


X_test = np.array(X)
X_test = scaler.transform(X_test)

y_pred = classifier.predict(X_test)
y_pred_prob = classifier.predict_proba(X_test)

average_precision = average_precision_score(Y, y_pred)

create_table()

connection.close()