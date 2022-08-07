from matplotlib.font_manager import json_load
import requests
import json
import time
import os
from datetime import datetime
from flask import Flask, escape, request, render_template, redirect, url_for, Response
import pandas as pd
# importing matplotlib module
import matplotlib.pyplot as plt
plt.style.use('default')
import io
import base64

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


app = Flask(__name__)
#app.config['DEBUG'] = True

columns = ['Time', 'Call OI Sum', 'Change in Call OI Sum', 'Put OI Sum', 'Change in Put OI Sum', 'Diff of Change in OI', 'OI Signal', 'PCR', 'Futures LTP']
rowData = []
ce_data = []
pe_data = []
top5TrendingOIData = []

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
    
    rowData.append([current_time, sum_call_OI, change_call_OI, sum_put_OI, change_put_OI,  diff_change_Call_OI_and_change_put_OI, oi_signal ,pcr, future_ltp])
    return render_template('index.html', columns=columns, rowdata=rowData)

@app.route('/trendingoi')
def trendingoi():
    # rowData = []
    # columns = ["Time", "Trending Strike Prices", "Change in OI"]
    # global top5TrendingOIData
    # top5TrendingOIData.append(trending(ce_data, pe_data))
    # for m in top5TrendingOIData:
    #     ce_or_pe = 'CE'
    #     if m["ce"].isnull().values.any():
    #         ce_or_pe = "PE"
    #     rowData.append([m["time"], str(m["strike"])+ce_or_pe, m["changeinOpenInterest"]])
    
    top5TrendingOIData = trending(ce_data, pe_data)
    top5TrendingOIData["time"] = top5TrendingOIData["time"].astype("datetime64")
    #top5TrendingOIData = top5TrendingOIData.set_index("time")

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = top5TrendingOIData["time"]
    ys = top5TrendingOIData["coi"]
    axis.plot(xs, ys)
    
    # Generate plot
    axis.grid()
    # #axis.plot(range(5), range(5), "ro-")
    
    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    
    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    
    #return Response(pngImage.getvalue(), mimetype='image/png')

    return render_template("trendingoi.html", image=pngImageB64String, oi_data=rowData, columns=columns)

#ternding OI is top 5 change in OI strike with CE/PE
def trending(allCE, allPE):
    dt1 = datetime.now()
    time_now = dt1.strftime("%H:%M:%S")
    df2= pd.DataFrame(allCE[1:])
    df3= pd.DataFrame(allPE[1:])
    df2['time'] = time_now
    df3['time'] = time_now
    df2['Ce'] = 'CE'
    df3['Pe'] = 'PE'
    df4= pd.concat([df2,df3])
    df5 = df4.sort_values(by=3 , ascending=False)
    df6 = df5[2:7]
    headers =  ["strike", "ltp", "oi", "coi", "time", "ce", "pe"]
    df6.columns = headers
    
    return df6

@app.route('/screener')
def screener():
    return render_template("screener.html")