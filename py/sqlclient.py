#!/usr/bin/python3
import sys
import time
import json
from constants import *
from crate.client import connect

def count_rows(cursor, devaddr):
    cursor.execute(f"SELECT count(*) FROM {TABLE_SENSORS} WHERE devaddr = {devaddr}")
    return cursor.fetchall()

def main(a):
    connection = connect(NODEURL)
    cursor = connection.cursor()

    devaddr = str(a[1])
    tmst_actual = int(a[2])
    tmst_last = int(a[11])
    tmst_dif = int(a[12])
    count = int(a[13])
    

    print("____SQL_client")
    print(devaddr)
    #print(tmst_actual)

    time_dif = 0
    if count == 1:
        tmst_dif = tmst_last
    elif count == 2:
        time.sleep(2)
        cursor.execute(f"DELETE FROM {TABLE_SENSORS} WHERE tmst = {tmst_last}")

    message = json.dumps({"latitude": float(a[3]),
                "longitude": float(a[4]),
                "sf": int(a[5]),
                "bw": int(a[6]),
                "lsnr": float(a[7]),
                "rssi": float(a[8]),
                "lenpayload": int(a[9]),
                "payload": str(a[10]),
                "tmst": tmst_actual,
                "tmst_dif":tmst_dif,
                "flag": 0
        })
    #print(message)
    cursor.execute("INSERT INTO sensors (devaddr, tmst, message) VALUES (?,?,?)", (devaddr, tmst_actual, message))
    connection.close()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        pass
    else:
        main(sys.argv)
