SELECT "devaddr", "model" FROM "doc"."models";


DELETE FROM "models" WHERE "devaddr" = 'D';


CREATE BLOB TABLE modeltable;

DROP BLOB TABLE modeltable;


INSERT INTO models (devaddr, model) VALUES (?,?) , (DEVADDR, { "model": key , "scaler": s })


INSERT INTO duvidas SELECT * FROM test WHERE message['tmst'] = 1591138908764;


SELECT devaddr FROM "doc"."models" WHERE "devaddr" = '0000BF53'
UPDATE "models" SET model = '{ "model": "ABC" , "scaler": "123" }' WHERE "devaddr" = '0000BF53'; 

UPDATE duvidas SET message['flag'] = 20 WHERE message['tmst'] = 1591153557828;


CREATE TABLE duvidas (
  devaddr TEXT,
  tmst TIMESTAMP WITH TIME ZONE,
  message object as (
    bw BIGINT,
    flag BIGINT,
    latitude REAL,
    longitude REAL,
    lsnr REAL,
    rssi REAL,
    tmst TIMESTAMP WITH TIME ZONE,
    tmst_dif BIGINT,
    lenpayload BIGINT,
    payload TEXT,
    sf BIGINT
    )
  );