# -*- coding: UTF-8 -*-
from flask import Flask, request, Response
from datetime import timedelta,date
import requests,json,datetime,pymysql
from waitress import serve

app = Flask(__name__)
@app.route('', methods=['POST'])
def root():
    try:
        try:
            accessIP = str(request.access_route[0])
            #print accessIP 
            f = open(r'access_start_honsecStockRecommend.log', 'a')
            f.writelines("\n["+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"]"+accessIP)
            f.close()        
        except BaseException as e:
            print (e)

        pymysql.install_as_MySQLdb()
        db = pymysql.connect(host="", user="", passwd="", db="", charset='utf8')
        cursor = db.cursor()

        user = ""
        password = ""
        try:
            user = str(request.form['user'])
            password = str(request.form['password'])
        except BaseException as e:
            f = open(r'Record_Error_honsecStockRecommend.txt', 'a')
            f.writelines("\n["+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"] withoutUserPass")
            f.close()

            data_json = {}
            data_json["title"] = "FlowSR"
            data_json["data"] = []
            data_json["calc_date"] = str(datetime.datetime.now().strftime('%Y-%m-%d'))
            data_json["total"] = "withoutUserPass"
            returnData = json.dumps(data_json,ensure_ascii=False,indent=2).decode("utf-8","ignore")
            return returnData

        if user != "" or password != "":
            f = open(r'Record_Error_honsecStockRecommend.txt', 'a')
            f.writelines("\n["+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"]HONSEC_AISTK: userpassError")
            f.close()

            data_json = {}
            data_json["title"] = "FlowSR"
            data_json["data"] = []
            data_json["calc_date"] = str(datetime.datetime.now().strftime('%Y-%m-%d'))
            data_json["total"] = "userpassError"
            returnData = json.dumps(data_json,ensure_ascii=False,indent=2).decode("utf-8","ignore")
            return returnData            
        
        data_json = {}
        data_json["title"] = "FlowSR"
        data_json["data"] = []
        sql = "SELECT CURDATE()"
        cursor.execute(sql)
        for i in cursor.fetchall():
            data_json["calc_date"] = str(i[0])

        week = int(datetime.datetime.now().strftime("%w"))
        if (week == 5):
            sql = "SELECT * FROM honsecStockRecommend WHERE date = CURDATE()" 
            cursor.execute(sql)
            counti = 0
            for i in cursor.fetchall():
                if counti == 0:
                    data_json["calc_date"] = str(i[1])
                print (i[1],i[2],i[3])
                if i[2] is not None:
                    stocklist = i[2].split(",")
                    for j in stocklist:
                        info = {}
                        info["TradeDate"] = str(int(str(i[1]).split("-")[0])-1911)+"/"+str(i[1]).split("-")[1]+"/"+str(i[1]).split("-")[2]
                        info["MarketId"] = ""
                        info["StockId"] = j
                        info["StockName"] = ""
                        info["BuySell"] = i[3]
                        info["ReferPrice"] = ""
                        info["Remarks"] = ""
                        info["ModifiedTime"] = str(i[1]).replace("-","/")+" 03:00:00"
                        data_json["data"].append(info)
                        counti += 1
            data_json["total"] = counti
                    
            returnData = json.dumps(data_json,ensure_ascii=False,indent=2).decode("utf-8","ignore")
            return returnData
        else:
            data_json = {}
            data_json["title"] = "FlowSR"
            data_json["data"] = []
            data_json["calc_date"] = str(datetime.datetime.now().strftime('%Y-%m-%d'))
            data_json["total"] = "No Data Today!"
            returnData = json.dumps(data_json,ensure_ascii=False,indent=2).decode("utf-8","ignore")
            return returnData
    except BaseException as e:
        f = open(r'Record_Error_honsecStockRecommend.txt', 'a') 
        f.writelines("\n["+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"]\n "+str(e))
        f.close()

        data_json = {}
        data_json['ErrorMsg'] = 'Process Wrong'
        returnData = json.dumps(data_json,ensure_ascii=False,indent=2).decode("utf-8","ignore")
        return returnData

if __name__ == '__main__':
    serve(app, host='', port='')

