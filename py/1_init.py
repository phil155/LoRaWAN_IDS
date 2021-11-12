#!/usr/bin/python3
import sys
from constants import *
from crate.client import connect

def create_normal_table(cursor, table):                         #IF NOT EXIST TABLE -> CREATE
    createtable = f"CREATE TABLE IF NOT EXISTS {table} (" \
                    "devaddr TEXT, "\
                    "tmst TIMESTAMP WITH TIME ZONE," \
                    "message object as ("\
                        "bw BIGINT,"\
                        "flag BIGINT,"\
                        "latitude REAL,"\
                        "longitude REAL,"\
                        "lsnr REAL,"\
                        "rssi REAL,"\
                        "tmst TIMESTAMP WITH TIME ZONE,"\
                        "tmst_dif BIGINT,"\
                        "lenpayload BIGINT,"\
                        "payload TEXT,"\
                        "sf BIGINT"\
                        ")"\
                    ");"
    cursor.execute(createtable)

def create_models_table(cursor, table):
    createtable = f"CREATE TABLE IF NOT EXISTS {table} (" \
                    "devaddr TEXT, "\
                    "model object as ("\
                        "model TEXT,"\
                        "scaler TEXT"\
                        ")"\
                    ");"
    cursor.execute(createtable)

def create_blob_table(cursor, table):
    cursor.execute(f"SELECT model FROM models")
    if len(cursor.fetchone()) == 0:
        cursor.execute(f"CREATE BLOB TABLE {table}")


def main():
    connection = connect(NODEURL)
    cursor = connection.cursor()

    create_normal_table(cursor, TABLE_SENSORS)
    create_normal_table(cursor, TABLE_DOUBTS)
    create_models_table(cursor, TABLE_MODELS)
    create_blob_table(cursor, BLOB)

    cursor.close()

if __name__ == "__main__":
    main()

'''EXTRA'''
#create_normal_table(cursor, 'original_3')
#create_normal_table(cursor, 'intrusions')
#create_normal_table(cursor, 'bf53_with_content_of_a010')
#create_normal_table(cursor, 'sensors_4intrusion')