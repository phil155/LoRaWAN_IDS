DIR = "/home/phil/Documents/IDS/py/"

'''CRATEDB'''
NODEURL = "http://localhost:4200/"
BLOB = "modeltable"

'''GUI'''
SERVER_ICON = "icons/server.png"
INFO_ICON = "icons/info.png"

'''TABLE NAMES'''
TABLE_SENSORS = 'sensors'
TABLE_DOUBTS = 'doubts'
TABLE_MODELS = 'models'

'''FOR TRAIN MODEL'''
NUM_THREADS = 20

'''FOR AUTO INTRUSIONS'''
NUM_INTRUSION = 5
LIMIT = NUM_INTRUSION*9

LSNR_MIN = -20
LSNR_MAX = 10
RSSI_MIN = -130
RSSI_MAX = -10
TMST_MIN = 2000     #miliseconds
LEN_MIN = 10        #VER
LEN_MAX = 222       #VER

LSNR_MARGIN = 15
RSSI_MARGIN = 50
TMST_MARGIN = 40000
LEN_HOP = 60                #ONLY PAIR NUMBER
LIST_SF = [7,8,9,10,11,12]
LIST_BW = [125, 250, 500]


'''COLOR TERMINAL'''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'