from constants import *
import os
from crate.client import connect

from tkinter.constants import CENTER
import PySimpleGUI as sg
import dateutil.parser as dp
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import time

sg.change_look_and_feel('Dark') 
file_list_column = [
    [
        sg.Text("DEVADDR :   DATE            TIME     LAT               LON              SF   BW    LSNR    RSSI    LEN   TMST_DIF  (probability)", justification='left', font = ("bold")),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(90, 20),font = ("Arial, 13"), key="-LIST-"
        )
    ],
]
text_column = [
    [
        sg.Text(" ", key = '-TOTAL-', font = ("bold"), justification=CENTER, size=(35, 1))
    ],
    [
        sg.Text(" ", key = '-TEXTinits-')
    ],
    [
        sg.Text(size=(35, 24), key = '-TEXTOUT-')
    ]
]
button_column = [
    [
        sg.Button("GET doubts", key = '-BUTTON1-', size=(11,1)),
    ],
    [
        sg.Text(' ')
    ],
    [   
        sg.Button("GET metrics", key = '-BUTTON2-', size=(11,1)),
    ],
    [
        sg.Text(' ')
    ],
    [   
        sg.Button("SET intrusion", key = '-BUTTON3-', size=(11,1), button_color='orange'),
    ],
    [
        sg.Text(' ')
    ],
    [   
        sg.Button("Learning", key = '-BUTTON4-', size=(11,1), button_color='green'),
    ]
]
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(button_column),
    ]
]

layout2 = [
    [
        sg.Column(text_column),
    ]
]

font = ("Arial, 11")
location = (200,200)
location2 = (1435,200)
window = sg.Window(title="Intrusion Detection System", icon= SERVER_ICON,layout=layout, font=font, location=location)

def get_data(cursor):
    cursor.execute(f"SELECT message, devaddr, tmst FROM {TABLE_DOUBTS} ORDER BY tmst")
    p = cursor.fetchall()
    X = []
    tmst = []
    total = 0
    for i in range(len(p)):
        devaddr = str(p[i][1])
        t = p[i][2]
        time = str(datetime.utcfromtimestamp(t/1000))[0 : -3]

        latitude = float(p[i][0]["latitude"])
        longitude = float(p[i][0]["longitude"])
        sf = int(p[i][0]["sf"])
        bw = int(p[i][0]["bw"])
        lsnr = float(p[i][0]["lsnr"])
        rssi = float(p[i][0]["rssi"])
        lenpayload = int(p[i][0]["lenpayload"])
        tmst_dif = int(p[i][0]["tmst_dif"])

        prob = int(p[i][0]["flag"])

        line = f'{devaddr}: {time},  {latitude}, {longitude}, {sf}, {bw},  {lsnr},  {rssi}, {lenpayload}, {tmst_dif}  -> {prob}%'
        X.append(line)
        tmst.append(t)
        total +=1

    return X, tmst, total

def get_metrics(cursor, devaddr):
    cursor.execute(f"SELECT message FROM {TABLE_SENSORS} WHERE devaddr = '{devaddr}' AND message['flag'] = 0 ORDER BY tmst") #ONLY FLAG = 0
    p = cursor.fetchall()

    X = []
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

    dataset = pd.DataFrame(X)
    

    if len(dataset[0].unique()) == 1 and len(dataset[1].unique()) == 1:
        position = 'Unique!'
        lat = dataset[0][0]
        lon = dataset[1][0]
    else:
        position = 'NOT Unique!'
        lat = dataset[0].unique()
        lon = dataset[1].unique()

    sf_ = dataset[2].value_counts().to_string()
    bw_ = dataset[3].value_counts().to_string()
    len_ = dataset[6].value_counts().to_string()
    lsnr_= f"{dataset[4].min()}   {dataset[4].max()}    {dataset[4].mean().round(2)}    {dataset[4].median().round(2)}"
    rssi_ = f"{dataset[5].min()}   {dataset[5].max()}    {dataset[5].mean().round(2)}    {dataset[5].median().round(2)}"
    tmst_ = f"{dataset[7].min()}   {dataset[7].max()}    {dataset[7].mean().round(2)}    {dataset[7].median().round(2)}"

    s = f"- Position:\t\t {position} \n      LAT: {lat}   LON: {lon}\n"\
        f"- Spreading Factor (SF):\n(val)  (quantity)\n{sf_}\n"\
        f"- BandWidth (BW):\n{bw_}\n"\
        f"- Length Payload (LEN):\n{len_}\n\n"\
        f"- Lora Signal Noise Ratio (LSNR):\n(min)  (max) (mean)  (median)\n{lsnr_}\n\n"\
        f"- Recv Sign Strength Indi (RSSI):\n{rssi_}\n\n"\
        f"- Diff. Timestamp (TMST_DIF):\n{tmst_}\n"
    
    #plt.plot(dataset[7], 'o')
    #plt.show()

    return s

def set_flag(cursor, tmst, flag):
    cursor.execute(f"UPDATE {TABLE_SENSORS} SET message['flag'] = {flag} WHERE tmst = {tmst};")

def delete_row(cursor, tmst):
    cursor.execute(f"DELETE FROM {TABLE_DOUBTS} WHERE tmst = {tmst}")

connection = connect(NODEURL)
cursor = connection.cursor()
blob_container = connection.get_blob_container(BLOB)
wind = False

while True:
    event, values = window.read()               # Read the event that happened and the values dictionary
    #print(event, values)
    if event == None or event == 'Exit':        # If user closed window with X or if user clicked "Exit" button then exit
        window.close()
        break
    if event == '-BUTTON1-':
        out, tmst, total = get_data(cursor)
        window["-LIST-"].update(out)
        
        if not wind:
            window2 = sg.Window(title="Information", icon= INFO_ICON, layout=layout2, font=font, finalize=True, location=location2)
            wind = True
        
        window2["-TOTAL-"].update(f"TOTAL of doubts = {total}")
    
    if event == '-BUTTON2-':
        if values["-LIST-"] != []:
            dev = values["-LIST-"][0][0 : 8]
            metrics = get_metrics(cursor, dev)
            
            window2['-TEXTinits-'].update(f"Metrics of : {dev}")
            window2['-TEXTOUT-'].update(metrics)
    
    if event == '-BUTTON3-':
        if values["-LIST-"] != []:
            result = sg.popup_yes_no('Confirm?', keep_on_top=True, no_titlebar = True, font= ("Arial, 11"))
            if result == 'Yes':
                i = out.index(values["-LIST-"][0])
                set_flag(cursor, tmst[i], 0)            #SET FLAG 1 TO TABLE_SENSORS
                delete_row(cursor, tmst[i])             #DELETE ROW IN TABLE_DOUBTS

                time.sleep(1)
                out, tmst, total = get_data(cursor)     #UPDATE LIST TO NEW DOUBTS
                window["-LIST-"].update(out)

                time.sleep(1)
                sg.popup_notify("DONE")
    if event == '-BUTTON4-':
        dev = values["-LIST-"][0][0 : 8]
        os.system(f"{DIR}3_train_model.py {dev}")

