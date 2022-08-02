from var_dump import var_dump

import mysql.connector 
from mysql.connector import Error

#FastAPI Package
from fastapi import FastAPI, status
from typing import Union

app = FastAPI()
        
def run_query(query) :
    cursor = mysql.connector.connect(host='localhost', user='root', password='P@ssw0rd', db='classicmodels').cursor(prepared=True)
    cursor.execute(query)
    return cursor
    

def Model() :
    db = run_query("select * from DL_DHIST")
    

    return db
   

@app.get("/test")
def read_item( ):
    data = Model()
    return {"Response" : data }
    # return Model()

