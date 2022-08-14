from matplotlib.font_manager import json_load
import requests
import json
from datetime import datetime
from flask import Flask, escape, request, render_template, redirect, url_for, Response
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('default')
import io
from flask import Flask, escape, request, render_template
import base64
import talib
import yfinance as yf
import os, csv
from patterns import candlestick_patterns

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import mysql.connector


app = Flask(__name__)
#app.config['DEBUG'] = True

columns = ['Time', 'Call OI Sum', 'Change in Call OI Sum', 'Put OI Sum', 'Change in Put OI Sum', 'Diff of Change in OI', 'OI Signal', 'PCR', 'Futures LTP', 'Futures VWAP']
rowData = []
ce_data = []
pe_data = []
top5TrendingOIData = []
trendingOIData = []

@app.route('/')
def getdata():
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; '
                'x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}


    main_url = "https://www.nseindia.com/"
    response = requests.get(main_url, headers=headers)
    cookies = response.cookies


    ## NIFTY code
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    nifty_oi_data = requests.get(url, headers=headers, cookies=cookies)
    # print("Nifty OI data", nifty_oi_data.text)
    # write to file
    # with open("response.txt", "w") as f:
    #     f.write(nifty_oi_data.text)
    
    #future price
    last_thursday = "28-07-2022"
    url_future_ltp = f"https://www.nseindia.com/api/quote-derivative?symbol=NIFTY&identifier=FUTIDXNIFTY{last_thursday}XX0.00"
    future_data = requests.get(url_future_ltp, headers=headers, cookies=cookies)
    future_ltp = json.loads(future_data.text)["underlyingValue"]
    
    #futures VWAP
    # main_future_vwap_url = "https://www1.nseindia.com/"
    # response_future_vwap = requests.get(main_future_vwap_url, headers=headers)
    # cookies_future_vwap = response_future_vwap.cookies
    # cookies_future_vwap = "C1E859F8FF4BFCAF70B2E67DC7EE1AE1~YAAQpv3UF2kTHfqBAQAAcFDpBhBfEIYMCsdDDBrthOMK/qfuxSedC5GTW6E/qek7K1G4vyRP89ox0zt7nonae5UP4JDIKp7VMgrPeLz1U6nMQxxjVFXWi5Stvii8TVgCY3hEgaSyAXVe9pQBs3t7AFCMAoc9mriB/ZCV7NOj84o0P+ZbUL1A45nR/AtdHahT3pBhPPnCgwgf7shD7xM3m3kWukFld6MQNfTAHj8MZRc8tZTTIljZuCtRrZgqVTxsS1Q=~1"
    # url_future_vwap= f"https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/ajaxFOGetQuoteJSON.jsp?underlying=NIFTY&instrument=FUTIDX&expiry=28JUL2022"
    # future_vwap = requests.get(url_future_vwap,headers=headers, cookies=cookies_future_vwap)
    # xyz = json.loads(future_vwap)

    json_object = json.loads(nifty_oi_data.text)
    filteredRecordsForCurrentExpiry = json_object["filtered"]["data"]
    
    multiple = 50
    at_the_money_strike = multiple * round(json_object["records"]["underlyingValue"] / multiple)
    

    _OTMcloseStrikePricesCE = filter(lambda c: c["strikePrice"] >= at_the_money_strike and c["strikePrice"] <= (at_the_money_strike + 500), filteredRecordsForCurrentExpiry)

    _OTMcloseStrikePricesPE = filter(lambda c: c["strikePrice"] <= at_the_money_strike and c["strikePrice"] >= (at_the_money_strike - 500), filteredRecordsForCurrentExpiry)

    allCE = [["Strike", "Price", "OI", "Change in OI"]]
    allPE = [["Strike", "Price", "OI", "Change in OI"]]

    lstDataCE = list(_OTMcloseStrikePricesCE)
    lstDataPE = list(_OTMcloseStrikePricesPE)
    
    for m in lstDataCE:
        allCE.append([m["CE"]["strikePrice"], m["CE"]["lastPrice"], m["CE"]["openInterest"] * multiple, m["CE"]["changeinOpenInterest"] * multiple])
    for m in lstDataPE:
        allPE.append([m["PE"]["strikePrice"], m["PE"]["lastPrice"], m["PE"]["openInterest"] * multiple, m["PE"]["changeinOpenInterest"] * multiple])

    allCE.append(["Total", "", sum(row[2] for row in allCE[1:]), sum(row[3] for row in allCE[1:])])
    allPE.append(["Total", "", sum(row[2] for row in allPE[1:]), sum(row[3] for row in allPE[1:])])

    print("--------------START OF CALL DATA--------------------")

    for i in range(len(allCE)):
        if i == 0:
            print('{:<20}{:<20}{:<20}{:<20}'.format(allCE[i][0],allCE[i][1],allCE[i][2],allCE[i][3]))
        elif i == len(allCE) - 1:
            print('---------------------------------------------------------------------------------')
            print('{:<20}{:<20}{:<20}{:<20}'.format(allCE[i][0],allCE[i][1],allCE[i][2],allCE[i][3]))
        else:
            print('{:<20}{:<20}{:<20}{:<20}'.format(allCE[i][0],allCE[i][1],allCE[i][2],allCE[i][3]))

    print("--------------END OF CALL DATA--------------------")


    print("--------------START OF PUT DATA--------------------")

    for i in range(len(allPE)):
        if i == 0:
            print('{:<20}{:<20}{:<20}{:<20}'.format(allPE[i][0],allPE[i][1],allPE[i][2],allPE[i][3]))
        elif i == len(allPE) -1 :
            print('---------------------------------------------------------------------------------')
            print('{:<20}{:<20}{:<20}{:<20}'.format(allPE[i][0],allPE[i][1],allPE[i][2],allPE[i][3]))
        else:
            print('{:<20}{:<20}{:<20}{:<20}'.format(allPE[i][0],allPE[i][1],allPE[i][2],allPE[i][3]))

    print("--------------END OF PUT DATA--------------------")

    global ce_data, pe_data
    ce_data = allCE
    pe_data = allPE

    global top5TrendingOIData
    top5TrendingOIData = trending(ce_data, pe_data)

    pcr = sum(row[2] for row in allPE[1:]) / sum(row[2] for row in allCE[1:])
    print('PCR is :', pcr)
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    global rowData
    
    sum_call_OI = sum(row[2] for row in allCE[1:-1])
    change_call_OI = sum(row[3] for row in allCE[1:-1])
    sum_put_OI = sum(row[2] for row in allPE[1:-1])
    change_put_OI = sum(row[3] for row in allPE[1:-1])
    
    diff_change_Call_OI_and_change_put_OI = change_put_OI - change_call_OI
    
    oi_signal = ''
    if diff_change_Call_OI_and_change_put_OI > 0:
         oi_signal = "BUY"
    elif diff_change_Call_OI_and_change_put_OI < 0:
        oi_signal = "SELL"
    
    if change_put_OI >= 3 * change_call_OI :
         oi_signal = "STRONG BUY"
    elif change_call_OI > 3 * change_put_OI:
        oi_signal = "STRONG SELL"
    
    futures_vwap = 0
    dataToSave = [current_time, sum_call_OI, change_call_OI, sum_put_OI, change_put_OI,  diff_change_Call_OI_and_change_put_OI, oi_signal , pcr, future_ltp, futures_vwap]
    rowData.append(dataToSave)
    SaveToDB(dataToSave)
    return render_template('index.html', columns=columns, rowdata=rowData)

