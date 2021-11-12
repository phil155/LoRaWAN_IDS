#!/usr/bin/python3
from constants import *
from crate.client import connect
from threading import Thread
import numpy as np
import sys
import pickle
import base64
import io
import time
import json

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.metrics import average_precision_score

##################################################
################# TRAIN MODEL ####################
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

def check_if_dev_exist(cursor, devaddr):
    cursor.execute(f"SELECT devaddr FROM models WHERE devaddr = '{devaddr}'")
    out = cursor.fetchall()
    if not out:
        return False
    else:
        return True

def test_model(X, Y, result, index):

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3)
    #, random_state=42

    X_t = X_test    #PACOTE ORIGINAL

    X_train = np.array(X_train)
    Y_train = np.array(Y_train)
    Y_test = np.array(Y_test)

    scaler = StandardScaler()
    scaler.fit(X_train)

    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)


    classifier = KNeighborsClassifier(n_neighbors=5)
    classifier.fit(X_train, Y_train)

    y_pred = classifier.predict(X_test)
    y_pred_prob = classifier.predict_proba(X_test)
    average_precision = average_precision_score(Y_test, y_pred)

    result[index] = [average_precision, classifier, scaler, X_train, X_test, Y_train, Y_test, y_pred, y_pred_prob,  X_t]

def main(arg):
    devaddr = str(arg[1])

    connection = connect(NODEURL)
    cursor = connection.cursor()
    blob_container = connection.get_blob_container(BLOB)

    cursor.execute(f"SELECT message FROM {TABLE_SENSORS} WHERE devaddr = '{devaddr}' ORDER BY tmst")
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
        

    threads = [None] * NUM_THREADS
    results = [None] * NUM_THREADS
    for i in range(len(threads)):
        threads[i] = Thread(target=test_model, args=(X, Y, results, i))
        threads[i].start()

    for i in range(len(threads)):
        threads[i].join()

    average = [ ]
    for i in range(len(results)):
        average.append(results[i][0])

    average_max_index = average.index(max(average))

    average_precision = results[average_max_index][0]
    classifier = results[average_max_index][1]
    scaler = results[average_max_index][2]
    X_train = results[average_max_index][3]
    X_test = results[average_max_index][4]
    Y_train = results[average_max_index][5]
    Y_test = results[average_max_index][6]
    y_pred = results[average_max_index][7]
    y_pred_prob = results[average_max_index][8]
    X_t = results[average_max_index][9]

    c = encode_IO(classifier)
    s = encode(scaler)

    if check_if_dev_exist(cursor, devaddr): #IN CASE OF UPDATE
        print("__MODEL EXIST")
        cursor.execute(f"SELECT model FROM models WHERE devaddr = '{devaddr}'")
        res = cursor.fetchone()
        key = res[0]["model"]
        blob_container.delete(key)          #DELETE THE OLD BLOB FILE

        key = blob_container.put(c)
        arg = json.dumps({ "model": key , "scaler": s })
        cursor.execute(f"UPDATE models SET model = '{arg}' WHERE devaddr = '{devaddr}'")
        #pass
    else:                                   #IN CASE OF NEW
        print("__CREATE NEW MODEL")
        key = blob_container.put(c)
        cursor.execute("INSERT INTO models (devaddr, model) VALUES (?,?)", (devaddr, { "model": key , "scaler": s }))

    scr = classifier.score(X_test, Y_test)

    print("AVERAGE PRECISION")
    print(average_precision)
    #print("SCORE")
    #print(scr)

    #print("F1 SCORE macro")
    #print(f1_score(Y_test, y_pred, average='macro'))
    #print("F1 SCORE micro")
    #print(f1_score(Y_test, y_pred, average='micro'))
    #print("F1 SCORE weighted")
    #print(f1_score(Y_test, y_pred, average='weighted'))

    #create_table()

    connection.close()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        pass
    else:
        main(sys.argv)