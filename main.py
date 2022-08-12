# from var_dump import var_dump

#FastAPI Package
from fastapi import FastAPI, status
from typing import Union

#uvicorn package
import uvicorn

#http handling error
from fastapi import FastAPI, HTTPException


#import Class Models from Models.py
from Models import Models

#created object from class model
objModel  = Models()

#FastAPI Object
app = FastAPI()

@app.get("/transaction")
def read_transaction():
    return { "All Records" : 'Response'}

@app.get("/Rekening_Koran/casa/{no_rekening}/{start_date}/{end_date}")
def read_no_rek( no_rekening: str, start_date, end_date: str):
    
    ##1.MUTASI
    Mutasi = objModel.Mutasi(no_rekening,start_date,end_date)
    
    ##2.DEMOGRAFI
    Demografi = objModel.demografi(no_rekening,start_date,end_date) 
    ##3.OUTPUT RESPONSE
    Response = objModel.outputView(Mutasi,Demografi)
    # Response = objModel.outputView(Mutasi)
    return Response

@app.get("/test")
def read_item(no_rekening: str, start_date, end_date: Union[str, None] = None  ):
    return objModel.Mutasi(no_rekening,start_date, end_date) 

# uvicorn.run(app, port=5000 , host='0.0.0.0')