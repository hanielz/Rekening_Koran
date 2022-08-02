import os
import csv
import time
import decimal
import phoenixdb
from phoenixdb.avatica.proto.common_pb2 import NULL
import phoenixdb.cursor
from datetime import datetime
import sys
import json
from decimal import *
from collections import Iterable
from re import A
from flask import Flask
from flask import json
from flask import jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.ext.declarative import api
from werkzeug.datastructures import LanguageAccept
from flask import Flask, request, abort, jsonify
from werkzeug.exceptions import HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
import random




def flatten(list_values):
     for item in list_values:
         if isinstance(item, Iterable) and not isinstance(item, str):
             for x in flatten(item):
                 yield x
         else:
             yield item

# test = nomor_rekening
# print('start')
# # print(nomor_rekening())
# print(tanggal_awal())
# print(tanggal_akhir())
#connection DB




#kinit first
os.system('kinit -kt /home/cloud-user/CLDRODSDRSVC.keytab CLDRODSDRSVC@HQ.BRI.CO.ID')

#globe variable
cursor=NULL

server = ['hbdrm01.data.bri.co.id', 'hbdrm02.data.bri.co.id', 'hbdrm03.data.bri.co.id', 'hbdrdata01.data.bri.co.id', 'hbdrdata02.data.bri.co.id','hbdrdata03.data.bri.co.id','hbdrdata04.data.bri.co.id','hbdrdata05.data.bri.co.id','hbdrdata06.data.bri.co.id']

if __name__ == '__main__':
    pqs_port = '8765'
    hostname = random.choice(server)
    # hostname = 'hbdrm01.hq.bri.co.id'
    database_url = 'http://' +(hostname)+ ':' +(pqs_port)+ '/'
    print("CREATING PQS CONNECTION")
    conn = phoenixdb.connect(database_url, autocommit=True, auth="SPNEGO")
    cursor = conn.cursor()



#kinit schedule
def kinit():
    os.system('kinit -kt /home/cloud-user/CLDRODSDRSVC.keytab CLDRODSDRSVC@HQ.BRI.CO.ID')
#set schedule setiap 6 jam
sched = BackgroundScheduler(daemon=True)
sched.add_job(kinit,'interval',hours=3)
sched.start()