@app.route('/trendingoi')
def trendingoi():
    rowData = []
    columns = ["Time", "Trending Strike Prices in (Desc Order)", "Change in OI (respective to Strike Price)"]
    
    global top5TrendingOIData
    rowData = top5TrendingOIData
    allStrikes = rowData['strike'].tolist()
    allCOI = rowData['coi'].tolist()
    global trendingOIData
    trendingOIData.append([datetime.now().strftime("%H:%M:%S"), allStrikes, allCOI])
    # top5TrendingOIData = top5TrendingOIData.set_index("time")

    # fig = Figure()
    # axis = fig.add_subplot(1, 1, 1)
    # xs = top5TrendingOIData["time"]
    # ys = top5TrendingOIData["coi"]
    # axis.plot(xs, ys)
    
    # # Generate plot
    # axis.grid()
    # # #axis.plot(range(5), range(5), "ro-")
    
    # # Convert plot to PNG image
    # pngImage = io.BytesIO()
    # FigureCanvas(fig).print_png(pngImage)
    
    # # Encode PNG image to base64 string
    # pngImageB64String = "data:image/png;base64,"
    # pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    return render_template("trendingoi.html", oi_data=trendingOIData, columns=columns)

#ternding OI is top 5 change in OI strike with CE/PE
def trending(allCE, allPE):
    dt1 = datetime.now()
    time_now = dt1.strftime("%H:%M:%S")
    df2= pd.DataFrame(allCE[1:])
    df3= pd.DataFrame(allPE[1:])
    df2.columns = ["strike", "ltp", "oi", "coi"]
    df3.columns = ["strike", "ltp", "oi", "coi"]
    df2['strike'] = df2['strike'].astype(str) + 'CE'
    df3['strike'] = df3['strike'].astype(str) + 'PE'
    df4= pd.concat([df2,df3])
    df5 = df4.sort_values(by=['coi'] , ascending=False)
    df6 = df5[2:7]
    headers =  ["strike", "ltp", "oi", "coi"]
    df6.columns = headers
    return df6

