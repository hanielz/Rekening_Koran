#FastAPI Package
from fastapi import FastAPI, Request,status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import Union

#uvicorn package
import uvicorn

#import Class Models from Models.py
from Models import Models
# from Procedure import Procedure

#created object from class model
objModel  = Models()

#FastAPI Object
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/Rekening_Koran/casa/{no_rekening}/{start_date}/{end_date}")
async def read_no_rek(no_rekening: str, start_date, end_date: str):
    
    ##1.MUTASI
    Mutasi = objModel.Mutasi(no_rekening,start_date,end_date)
    
    ##2.DEMOGRAFI
    Demografi = objModel.demografi(no_rekening,start_date,end_date) 
    ##3.OUTPUT RESPONSE
    Output = objModel.outputView(Mutasi,Demografi)
    # Response = objModel.outputView(Mutasi)
    return Output
    # return templates.TemplateResponse(
    #     "item.html", {"request": request, 
    #                  "Demografi" : Demografi ,
    #                  "Mutasi" : Mutasi}
    #     )

@app.get("/Rekening_Koran/loan/{no_rekening}/{start_date}/{end_date}")
async def read_no_rek(no_rekening: str, start_date, end_date: str):
    loanDemografi = objModel.loanDemografi(no_rekening,start_date,end_date)
    print(loanDemografi)
    # mutasiLoan = objModel.loanMutasi(self,acctno, start_date, end_date)
    Output = objModel.outputView('mutasiLoan',loanDemografi)
    return Output

@app.get("/testing/{no_rekening}/{start_date}/{end_date}")
async def main_testing(no_rekening: str, start_date:str, end_date: str):
    # test = objModel.testing(no_rekening)
    Mutasi = objModel.Mutasi(no_rekening,start_date,end_date)
    return Mutasi

