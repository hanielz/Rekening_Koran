from var_dump import var_dump

#FastAPI Package

#http handling error
from fastapi import FastAPI, Request,status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import Union

#uvicorn package
import uvicorn

#import Class Models from Models.py
from Models import Models

#created object from class model
objModel  = Models()

#FastAPI Object
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/Rekening_Koran/casa/{no_rekening}/{start_date}/{end_date}",response_class=HTMLResponse)
async def read_no_rek(request: Request,no_rekening: str, start_date, end_date: str):
    
    ##1.MUTASI
    Mutasi = objModel.Mutasi(no_rekening,start_date,end_date)
    
    ##2.DEMOGRAFI
    #Demografi = objModel.demografi(no_rekening,start_date, end_date) 
    ##3.OUTPUT RESPONSE
    #Response = objModel.outputView(Mutasi,Demografi)
    Output = objModel.outputView(Mutasi)
    return templates.TemplateResponse("item.html", {"request": request, "Output" : Output})
    

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})
# uvicorn.run(app, port=5000 , host='0.0.0.0')