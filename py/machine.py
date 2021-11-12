#!/usr/bin/python3

import sys
import io
import pickle
import base64
import time
from constants import *
from crate.client import connect

import matplotlib.pyplot as plt
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix

##################################################
################ PREDICT MODEL ###################
##################################################

def encode_IO(data):
    out = base64.b64encode(pickle.dumps(data))
    out.decode('utf-8')
    return io.BytesIO(out)

def encode(data):
    out = base64.b64encode(pickle.dumps(data))
    return out.decode('utf-8')

def decode(data):
    out = base64.b64decode(data) 
    return pickle.loads(out)

def decision(pred):
    if 0 < pred < 0.5:
        return f"DUVIDAS {pred}"
    elif pred == 0:
        return "NORMAL"
    else:
        return "INTRUSION"

def get_model(cursor, devaddr, blob_container):
    cursor.execute(f"SELECT model FROM models WHERE devaddr = '{devaddr}'")
    res = cursor.fetchone()
    key = res[0]["model"]
    scl = res[0]["scaler"]

    blob_content = b''
    index = 0 
    for chunk in blob_container.get(key):
        index +=1
        blob_content += chunk

    model = decode(blob_content)
    scaler = decode(scl)

    return model, scaler

def run_predict(model, scaler, X):
    X = [X]
    X_np = np.array(X)
    X_test = scaler.transform(X_np)
    #res = model.predict(X_test)
    res = model.predict_proba(X_test)[0,1]
    return res

def insert_doubts(cursor, tmst, prob):
    cursor.execute(f"INSERT INTO {TABLE_DOUBTS} SELECT * FROM {TABLE_SENSORS} WHERE message['tmst'] = {tmst};")
    time.sleep(1)
    cursor.execute(f"UPDATE {TABLE_DOUBTS} SET message['flag'] = {prob*100} WHERE message['tmst'] = {tmst};")

def update_flag(cursor, tmst, flag):
    cursor.execute(f"UPDATE {TABLE_SENSORS} SET message['flag'] = {flag} WHERE tmst = {tmst}")

def fit_model(cursor, devaddr):
    print("fit")




def main(arg):
    connection = connect(NODEURL)
    cursor = connection.cursor()
    blob_container = connection.get_blob_container(BLOB)


    devaddr = str(arg[1])           #devaddr
    tmst_actual = int(arg[2])       #tmst

    packet =[]     
    packet.append(float(arg[3]))    #latitude
    packet.append(float(arg[4]))    #longitude
    packet.append(int(arg[5]))      #sf
    packet.append(int(arg[6]))      #bw
    packet.append(float(arg[7]))    #lsnr
    packet.append(float(arg[8]))    #rssi
    packet.append(int(arg[9]))      #lenpayload
    packet.append(int(arg[12]))     #tmst_dif

    #arg = devaddr.." "..tmst_actual.." "..latitude.." "..longitude.." "..sf.." "..bw.." "..lsnr.." "..rssi.." "..lenpayload.." "..data.." "..tmst_last.." "..tmst_dif.." "..count

    print("____Machine")
    print(f"{devaddr} tmst: {tmst_actual}")


    model, scaler = get_model(cursor, devaddr, blob_container)

    #print(packet)
    pred = run_predict(model, scaler, packet)
    if pred == 0 :
        print(f"{bcolors.OKGREEN}NORMAL {bcolors.ENDC}")
    elif 0 < pred < 0.5:
        print(f"{bcolors.WARNING}DUVIDAS {bcolors.ENDC}")
        update_flag(cursor, tmst_actual, 2)                 #UPDATE FLAG TO VAL= 2 (DOUBTS)
        insert_doubts(cursor, tmst_actual, pred)            #INSERT DOUBTS FROM TABLE_SENSORS TO TABLE_DOUBTS
    else:
        print(f"{bcolors.FAIL}INTRUSION {bcolors.ENDC}")
        update_flag(cursor, tmst_actual, 1)                 #UPDATE ONLY FLAG TO VAL= 1 (INTRUSION)
        connection.close()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        pass
    else:
        main(sys.argv)
