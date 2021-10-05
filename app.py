from flask import Flask, render_template, flash,url_for, request,redirect
from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import date
from binance.client import Client
import talib
import math
import pymysql
import random
import smtplib
import datetime
import logging
import threading
import talib, numpy
from binance.client import Client
from binance.enums import *
import time
import threading
import os
import math
import random
import smtplib


from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel,db,login

def crypto_name(i):
    if "CUSD" in i[3:]:
        i = i.replace("CUSD", "")
        return i
    elif "BUSD" in i[3:]:
        i=i.replace("BUSD","")
        return i
    elif "BTC" in i[3:]:
        i=i.replace("BTC","")
        return i
    elif "USDT" in i[3:]:
        i=i.replace("USDT","")
        return i
    elif "USDC" in i[3:]:
        i = i.replace("USDC", "")
        return i
    elif "USD" in i[3:]:
        i=i[0:len(i)-3]
        return i

def random_otp():
    digits="0123456789"
    OTP=""
    for i in range(6):
        OTP+=digits[math.floor(random.random()*10)]
    return OTP
def send_email(OTP,emailid):
    otp = str(OTP) + " is your OTP"
    msg= otp
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("verify.cryptoby@gmail.com", "jemjyhtqdnflndfx")
    s.sendmail('&&&&&&&&&&&',emailid,msg)

def order(side, quantity, symbol,client ,order_type=ORDER_TYPE_MARKET):
    try:
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        return True
    except Exception as e:
        return False
def timefc(tp):
    if tp=="30m":
        return(1800)
    elif tp=="1m":
        return(60)
    elif tp=="3m":
        return(180)
    elif tp=="5m":
        return(300)
    elif tp=="15m":
        return(900)
    elif tp=="45m":
        return(2700)
    elif tp=="1hour":
        return(3600)
    elif tp=="2hours":
        return(7200)
    elif tp=="4hours":
        return(14400)
    elif tp=="6hours":
        return(21600)


def runprog0(strat,num,symbol1,tf,tp,qty,tunit,rsip,rsiob,rsios,client):
    
    client = client
    symbol=symbol1
    if tf=="1m":
        candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE)
    elif tf=="3m":
        candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_3MINUTE)
    elif tf=="5m":
        candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
    elif tf=="15m":
        candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE)
    elif tf=="30m":
        candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_30MINUTE)

    global start
    RSI_PERIOD = int(rsip)
    RSI_OVERBOUGHT = int(rsiob)
    RSI_OVERSOLD =int(rsios)
    quant=float(qty)/int(tunit)
    close = []
    purchase=[]
    candles = candles[-2:-RSI_PERIOD-2:-1]
    for i in candles:
        close.append(float(i[4]))
    in_position = 0
    b=timefc(tp)
    while ((start[num]== 1) and (b>0)):
        file1 = open("myfile.txt","a")
        now = datetime.datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        file1.write(strat+" "+"Current Time = " +current_time)
        if tf == "1m":
            c = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE)
        elif tf == "3m":
            c = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_3MINUTE)
        elif tf == "5m":
            c = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
        elif tf == "15m":
            c = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE)
        elif tf == "30m":
            c = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_30MINUTE)
        close.append(float(c[-1][4]))
        np_closes = numpy.array(close)
        rsi = talib.RSI(np_closes, RSI_PERIOD)
        last_rsi = rsi[-1]
        file1.write(symbol+" RSI VALUES "+str(rsi)+"\n")
        file1.write(symbol+ " Close Price "+str(close)+"\n")
        if last_rsi > RSI_OVERBOUGHT:
            if in_position > 0:
                purchase.sort()
                if purchase[-1]*1.01<close[-1]:
                    file1.write("Price is high therefore Selling " +symbol+"\n")
                    # put binance sell logic here
                    file1.write("purchases- " + str(purchase)+"\n")
                    order_succeeded = order(SIDE_SELL, quant, symbol,client)
                    if order_succeeded:
                        purchase.pop()
                        file1.write("Sold at price" + str(close[-1]))
                        in_position = in_position - 1
                    else :
                        file1.write("Order Expired " + symbol+"\n")
            else:
                file1.write("Price is high but we don't have quantity to sell " +symbol+"\n")

        if last_rsi < RSI_OVERSOLD:
            if in_position == tunit:
                file1.write("Already Bought !!!"+ symbol+"\n")
            else:
                order_succeeded = order(SIDE_BUY, quant, symbol,client)
                if order_succeeded:
                    file1.write("Stock Purchased " + symbol+"\n")
                    purchase.append(close[-1])
                    file1.write("Purchased at price " +str(close[-1])+"\n")
                    in_position = in_position + 1
                else :
                    file1.write("Order Expired " + symbol+"\n")
        file1.close()
        time.sleep(timefc(tf))
        b=b-timefc(tf)
        