# ======================
def mutasi():
    #Parameter input fron API URL
    nomor_rekening = request.args.get('nomor_rekening')
    tanggal_awal = request.args.get('tanggal_awal')
    tanggal_akhir = request.args.get('tanggal_akhir')


    # inquiry ddmast
    inquiry_ddmast_date = f"SELECT MODFIED_DATE  FROM POC_REKENING_KORAN.DDMAST_PST DDMAST WHERE ACCTNO  ='{nomor_rekening}'"
    cursor.execute(inquiry_ddmast_date)
    tanggal_inquiry = cursor.fetchall()
    tanggal_inquiry = list(flatten(tanggal_inquiry))
    tanggal_inquiry = str(tanggal_inquiry[0])
    tanggal_trx_awal = tanggal_awal
    tanggal_ddmast = tanggal_inquiry   
    date_format = "%Y-%m-%d"
    tanggal_trx_awal = datetime.strptime(tanggal_trx_awal, date_format)
    tanggal_ddmast = datetime.strptime(tanggal_ddmast, date_format)
    
    
    
    #tanggal trx awal lebih kecil dari ddmast
    if tanggal_trx_awal < tanggal_ddmast :
        saldo_awal = f"SELECT (DDMAST.CBAL_BASE + SUM(DDHIST.DEBIT) - SUM(DDHIST.KREDIT)) AS saldo_awal FROM POC_REKENING_KORAN.DDMAST_PST DDMAST INNER JOIN (SELECT DEBIT,KREDIT,NOMOR_REKENING FROM POC_REKENING_KORAN.DDHIST_PST WHERE NOMOR_REKENING = '{nomor_rekening}' AND TANGGAL_TRANSAKSI  >= TO_DATE('{tanggal_awal}') + (1) AND TANGGAL_TRANSAKSI <= TO_DATE('{tanggal_inquiry}') + (1)) DDHIST ON DDMAST.ACCTNO = DDHIST.NOMOR_REKENING GROUP BY DDMAST.CBAL_BASE"
        cursor.execute(saldo_awal)
        saldo_awal = cursor.fetchall()
        saldo_awal = list(flatten(saldo_awal))
        saldo_awal = saldo_awal[0]
 
     #tanggal trx awal sama dengan ddmast       
    elif tanggal_trx_awal == tanggal_ddmast :
        saldo_awal = f"SELECT (DDMAST.CBAL_BASE + SUM(DDHIST.DEBIT) - SUM(DDHIST.KREDIT)) AS saldo_awal FROM POC_REKENING_KORAN.DDMAST_PST DDMAST INNER JOIN (SELECT DEBIT,KREDIT,NOMOR_REKENING FROM POC_REKENING_KORAN.DDHIST_PST WHERE NOMOR_REKENING = '{nomor_rekening}' AND TANGGAL_TRANSAKSI  >= TO_DATE('{tanggal_awal}') + (1) AND TANGGAL_TRANSAKSI <= TO_DATE('{tanggal_inquiry}') + (1)) DDHIST ON DDMAST.ACCTNO = DDHIST.NOMOR_REKENING GROUP BY DDMAST.CBAL_BASE"
        cursor.execute(saldo_awal)
        saldo_awal = cursor.fetchall()
        saldo_awal = list(flatten(saldo_awal))
        saldo_awal = saldo_awal[0]
        
      #tanggal trx awal lebih dengan ddmast     
    else :
        saldo_awal = f"SELECT (DDMAST.CBAL_BASE - SUM(DDHIST.DEBIT) + SUM(DDHIST.KREDIT)) AS saldo_awal FROM POC_REKENING_KORAN.DDMAST_PST DDMAST INNER JOIN (SELECT DEBIT,KREDIT,NOMOR_REKENING FROM POC_REKENING_KORAN.DDHIST_PST WHERE NOMOR_REKENING = '{nomor_rekening}' AND TANGGAL_TRANSAKSI  <= TO_DATE('{tanggal_awal}') + (1) AND TANGGAL_TRANSAKSI >= TO_DATE('{tanggal_inquiry}') + (1)) DDHIST ON DDMAST.ACCTNO = DDHIST.NOMOR_REKENING GROUP BY DDMAST.CBAL_BASE"
        cursor.execute(saldo_awal)
        saldo_awal = cursor.fetchall()
        saldo_awal = list(flatten(saldo_awal))
        saldo_awal = saldo_awal[0]


    #Query mutasi rekening
    cursor.execute(f"SELECT  DDHIST.NOMOR_REKENING, DDHIST.TANGGAL_TRANSAKSI,CASE WHEN DDHIST.KETERANGAN IS NULL THEN 'NULL' ELSE DDHIST.KETERANGAN END AS KETERANGAN, (DDHIST.DEBIT), (DDHIST.KREDIT)  FROM POC_REKENING_KORAN.DDHIST_PST DDHIST  WHERE DDHIST.NOMOR_REKENING = '{nomor_rekening}' AND DDHIST.TANGGAL_TRANSAKSI  >= TO_DATE('{tanggal_awal}') + (1) AND DDHIST.TANGGAL_TRANSAKSI <= TO_DATE('{tanggal_akhir}') + (1) ORDER BY TANGGAL_TRANSAKSI ASC")
    mutasi_rekening = cursor.fetchall()



    #aray mutasi output
    result = []
    for mutasi_rekening in mutasi_rekening :
        temp = dict.fromkeys(['NOMOR_REKENING','TANGGAL_TRANSAKSI','KETERANGAN','DEBIT','KREDIT','SALDO_AWAL','SALDO_AKHIR'])

        temp["NOMOR_REKENING"] = mutasi_rekening[0]
        temp["TANGGAL_TRANSAKSI"] = mutasi_rekening[1].strftime("%Y-%m-%d")
        temp["KETERANGAN"] = mutasi_rekening[2]
        temp["DEBIT"] = float(mutasi_rekening[3])
        temp["KREDIT"] = float(mutasi_rekening[4])
        temp["SALDO_AWAL"] = float(saldo_awal)
        temp["SALDO_AKHIR"] = float(saldo_awal - mutasi_rekening[3] + mutasi_rekening[4])
        saldo_awal= (saldo_awal - mutasi_rekening[3] + mutasi_rekening[4])
        result.append(temp)
    
    output = dict.fromkeys(['mutasi'])
    tmp = []
    counter = 0
    for val in result:
        tmp.append(val)
        counter = counter+1
    output["mutasi"] = tmp
    json_rekening_koran = json.dumps(output)
    json_rekening_koran = json.loads(json_rekening_koran.replace("\'", '"'))
    return json_rekening_koran
