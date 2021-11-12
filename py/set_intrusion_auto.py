from crate.client import connect
import pandas as pd
import random

NODEURL = "http://localhost:4200/"
BLOB = "modeltable"
TABLE_SENSORS = 'sensors'
DEVADDR = '0000BF53'

LSNR_MIN = -20
LSNR_MAX = 10
RSSI_MIN = -130
RSSI_MAX = -10
TMST_MIN = 2000     #miliseconds
LEN_MIN = 10        #VER
LEN_MAX = 222       #VER

NUM_INTRUSION = 5
LSNR_MARGIN = 15
RSSI_MARGIN = 50
TMST_MARGIN = 40000
LEN_HOP = 60                #ONLY PAIR NUMBER
LIST_SF = [7,8,9,10,11,12]
LIST_BW = [125, 250, 500]

LIMIT = 5*9

def update(cursor, list_, name, tmst):
    for i in range(len(list_)):
        cursor.execute(f"UPDATE {TABLE_SENSORS} SET message['{name}'] = {list_[i]}, message['flag'] = 1 WHERE message['tmst'] = {tmst[i][0]};")

def set_intrusion(cursor, devaddr):
    cursor.execute(f"SELECT tmst FROM {TABLE_SENSORS} ORDER BY tmst LIMIT {LIMIT}")
    t = cursor.fetchall()

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
    
    sf_unique = dataset[2].unique()
    bw_unique = dataset[3].unique()
    rssi_median = int(dataset[5].median())
    lsnr_median = int(dataset[4].median())
    tmst_median = int(dataset[7].median())

    ### SF ###
    l_sf = LIST_SF
    for i in range(len(sf_unique)):
        l_sf.pop(l_sf.index(sf_unique[i]))
    sf_list = [random.choice(l_sf) for i in range(NUM_INTRUSION)]
    
    update(cursor, sf_list, "sf", t)                #UPDATE SF
    t = t[NUM_INTRUSION:]

    ### BW ###
    l_bw = LIST_BW
    for i in range(len(bw_unique)):
        l_bw.pop(l_bw.index(bw_unique[i]))
    bw_list = [random.choice(l_bw) for i in range(NUM_INTRUSION)]

    update(cursor, bw_list, "bw", t)                #UPDATE BW
    t = t[NUM_INTRUSION:]

    ### LEN ###
    len_occurrent = dataset[6].unique()[dataset[6].value_counts().to_list().index(max(dataset[6].value_counts().to_list()))] #LEN MORE OCCURRENCY
    if len_occurrent % 2 == 0: #IF PAIR
        r = LEN_HOP+1
    else:
        r = LEN_HOP
    len_list = [random.randrange(LEN_MIN, LEN_MAX, r) for i in range(NUM_INTRUSION)]
    
    update(cursor, len_list, "lenpayload", t)       #UPDATE LEN
    t = t[NUM_INTRUSION:]
    
    

    ### LSNR ###
    if lsnr_median + LSNR_MARGIN < LSNR_MAX:
        lsnr_max = lsnr_median + LSNR_MARGIN
    else:
        lsnr_max = LSNR_MAX
    
    if lsnr_median - LSNR_MARGIN > LSNR_MIN:
        lsnr_min = lsnr_median - LSNR_MARGIN
    else:
        lsnr_min = LSNR_MIN

    lsnr_min_list = [random.randrange(lsnr_min-2, lsnr_min+2, 1) for i in range(NUM_INTRUSION)]
    lsnr_max_list = [random.randrange(lsnr_max-2, lsnr_max+2, 1) for i in range(NUM_INTRUSION)]

    lsnr_list = []
    lsnr_list.extend(lsnr_min_list)
    lsnr_list.extend(lsnr_max_list)
    update(cursor, lsnr_list, "lsnr", t)            #UPDATE LSNR
    t = t[NUM_INTRUSION*2:]

    ### RSSI ###
    if rssi_median + RSSI_MARGIN < RSSI_MAX:
        rssi_max = rssi_median + RSSI_MARGIN
    else:
        rssi_max = RSSI_MAX

    if rssi_median - RSSI_MARGIN > RSSI_MIN:
        rssi_min = rssi_median - RSSI_MARGIN
    else:
        rssi_min = RSSI_MIN
    
    rssi_min_list = [random.randrange(rssi_min-2, rssi_min+2, 1) for i in range(NUM_INTRUSION)]
    rssi_max_list = [random.randrange(rssi_max-2, rssi_max+2, 1) for i in range(NUM_INTRUSION)]

    rssi_list = []
    rssi_list.extend(rssi_min_list)
    rssi_list.extend(rssi_max_list)
    update(cursor, rssi_list, "rssi", t)            #UPDATE RSSI
    t = t[NUM_INTRUSION*2:]
    
    ### DIF_TMST ###
    if tmst_median - TMST_MARGIN > TMST_MIN:
        tmst_min = tmst_median - TMST_MARGIN
    else:
        tmst_min = TMST_MIN
    
    tmst_max = tmst_median + TMST_MARGIN
    tmst_min_list = [random.randrange(tmst_min-500, tmst_min+500, 100) for i in range(NUM_INTRUSION)]
    tmst_max_list = [random.randrange(tmst_max-500, tmst_max+500, 100) for i in range(NUM_INTRUSION)]

    tmst_list = []
    tmst_list.extend(tmst_min_list)
    tmst_list.extend(tmst_max_list)
    update(cursor, tmst_list, "tmst_dif", t)        #UPDATE TMST DIF
    t = t[NUM_INTRUSION*2:]

    
    print(sf_list)
    print(bw_list)
    print(len_list)
    print()
    print(lsnr_list)
    print(rssi_list)
    print(tmst_list)
    
    return sf_list, bw_list, len_list, lsnr_list, rssi_list, tmst_list



connection = connect(NODEURL)
cursor = connection.cursor()
blob_container = connection.get_blob_container(BLOB)


set_intrusion(cursor, DEVADDR)


connection.close()