symbols = ['BTCBUSD','BNBBUSD',  'ETHBUSD', 'LTCBUSD', 'TRXBUSD', 'XRPBUSD', 'BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'TRXUSDT', 'XRPUSDT', 'BNBBTC', 'ETHBTC', 'LTCBTC', 'TRXBTC', 'XRPBTC', 'LTCBNB', 'TRXBNB', 'XRPBNB']
symbols1=['BTCUSD', 'ETHUSD', 'XRPUSD', 'BCHUSD', 'LTCUSD', 'USDTUSD', 'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT', 'BNBUSD', 'BNBUSDT', 'ETHBTC', 'XRPBTC', 'BNBBTC', 'LTCBTC', 'BCHBTC', 'ADAUSD', 'BATUSD', 'ETCUSD', 'XLMUSD', 'ZRXUSD', 'ADAUSDT', 'BATUSDT', 'ETCUSDT', 'XLMUSDT', 'ZRXUSDT', 'LINKUSD', 'RVNUSD', 'DASHUSD', 'ZECUSD', 'ALGOUSD', 'IOTAUSD', 'BUSDUSD', 'BTCBUSD', 'DOGEUSDT', 'WAVESUSD', 'ATOMUSDT', 'ATOMUSD', 'NEOUSDT', 'NEOUSD', 'VETUSDT', 'QTUMUSDT', 'QTUMUSD', 'NANOUSD', 'ICXUSD', 'ENJUSD', 'ONTUSD', 'ONTUSDT', 'ZILUSD', 'ZILBUSD', 'VETUSD', 'BNBBUSD', 'XRPBUSD', 'ETHBUSD', 'ALGOBUSD', 'XTZUSD', 'XTZBUSD', 'HBARUSD', 'HBARBUSD', 'OMGUSD', 'OMGBUSD', 'MATICUSD', 'MATICBUSD', 'XTZBTC', 'ADABTC', 'REPBUSD', 'REPUSD', 'EOSBUSD', 'EOSUSD', 'DOGEUSD', 'KNCUSD', 'KNCUSDT', 'VTHOUSDT', 'VTHOUSD', 'USDCUSD', 'COMPUSDT', 'COMPUSD', 'MANAUSD', 'HNTUSD', 'HNTUSDT', 'MKRUSD', 'MKRUSDT', 'DAIUSD', 'ONEUSDT', 'ONEUSD', 'BANDUSDT', 'BANDUSD', 'STORJUSDT', 'STORJUSD', 'BUSDUSDT', 'UNIUSD', 'UNIUSDT', 'SOLUSD', 'SOLUSDT', 'LINKBTC', 'VETBTC', 'UNIBTC', 'EGLDUSDT', 'EGLDUSD', 'PAXGUSDT', 'PAXGUSD', 'OXTUSDT', 'OXTUSD', 'ZENUSDT', 'ZENUSD', 'BTCUSDC', 'ONEBUSD', 'FILUSDT', 'FILUSD']


# Create a Flask Instance

app = Flask(__name__)

 
# configuration

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'Anil%9129'
CLOUDSQL_DATABASE = 'crypto_by'
CLOUDSQL_CONNECTION_NAME = 'grand-appliance-328113:us-central1:crypto-by'
app.config["SQLALCHEMY_DATABASE_URI"] = (
    'mysql+pymysql://{nam}:{pas}@35.192.59.225/{dbn}?unix_socket=/cloudsql/{con}').format (
    nam=CLOUDSQL_USER,
    pas=CLOUDSQL_PASSWORD,
    dbn=CLOUDSQL_DATABASE,
    con=CLOUDSQL_CONNECTION_NAME,
)

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

@app.before_first_request
def create_all():
    db.create_all()
    
    
    

@app.route('/otp_verification', methods = ['POST', 'GET'])
def otp_verification():
    if request.method == "POST":
        if request.form.get("verify"):
            if request.form.get("otp")==current_user.otp:
                current_user.verified='1'
                db.session.commit()
                return redirect('/home')
            else:
                flash('Invalid OTP')
    return render_template('otp_verification.html')   
    
    
    
    
    


@app.route('/', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/home')
    if request.method == 'POST':
        if request.form.get("login"):
            email = request.form['email']
            user1 = UserModel.query.filter_by(email = email).first()
            if user1 is not None and user1.check_password(request.form['password']):
                login_user(user1)
                if current_user.verified=='1':
                    return redirect('/home')
                else:
                    send_email(current_user.otp,current_user.email)
                    return redirect('/otp_verification')
            else:
                flash('Invalid Credentials')
                return render_template('login1.html')
            
    
    return render_template('login1.html')

email="" 
otp=""

    

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect('/home')
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if UserModel.query.filter_by(email=email).first():
            flash('Email already registered login')
            return render_template('signup.html')
        otp = random_otp()
        user = UserModel(email=email, username=username,otp=otp,verified=0)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/editemail', methods =["GET", "POST"])
@login_required
def editmail():
    if request.method == "POST":
        if request.form.get("edit"):
            current_user.email = request.form.get("email")
            db.session.commit()
            return redirect('/profile')
    return render_template("editemail.html",user=current_user)
@app.route('/editbspk', methods =["GET", "POST"])
@login_required
def editbspk():
    if request.method == "POST":
        if request.form.get("edit"):
            current_user.binpk = request.form.get("bspk")
            db.session.commit()
            return redirect('/profile')
    return render_template("editbspk.html",user=current_user)
@app.route('/editbssk', methods =["GET", "POST"])
@login_required
def editbssk():
    if request.method == "POST":
        if request.form.get("edit"):
            current_user.binsk = request.form.get("bssk")
            db.session.commit()
            return redirect('/profile')
    return render_template("editbssk.html",user=current_user)
@app.route('/editbstsk', methods =["GET", "POST"])
@login_required
def editbstsk():
    if request.method == "POST":
        if request.form.get("edit"):
            current_user.bintsk = request.form.get("bstsk")
            db.session.commit()
            return redirect('/profile')
    return render_template("editbstsk.html",user=current_user)
@app.route('/editbstpk', methods =["GET", "POST"])
@login_required
def editbstpk():
    if request.method == "POST":
        if request.form.get("edit"):
            current_user.bintpk = request.form.get("bstpk")
            db.session.commit()
            return redirect('/profile')
    return render_template("editbstpk.html",user=current_user)

    
 
        
try:   
    list1=eval(current_user.wid_list)
except:
    list1=['BTCUSDT']

try:
    strategy=eval(current_user.strategy)
    st0=strategy[0]
    st1=strategy[1]
    st2=strategy[2]
    st3=strategy[3]
    st4=strategy[4]
    st5=strategy[5]
    st6=strategy[6]
    st7=strategy[7]
    st8=strategy[8]
    st9=strategy[9]

except:
    st0={}
    st1={}
    st2={}
    st3={}
    st4={}
    st5={}
    st6={}
    st7={}
    st8={}
    st9={}
try:   
    start=eval(current_user.start)
    a0=start[0]
    a1=start[1]
    a2=start[2]
    a3=start[3]
    a4=start[4]
    a5=start[5]
    a6=start[6]
    a7=start[7]
    a8=start[8]
    
except:
    start=[0,0,0,0,0,0,0,0,0,0]
    a0=0
    a1=0
    a2=0
    a3=0
    a4=0
    a5=0
    a6=0
    a7=0
    a8=0
    a9=0

    
  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# Create a route decorator


@app.route('/home', methods =["GET", "POST"])
@login_required
def index(): 
    if request.method == "POST":
        global list1
        if request.form.get("submit_a"):
            list1.append(request.form.get('syms'))
            current_user.wid_list = str(list1)
            db.session.commit()
        elif request.form.get("submit_b"):
            try:
                list1.pop()
            except:
                list1=[]
            current_user.wid_list = str(list1)
            db.session.commit()
    return render_template("index.html",user=current_user,list1=list1,symbols=symbols1)


@app.route('/profile',methods =["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        if request.form.get("editemail"):
            return redirect("/editemail")
        elif request.form.get("editbspk"):
            return redirect("/editbspk")
        elif request.form.get("editbssk"):
            return redirect("/editbssk")
        elif request.form.get("editbstpk"):
            return redirect("/editbstpk")
        elif request.form.get("editbstsk"):
            return redirect("/editbstsk")
    return render_template("user.html",user=current_user)


@app.route('/history', methods =["GET", "POST"])
@login_required
def history():
    pub=current_user.binpk
    sec=current_user.binsk
    client = Client(pub,sec, tld='us')
    if request.method == "POST":
        orders = client.get_all_orders(symbol=request.form.get("hist"))
        times=[]
        orderid=[]
        symbol=[]
        typ=[]
        price=[]
        quantity=[]
        cumprice=[]
        status=[]
        le=len(orders)
        orders.reverse()
        for i in orders:
            times.append(datetime.datetime.fromtimestamp(i["time"]/1000))
            orderid.append(i['orderId'])
            symbol.append(i['symbol'])
            typ.append(i["side"])
            try:
                price.append(round(float(i['cummulativeQuoteQty'])/float(i['executedQty']),2))
            except:
                price.append(0)
            quantity.append(i['executedQty'])
            cumprice.append(i['cummulativeQuoteQty'])
            status.append(i['status'])

        return render_template("history.html" ,symbols=symbols1,hist=request.form.get("hist"),time=times,orderid=orderid,symbol=symbol,typ=typ,price=price,quantity=quantity,cumprice=cumprice,status=status,le=range(le),user=current_user)

    return render_template("history.html",symbols=symbols,hist="",time=[],user=current_user)
@app.route('/historytest', methods =["GET", "POST"])
@login_required
def historytest():
    if request.method == "POST":
        try:
            pub=current_user.bintpk
            sec=current_user.bintsk
            client = Client(pub,sec, tld='us')
            client.API_URL = 'https://testnet.binance.vision/api'
            orders = client.get_all_orders(symbol=request.form.get("hist"))
            times=[]
            orderid=[]
            symbol=[]
            typ=[]
            price=[]
            quantity=[]
            cumprice=[]
            status=[]
            le=len(orders)
            orders.reverse()
            for i in orders:
                times.append(datetime.datetime.fromtimestamp(i["time"]/1000))
                orderid.append(i['orderId'])
                symbol.append(i['symbol'])
                typ.append(i["side"])
                try:
                    price.append(round(float(i['cummulativeQuoteQty'])/float(i['executedQty']),2))
                except:
                    price.append(0)
                quantity.append(i['executedQty'])
                cumprice.append(i['cummulativeQuoteQty'])
                status.append(i['status'])
        except:
            times=[]
            orderid=[]
            symbol=[]
            typ=[]
            price=[]
            quantity=[]
            cumprice=[]
            status=[]
            le=len(orders)
            

        return render_template("history.html" ,symbols=symbols,hist=request.form.get("hist"),time=times,orderid=orderid,symbol=symbol,typ=typ,price=price,quantity=quantity,cumprice=cumprice,status=status,le=range(le),user=current_user)

    return render_template("history.html",symbols=symbols,hist="",time=[],user=current_user)


@app.route('/wallet')
@login_required
def wallet():
    try:
        pub=current_user.binpk
        sec=current_user.binsk
        client = Client(pub,sec, tld='us')
        info = client.get_account()
        dict1={}
        for i in info["balances"]:
            dict1[i['asset']]= round(float(i['free']),3)
        return render_template("wallet.html",balance=dict1,user=current_user)
    except:
        return render_template("wallet.html",balance={" ": "0 Register with Binance api keys"},user=current_user)

@app.route('/wallettest')
@login_required
def wallettest():
    try:
        pub=current_user.bintpk
        sec=current_user.bintsk
        client = Client(pub,sec, tld='us')
        client.API_URL = 'https://testnet.binance.vision/api'
        info = client.get_account()
        dict1={}
        for i in info["balances"]:
            dict1[i['asset']]= round(float(i['free']),3)
        return render_template("wallet.html",balance=dict1,user=current_user)
    except:
        return render_template("wallet.html",balance={" ": "0 Register with Binance api keys"},user=current_user)

    
#@app.route('/', methods =["GET", "POST"])
#def login():
 #   if request.method == "POST":
 #       if request.form.get("login"):
 #           return render_template("index.html")
 #   return render_template("login1.html")
#@app.route('/signup', methods =["GET", "POST"])
#def signup():
#    if request.form.get("signup"):
 #       return render_template("index.html")
 #   return render_template("signup.html")
@app.route('/test', methods =["GET", "POST"])
@login_required
def test():
    pub=current_user.bintpk
    sec=current_user.bintsk
    client = Client(pub,sec, tld='us')
    client.API_URL = 'https://testnet.binance.vision/api'
    try:
        info = client.get_account()
        dict1={}
        for i in info["balances"]:
            dict1[i['asset']]= round(float(i['free']),3)
    except:
        dict1={}
    global a1,a2,a3,a4,a5,a6,a7,a8,a9,a0,st0,st1,st2,st3,st4,st5,st6,st7,st8,st9,start
    if request.method == "POST":
        global list1
        if request.form.get("save"):
            tu=1
            try:
                pub=request.form.get("bspk")
                sec=request.form.get("bssk")
                client = Client(pub,sec, tld='us')
                client.API_URL = 'https://testnet.binance.vision/api'
                info = client.get_account()
            except:
                flash("Invalid API keys")
                tu=0
            if tu==1:
                current_user.bintpk=request.form.get("bspk")
                current_user.bintsk=request.form.get("bssk")
                db.session.commit()
            return render_template("test-test.html",symbols=symbols1,list1 =list1,balance=dict1,test="active",user=current_user)
     
        elif request.form.get("submit_a"):
            list1.append(request.form.get('syms'))
            current_user.wid_list = str(list1)
            db.session.commit()
        elif request.form.get("submit_b"):
            try:
                list1.pop()
            except:
                list1=[]
            current_user.wid_list = str(list1)
            db.session.commit()
        elif request.form.get("act00"):
            st0={"strategy":request.form.get("0f1"),"symbol":request.form.get("0f2"),"timeframe":request.form.get("0f8"),"timeperiod":request.form.get("0f9"),"quantity":request.form.get("0f3"),"tradeunits":request.form.get("0f4"),"rsiperiod":request.form.get("0f5"),"rsiob":request.form.get("0f6"),"rsios":request.form.get("0f7")}
            start[0]=1
            a0=start[0]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread0= threading.Thread(target=runprog0 , args=([st0["strategy"],0,st0["symbol"],st0["timeframe"],st0["timeperiod"],st0["quantity"],st0["tradeunits"],st0["rsiperiod"],st0["rsiob"],st0["rsios"],client]))
            thread0.start()
            return render_template("test-test.html",symbols=symbols,list1=list1, test="active",balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act0"):
            start[0]=0
            a0=start[0]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("test-test.html",symbols=symbols,list1=list1, test="active",balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act11"):
            st1={"strategy":request.form.get("1f1"),"symbol":request.form.get("1f2"),"timeframe":request.form.get("1f8"),"timeperiod":request.form.get("1f9"),"quantity":request.form.get("1f3"),"tradeunits":request.form.get("1f4"),"rsiperiod":request.form.get("1f5"),"rsiob":request.form.get("1f6"),"rsios":request.form.get("1f7")}
            start[1]=1
            a1=start[1]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread1= threading.Thread(target=runprog0 , args=([st1["strategy"],1,st1["symbol"],st1["timeframe"],st1["timeperiod"],st1["quantity"],st1["tradeunits"],st1["rsiperiod"],st1["rsiob"],st1["rsios"],client]))
            thread1.start()
            
            return render_template("test-test.html",symbols=symbols,test="active",list1=list1,balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act1"):
            start[1]=0
            a1=start[1]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("test-test.html",symbols=symbols,list1=list1,balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,test="active",user=current_user)
        elif request.form.get("act22"):
            
            st2={"strategy":request.form.get("2f1"),"symbol":request.form.get("2f2"),"timeframe":request.form.get("2f8"),"timeperiod":request.form.get("2f9"),"quantity":request.form.get("2f3"),"tradeunits":request.form.get("2f4"),"rsiperiod":request.form.get("2f5"),"rsiob":request.form.get("2f6"),"rsios":request.form.get("2f7")}
            start[2]=1
            a2=start[2]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread2= threading.Thread(target=runprog0 , args=([st2["strategy"],2,st2["symbol"],st2["timeframe"],st2["timeperiod"],st2["quantity"],st2["tradeunits"],st2["rsiperiod"],st2["rsiob"],st2["rsios"],client]))
            thread2.start()
            return render_template("test-test.html",symbols=symbols,test="active",list1=list1,balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act2"):
            start[2]=0
            a2=start[2]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("test-test.html",symbols=symbols,test="active",list1=list1,balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act33"):
            st3={"strategy":request.form.get("3f1"),"symbol":request.form.get("3f2"),"timeframe":request.form.get("3f8"),"timeperiod":request.form.get("3f9"),"quantity":request.form.get("3f3"),"tradeunits":request.form.get("3f4"),"rsiperiod":request.form.get("3f5"),"rsiob":request.form.get("3f6"),"rsios":request.form.get("3f7")}
            start[3]=1
            a3=start[3]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread3= threading.Thread(target=runprog0,args=([st3["strategy"],3,st3["symbol"],st3["timeframe"],st3["timeperiod"],st3["quantity"],st3["tradeunits"],st3["rsiperiod"],st3["rsiob"],st3["rsios"],client]))
            thread3.start()
            return render_template("test-test.html",symbols=symbols,list1=list1,test="active",balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act3"):
            
            start[3]=0
            a3=start[3]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("test-test.html",symbols=symbols,list1=list1,test="active",balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act44"):
            
            st4={"strategy":request.form.get("4f1"),"symbol":request.form.get("4f2"),"timeframe":request.form.get("4f8"),"timeperiod":request.form.get("4f9"),"quantity":request.form.get("4f3"),"tradeunits":request.form.get("4f4"),"rsiperiod":request.form.get("4f5"),"rsiob":request.form.get("4f6"),"rsios":request.form.get("4f7")}
            start[4]=1
            a4=start[4]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread4= threading.Thread(target=runprog0 , args=([st4["strategy"],4,st4["symbol"],st4["timeframe"],st4["timeperiod"],st4["quantity"],st4["tradeunits"],st4["rsiperiod"],st4["rsiob"],st4["rsios"],client]))
            thread4.start()
            return render_template("test-test.html",symbols=symbols,list1=list1,test="active",balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act4"):
            start[4]=0
            a4=start[4]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("test-test.html",symbols=symbols,list1=list1,test="active",balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        
    return render_template("test-test.html",symbols=symbols,list1=list1,balance=dict1,test="active",a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)


@app.route('/trade', methods =["GET", "POST"])
@login_required
def trade():
    
    pub=current_user.binpk
    sec=current_user.binsk
    client = Client(pub,sec, tld='us')
    try:
        info = client.get_account()
        dict1={}
        for i in info["balances"]:
            dict1[i['asset']]= round(float(i['free']),3)
    except:
        dict1={}
    global a5,a6,a7,a8,a9,st0,st1,st2,st3,st4,st5,st6,st7,st8,st9,start
    if request.method == "POST":
        if request.form.get("save"):
            tu=1
            try:
                pub=request.form.get("bspk")
                sec=request.form.get("bssk")
                client = Client(pub,sec, tld='us')
                client.API_URL = 'https://testnet.binance.vision/api'
                info = client.get_account()
            except:
                flash("Invalid API keys")
                tu=0
            if tu==1:
                current_user.bintpk=request.form.get("bspk")
                current_user.bintsk=request.form.get("bssk")
                db.session.commit()
            return render_template("trade-trade.html",symbols=symbols1,list1 =list1,trade="active",balance=dict1,user=current_user)
        elif request.form.get("submit_a"):
            list1.append(list1[0])
            return render_template("trade-trade.html",symbols=symbols1,list1 =list1,trade="active",balance=dict1,user=current_user)
        elif request.form.get("act00"):
            st5={"strategy":request.form.get("0f1"),"symbol":request.form.get("0f2"),"timeframe":request.form.get("0f8"),"timeperiod":request.form.get("0f9"),"quantity":request.form.get("0f3"),"tradeunits":request.form.get("0f4"),"rsiperiod":request.form.get("0f5"),"rsiob":request.form.get("0f6"),"rsios":request.form.get("0f7")}
            start[5]=1
            a5=start[5]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread10= threading.Thread(target=runprog0 , args=([st5["strategy"],5,st5["symbol"],st5["timeframe"],st5["timeperiod"],st5["quantity"],st5["tradeunits"],st5["rsiperiod"],st5["rsiob"],st5["rsios"],client]))
            thread10.start()
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        elif request.form.get("act0"):
            start[5]=0
            a5=start[5]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        elif request.form.get("act11"):
            st6={"strategy":request.form.get("1f1"),"symbol":request.form.get("1f2"),"timeframe":request.form.get("1f8"),"timeperiod":request.form.get("1f9"),"quantity":request.form.get("1f3"),"tradeunits":request.form.get("1f4"),"rsiperiod":request.form.get("1f5"),"rsiob":request.form.get("1f6"),"rsios":request.form.get("1f7")}
            start[6]=1
            a6=start[6]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread11= threading.Thread(target=runprog0 , args=([st6["strategy"],6,st6["symbol"],st6["timeframe"],st6["timeperiod"],st6["quantity"],st6["tradeunits"],st6["rsiperiod"],st6["rsiob"],st6["rsios"],client]))
            thread11.start()
            
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        elif request.form.get("act1"):
            start[6]=0
            a6=start[6]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        elif request.form.get("act22"):
            
            st7={"strategy":request.form.get("2f1"),"symbol":request.form.get("2f2"),"timeframe":request.form.get("2f8"),"timeperiod":request.form.get("2f9"),"quantity":request.form.get("2f3"),"tradeunits":request.form.get("2f4"),"rsiperiod":request.form.get("2f5"),"rsiob":request.form.get("2f6"),"rsios":request.form.get("2f7")}
            start[7]=1
            a7=start[7]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread12= threading.Thread(target=runprog0 , args=([st7["strategy"],7,st7["symbol"],st7["timeframe"],st7["timeperiod"],st7["quantity"],st7["tradeunits"],st7["rsiperiod"],st7["rsiob"],st7["rsios"],client]))
            thread12.start()
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        elif request.form.get("act2"):
            start[7]=0
            a7=start[7]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        elif request.form.get("act33"):
            st8={"strategy":request.form.get("3f1"),"symbol":request.form.get("3f2"),"timeframe":request.form.get("3f8"),"timeperiod":request.form.get("3f9"),"quantity":request.form.get("3f3"),"tradeunits":request.form.get("3f4"),"rsiperiod":request.form.get("3f5"),"rsiob":request.form.get("3f6"),"rsios":request.form.get("3f7")}
            start[8]=1
            a8=start[8]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread13= threading.Thread(target=runprog0,args=([st8["strategy"],8,st8["symbol"],st8["timeframe"],st8["timeperiod"],st8["quantity"],st8["tradeunits"],st8["rsiperiod"],st8["rsiob"],st8["rsios"],client]))
            thread13.start()
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        elif request.form.get("act3"):
            
            start[8]=0
            a8=start[8]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("trade-trade.html",symbols=symbols,list1=list1,trade="active",balance=dict1,a0=a0,a1=a1,a2=a2,a3=a3,a4=a4,st0=st0,st1=st1,st2=st2,st3=st3,st4=st4,user=current_user)
        elif request.form.get("act44"):
            
            st9={"strategy":request.form.get("4f1"),"symbol":request.form.get("4f2"),"timeframe":request.form.get("4f8"),"timeperiod":request.form.get("4f9"),"quantity":request.form.get("4f3"),"tradeunits":request.form.get("4f4"),"rsiperiod":request.form.get("4f5"),"rsiob":request.form.get("4f6"),"rsios":request.form.get("4f7")}
            start[9]=1
            a9=start[9]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            thread14= threading.Thread(target=runprog0 , args=([st9["strategy"],9,st9["symbol"],st9["timeframe"],st9["timeperiod"],st9["quantity"],st9["tradeunits"],st9["rsiperiod"],st9["rsiob"],st9["rsios"],client]))
            thread14.start()
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        elif request.form.get("act4"):
            start[9]=0
            a9=start[9]
            current_user.strategy=str([st0,st1,st2,st3,st4,st5,st6,st7,st8,st9])
            current_user.start=str(start)
            db.session.commit()
            return render_template("trade-trade.html",symbols=symbols1,list1=list1, trade="active",balance=dict1,a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)
        
    return render_template("trade-trade.html",symbols=symbols1,list1=list1, balance=dict1,trade="active", a0=a5,a1=a6,a2=a7,a3=a8,a4=a9,st0=st5,st1=st6,st2=st7,st3=st8,st4=st9,user=current_user)













@app.route('/spot', methods =["GET", "POST"])
@login_required
def spot():
    try:
        a=crypto_name(request.form.get("syms"))
    except:
        a="BTC"
    try:
        pub=current_user.binpk
        sec=current_user.binsk
        client = Client(pub,sec, tld='us')
        info = client.get_account()
        dict1={}
        for i in info["balances"]:
            dict1[i['asset']]= round(float(i['free']),3)
    except:
        dict1={}
    
    ll=0
    if request.method == "POST":
        if request.form.get("save"):
            tu=1
            try:
                pub=request.form.get("bspk")
                sec=request.form.get("bssk")
                client = Client(pub,sec, tld='us')
                info = client.get_account()
            except:
                flash("Invalid API keys")
                tu=0
            if tu==1:
                current_user.bintpk=request.form.get("bspk")
                current_user.bintsk=request.form.get("bssk")
                db.session.commit()
            return render_template("spot-trade.html" ,a=a,spot="active",symbols=symbols,balance=dict1,sym="BTCUSDT",user=current_user)
        elif request.form.get("submit_t"):
            a=crypto_name(request.form.get("syms"))
            return render_template("spot-trade.html",a=a ,spot="active",symbols=symbols,balance=dict1,sym=request.form.get("syms"),user=current_user) 
        elif request.form.get("submit_buy"):
            try:
                ll=0
                order_succeeded = order(SIDE_BUY, float(request.form.get("buy_qt")), request.form.get("syms"),client)
                if order_succeeded:
                    flash('Order Placed')
                    info = client.get_account()
                    ll=1
                    dict1={}
                    for i in info["balances"]:
                        dict1[i['asset']]= round(float(i['free']),3)
                    return render_template("spot-trade.html" ,a=a,symbols=symbols,spot="active",balance=dict1,sym=request.form.get("syms"),ll=ll,user=current_user)
                else:
                    ll=0
                    render_template("spot-trade.html" ,a=a,symbols=symbols,balance=dict1,spot="active",sym=request.form.get("syms"),ll=ll,user=current_user)
            except:
                flash('Enter Valid Quantity to Buy')
                return render_template("spot-trade.html" ,a=a,spot="active",symbols=symbols,balance=dict1,sym=request.form.get("syms"),user=current_user)
            return render_template("spot-trade.html" ,a=a,symbols=symbols,spot="active",balance=dict1,sym="BTCUSDT",user=current_user)
        elif request.form.get("submit_sell"):
            try:
                ll=0
                order_succeeded = order(SIDE_SELL,float(request.form.get("sell_qt")), request.form.get("syms"),client)
                if order_succeeded:
                    flash('Order Placed')
                    ll=1
                    info = client.get_account()
                    dict1={}
                    for i in info["balances"]:
                        dict1[i['asset']]= round(float(i['free']),3)
                    return render_template("spot-trade.html" ,a=a,symbols=symbols,spot="active",balance=dict1,sym=request.form.get("syms"),ll=ll,user=current_user)
                else:
                    ll=0
                    render_template("spot-trade.html" ,a=a,symbols=symbols,balance=dict1,spot="active",sym=request.form.get("syms"),ll=ll,user=current_user)
            except:
                flash('Enter Valid Quantity to Sell')
                return render_template("spot-trade.html" ,a=a,symbols=symbols,balance=dict1,spot="active",sym=request.form.get("syms"),ll=ll,user=current_user)
            return render_template("spot-trade.html" ,a=a,symbols=symbols,spot="active",balance=dict1,sym=request.form.get("syms"),user=current_user)
    return render_template("spot-trade.html" ,a=a,symbols=symbols,spot="active",balance=dict1,sym="BTCUSDT",user=current_user)



















@app.route('/spottest', methods =["GET", "POST"])
@login_required
def spottest():
    try:
        a=crypto_name(request.form.get("syms"))
    except:
        a="BTC"
    try:
        pub=current_user.bintpk
        sec=current_user.bintsk
        client = Client(pub,sec, tld='us')
        client.API_URL = 'https://testnet.binance.vision/api'
        info = client.get_account()
        dict1={}
        for i in info["balances"]:
            dict1[i['asset']]= round(float(i['free']),3)
    except:
        dict1={}
    
    ll=0
    if request.method == "POST":
        if request.form.get("save"):
            tu=1
            try:
                pub=request.form.get("bstpk")
                sec=request.form.get("bstsk")
                client = Client(pub,sec, tld='us')
                client.API_URL = 'https://testnet.binance.vision/api'
                info = client.get_account()
            except:
                flash("Invalid API keys")
                tu=0
            if tu==1:
                current_user.bintpk=request.form.get("bstpk")
                current_user.bintsk=request.form.get("bstsk")
                db.session.commit()
            return render_template("spot-test.html" ,a=a,spottest="active",symbols=symbols,balance=dict1,sym="BTCUSDT",user=current_user)
        elif request.form.get("submit_t"):
            a=crypto_name(request.form.get("syms"))
            return render_template("spot-test.html",a=a ,spottest="active",symbols=symbols,balance=dict1,sym=request.form.get("syms"),user=current_user) 
        elif request.form.get("submit_buy"):
            try:
                ll=0
                order_succeeded = order(SIDE_BUY, float(request.form.get("buy_qt")), request.form.get("syms"),client)
                if order_succeeded:
                    flash('Order Placed')
                    info = client.get_account()
                    ll=1
                    dict1={}
                    for i in info["balances"]:
                        dict1[i['asset']]= round(float(i['free']),3)
                    return render_template("spot-test.html" ,a=a,symbols=symbols,balance=dict1,spottest="active",sym=request.form.get("syms"),ll=ll,user=current_user)
                else:
                    ll=0
                    render_template("spot-test.html" ,a=a,symbols=symbols,balance=dict1,spottest="active",sym=request.form.get("syms"),ll=ll,user=current_user)
            except:
                flash('Enter Valid Quantity to Buy')
                return render_template("spot-test.html" ,a=a,symbols=symbols,balance=dict1,spottest="active",sym=request.form.get("syms"),user=current_user)
            return render_template("spot-test.html" ,a=a,symbols=symbols,balance=dict1,spottest="active",sym="BTCUSDT",user=current_user)
        elif request.form.get("submit_sell"):
            try:
                ll=0
                order_succeeded = order(SIDE_SELL,float(request.form.get("sell_qt")), request.form.get("syms"),client)
                if order_succeeded:
                    flash('Order Placed')
                    ll=1
                    info = client.get_account()
                    dict1={}
                    for i in info["balances"]:
                        dict1[i['asset']]= round(float(i['free']),3)
                    return render_template("spot-test.html" ,a=a,symbols=symbols,spottest="active",balance=dict1,sym=request.form.get("syms"),ll=ll,user=current_user)
                else:
                    ll=0
                    render_template("spot-test.html" ,a=a,symbols=symbols,spottest="active",balance=dict1,sym=request.form.get("syms"),ll=ll,user=current_user)
            except:
                flash('Enter Valid Quantity to Sell')
                return render_template("spot-test.html" ,a=a,symbols=symbols,balance=dict1,spottest="active",sym=request.form.get("syms"),ll=ll,user=current_user)
            return render_template("spot-test.html" ,a=a,symbols=symbols,balance=dict1,spottest="active",sym=request.form.get("syms"),user=current_user)
    return render_template("spot-test.html" ,a=a,symbols=symbols,spottest="active",balance=dict1,sym="BTCUSDT",user=current_user)
if __name__ == "__main__":
    app.run()