#==========================JSON_CSV=====================    

    

def gen_csv():
    #Parameter input fron API URL
    nomor_rekening = request.args.get('nomor_rekening')
    tanggal_awal = request.args.get('tanggal_awal')
    tanggal_akhir = request.args.get('tanggal_akhir')
    start = time.time()

    # inquiry ddmast
    inquiry_ddmast_date = f"SELECT MODFIED_DATE  FROM POC_REKENING_KORAN.DDMAST_PST DDMAST WHERE ACCTNO  ='{nomor_rekening}'"
    cursor.execute(inquiry_ddmast_date)
    tanggal_inquiry = cursor.fetchall()
    tanggal_inquiry = list(flatten(tanggal_inquiry))
    tanggal_inquiry = str(tanggal_inquiry[0])
    tanggal_trx_awal = tanggal_awal
    tanggal_ddmast = tanggal_inquiry   
    date_format = "%Y-%m-%d"
    tanggal_trx_awal = datetime.strptime(tanggal_trx_awal, date_format)
    tanggal_ddmast = datetime.strptime(tanggal_ddmast, date_format)
    
    
    
    #tanggal trx awal lebih kecil dari ddmast
    if tanggal_trx_awal < tanggal_ddmast :
        saldo_awal = f"SELECT (DDMAST.CBAL_BASE + SUM(DDHIST.DEBIT) - SUM(DDHIST.KREDIT)) AS saldo_awal FROM POC_REKENING_KORAN.DDMAST_PST DDMAST INNER JOIN (SELECT DEBIT,KREDIT,NOMOR_REKENING FROM POC_REKENING_KORAN.DDHIST_PST WHERE NOMOR_REKENING = '{nomor_rekening}' AND TANGGAL_TRANSAKSI  >= TO_DATE('{tanggal_awal}') + (1) AND TANGGAL_TRANSAKSI <= TO_DATE('{tanggal_inquiry}') + (1)) DDHIST ON DDMAST.ACCTNO = DDHIST.NOMOR_REKENING GROUP BY DDMAST.CBAL_BASE"
        cursor.execute(saldo_awal)
        saldo_awal = cursor.fetchall()
        saldo_awal = list(flatten(saldo_awal))
        saldo_awal = saldo_awal[0]
 
     #tanggal trx awal sama dengan ddmast       
    elif tanggal_trx_awal == tanggal_ddmast :
        saldo_awal = f"SELECT (DDMAST.CBAL_BASE + SUM(DDHIST.DEBIT) - SUM(DDHIST.KREDIT)) AS saldo_awal FROM POC_REKENING_KORAN.DDMAST_PST DDMAST INNER JOIN (SELECT DEBIT,KREDIT,NOMOR_REKENING FROM POC_REKENING_KORAN.DDHIST_PST WHERE NOMOR_REKENING = '{nomor_rekening}' AND TANGGAL_TRANSAKSI  >= TO_DATE('{tanggal_awal}') + (1) AND TANGGAL_TRANSAKSI <= TO_DATE('{tanggal_inquiry}') + (1)) DDHIST ON DDMAST.ACCTNO = DDHIST.NOMOR_REKENING GROUP BY DDMAST.CBAL_BASE"
        cursor.execute(saldo_awal)
        saldo_awal = cursor.fetchall()
        saldo_awal = list(flatten(saldo_awal))
        saldo_awal = saldo_awal[0]
        
      #tanggal trx awal lebih dengan ddmast     
    else :
        saldo_awal = f"SELECT (DDMAST.CBAL_BASE - SUM(DDHIST.DEBIT) + SUM(DDHIST.KREDIT)) AS saldo_awal FROM POC_REKENING_KORAN.DDMAST_PST DDMAST INNER JOIN (SELECT DEBIT,KREDIT,NOMOR_REKENING FROM POC_REKENING_KORAN.DDHIST_PST WHERE NOMOR_REKENING = '{nomor_rekening}' AND TANGGAL_TRANSAKSI  <= TO_DATE('{tanggal_awal}') + (1) AND TANGGAL_TRANSAKSI >= TO_DATE('{tanggal_inquiry}') + (1)) DDHIST ON DDMAST.ACCTNO = DDHIST.NOMOR_REKENING GROUP BY DDMAST.CBAL_BASE"
        cursor.execute(saldo_awal)
        saldo_awal = cursor.fetchall()
        saldo_awal = list(flatten(saldo_awal))
        saldo_awal = saldo_awal[0]


    #Query mutasi rekening
    cursor.execute(f"SELECT  DDHIST.NOMOR_REKENING, DDHIST.TANGGAL_TRANSAKSI,CASE WHEN DDHIST.KETERANGAN IS NULL THEN 'NULL' ELSE DDHIST.KETERANGAN END AS KETERANGAN, (DDHIST.DEBIT), (DDHIST.KREDIT)  FROM POC_REKENING_KORAN.DDHIST_PST DDHIST  WHERE DDHIST.NOMOR_REKENING = '{nomor_rekening}' AND DDHIST.TANGGAL_TRANSAKSI  >= TO_DATE('{tanggal_awal}') + (1) AND DDHIST.TANGGAL_TRANSAKSI <= TO_DATE('{tanggal_akhir}') + (1) ORDER BY TANGGAL_TRANSAKSI ASC")
    mutasi_rekening = cursor.fetchall()



    #aray mutasi output
    result = []
    for mutasi_rekening in mutasi_rekening :
        temp = dict.fromkeys(['NOMOR_REKENING','TANGGAL_TRANSAKSI','KETERANGAN','DEBIT','KREDIT','SALDO_AWAL','SALDO_AKHIR'])

        temp["NOMOR_REKENING"] = mutasi_rekening[0]
        temp["TANGGAL_TRANSAKSI"] = mutasi_rekening[1].strftime("%Y-%m-%d")
        temp["KETERANGAN"] = mutasi_rekening[2]
        temp["DEBIT"] = float(mutasi_rekening[3])
        temp["KREDIT"] = float(mutasi_rekening[4])
        temp["SALDO_AWAL"] = float(saldo_awal)
        temp["SALDO_AKHIR"] = float(saldo_awal - mutasi_rekening[3] + mutasi_rekening[4])
        saldo_awal= (saldo_awal - mutasi_rekening[3] + mutasi_rekening[4])
        result.append(temp)
    jsondata = json.dumps(result)
    jsondata = json.loads(jsondata)
    data_file = open('/home/cloud-user/rekening_koran/rekening_koran.csv', 'w', newline='')
    csv_writer = csv.writer(data_file)
 
    count = 0
    for data in jsondata:
        if count == 0:
            header = data.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(data.values())
 
    data_file.close()
    end = time.time()
    count_time = (end - start)
    count_time = (str(count_time)+" Second")
    generate_csv = [[count_time,"Successfull Generated CSV","/home/cloud-user/rekening_koran/rekening_koran.csv"]]
    result = []
    for generate_csv in generate_csv :
        temp = dict.fromkeys(['DURATION','CSV_STATUS','LOCATION'])
        temp["DURATION"] = str(generate_csv[0])
        temp["CSV_STATUS"] = generate_csv[1]
        temp["LOCATION"] = generate_csv[2]
        result.append(temp)
        
    generate_csv = json.dumps(result)
    generate_csv = json.loads(generate_csv.replace("\'", '"'))
    return generate_csv

# ========================
#return jsonify(nomor_rekening,tanggal_awal,tanggal_akhir)
#  if nomor_rekening == '123213123' and tanggal_awal == '2021-09-09' and tanggal_akhir = '2021-09-10' :
#     print('asdaadsasd')
#url   http://127.0.0.1:5000/api/v1/transaction/?nomor_rekening=1004006509&tanggal_awal=2021-09-04&tanggal_akhir=2021-09-07


#apps run
app = Flask(__name__)
api = Api(app)

#error_handling
@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

@app.route('/')
def index():
    abort(409)


#API endpoint
class rek_koran(Resource) :
    def get(self):
        return mutasi()


class download_rek_koran(Resource) :
    def get(self):
        return gen_csv()

#api url
api.add_resource(rek_koran, "/api/v1/transaction/")
api.add_resource(download_rek_koran, "/api/v1/transaction/downloads/")

#apps debug and ipaddress
app.run(host="0.0.0.0", port=5002, debug=True, threaded=True)
#app.run(host="10.148.2.106", port=5002, debug=True, threaded=True)