@app.route('/screener')
def screener():
    return render_template("screener.html")

@app.route('/extractdata')
def extractdata():
    with open('datasets/symbols.csv') as f:
        for line in f:
            if "," not in line:
                continue
            symbol = line.split(",")[0]
            data = yf.download(symbol, start="2022-01-01", end=datetime.today().strftime('%Y-%m-%d'))
            data.to_csv('datasets/daily/{}.csv'.format(symbol.replace(".","_")))

    return {
        "code": "success"
    }
    
@app.route('/patterns')
def patterns():
    pattern  = request.args.get('pattern', False)
    stocks = {}

    with open('datasets/symbols.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company': row[1]}

    if pattern:
        for filename in os.listdir('datasets/daily'):
            df = pd.read_csv('datasets/daily/{}'.format(filename))
            pattern_function = getattr(talib, pattern)
            symbol = filename.split('_')[0] + ".NS"

            try:
                results = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last = results.tail(1).values[0]

                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
            except Exception as e:
                print('failed on filename: ', filename)

    return render_template('patterns.html', candlestick_patterns=candlestick_patterns, stocks=stocks, pattern=pattern)

def SaveToDB(dataToSave):
    try:
        
        global connection
        connection = mysql.connector.connect(host='localhost',
                                            database="OptionsData",
                                            user='root',
                                            password='Mysqlpassword')

        mycursor = connection.cursor()
        # mySql_Create_Table_Query = """CREATE TABLE oianalysis ( 
        #                           id INT AUTO_INCREMENT PRIMARY KEY,
        #                           created_at varchar(20), 
        #                           sum_call_oi int(20),
        #                           change_call_oi int(20),
        #                           sum_put_oi int(20),
        #                           change_put_oi int(20),
        #                           diff_change_Call_oi_and_change_put_oi int(25),
        #                           oi_signal varchar(20),
        #                           pcr float,
        #                           future_ltp float,
        #                           future_vwap float
        #                           )
        #                           """

        mycursor = connection.cursor()
        # mycursor.execute(mySql_Create_Table_Query)
        sql = """INSERT INTO oianalysis (created_at, sum_call_oi, change_call_oi, sum_put_oi, change_put_oi,
        diff_change_Call_oi_and_change_put_oi, oi_signal, pcr, future_ltp, future_vwap) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        mycursor.execute(sql, dataToSave)
        connection.commit()
    except mysql.connector.Error as error:
        print("Failed to create table in MySQL: {}".format(error))
    #finally:
        #if connection.is_connected():
            # cursor.close()
            # connection.close()
            # print("MySQL connection is closed")