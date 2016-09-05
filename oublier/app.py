try:
    from flask import Flask, render_template, json, request,flash,session
    from werkzeug import generate_password_hash, check_password_hash
    import sqlite3
    from twilio.rest import TwilioRestClient
    import json
    from datetime import datetime
    from pytz import *
    from geopy import geocoders
    import time    
    import random
    import string
    import itertools
    from config import ACCOUNT_SID ,AUTH_TOKEN ,DB_PATH,TWILIO_NUMBER,OTP_TIMEOUT
except Exception as e:
    print "Import Error"+ str(e)


app = Flask(__name__)
app.debug=True
app.secret_key = 'super secret key'

"""Returns all rows from a cursor as a list of dicts"""
    
def dictfetchall(cursor):
    desc = cursor.description
    return [dict(itertools.izip([col[0] for col in desc], row)) 
            for row in cursor.fetchall()]

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')
@app.route('/showLogs')
def showLogs():
    conn = sqlite3.connect(DB_PATH)    
    query="select * from errorlogs where phone='"+session["phone"]+"'"    
    cursor = conn.execute(query)
    results = dictfetchall(cursor)
    json_results = json.dumps(results)
    conn.close()
    return json_results

@app.route('/showTime')
def showTime():
    conn = sqlite3.connect(DB_PATH)    
    query="select activetime from users where phone='"+session["phone"]+"'"    
    cursor = conn.execute(query)

    for row in cursor:
        _activetime=row[0]
        print _activetime
    if _activetime=="--":
        time="Application not running. Please Subscribe"
        return render_template("time.html",time=time)
    else:
        _activetime=datetime.strptime(_activetime, "%Y-%m-%d %H:%M:%S.%f")

    diff = datetime.now()-_activetime
    diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)
    time="Application running since "+str(diff_minutes) +" minutes"
    return render_template("time.html",time=time)


"""View to subscribe to the service. By default users are subscribed when they sign up for the service."""

@app.route('/subscribe')
def subscribe():
    conn = sqlite3.connect(DB_PATH)
    query="update users set status='1' where phone='"+session["phone"]+"'"    
    cursor = conn.execute(query)
    
    try:
        conn.execute("insert into activeusers (phone,country,name) values (?,?,?)",(session["phone"],session["country"],session["name"]))
    except Exception as e:
        subscription_message="User Already Subscribed"
        return render_template("profile.html",subscription_message=subscription_message)
    
    _activetime=datetime.now()

    query="update users set activetime='"+str(_activetime)+"' where phone='"+session["phone"]+"'"    
    cursor = conn.execute(query)
    
    conn.commit()
    conn.close()
    
    subscription_message="Successfully Subscribed"
    return render_template("profile.html",subscription_message=subscription_message,name=session["name"])


"""View to un-subscribe the service. If users doesn't want the hourly text reminder he/she can unsubscribe"""

@app.route('/unsubscribe')
def unsubscribe():
    conn = sqlite3.connect(DB_PATH)
    query="update users set status='0' where phone='"+session["phone"]+"'"    
    
    cursor = conn.execute(query)
    
    try:
        conn.execute("delete from activeusers where phone='"+session["phone"]+"'")
    except Exception as e:
        subscription_message="User Already Un-Subscribed"
        return render_template("profile.html",subscription_message=subscription_message,name=session["name"])
    
    
    query="update users set activetime='--' where phone='"+session["phone"]+"'"    
    cursor = conn.execute(query)
    
    conn.commit()
    conn.close()
    subscription_message="Successfully Un-Subscribed"
    return render_template("profile.html",subscription_message=subscription_message,name=session["name"])


"""For generating OTP we first poll the database to see if a generated OTP is already in use for one of the current sessions, if not
we assing it as the current session OTP. For our case, the OTP is combination of uppercase,lowercase and numeric characters."""


def generate_otp():
    print "inside OTP generator"
    done=True
    while done:
        otp=''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(6))
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.execute("insert into otp (key,phone,activetime) values (?,?,?)",(otp,session["phone"],str(datetime.now())))
            session["otp"]=otp
            session["update"]=datetime.now()
            conn.commit()
            conn.close()
            print otp
            done=False
        except Exception as e:
            pass
        
"""The following function is to validate OTP. Here we have set OTP_TIMEOUT as 40 seconds, after which OTP gets regenerated. In case of incorrect input of OTP,
the OTP gets regenerated."""


@app.route('/checkOTP',methods=['POST','GET'])
def checkOTP():
    _otp =request.form['inputOTP']    
    conn = sqlite3.connect(DB_PATH)
    
    time_difference=datetime.now()-session["update"]
    error=None
    if time_difference.seconds >OTP_TIMEOUT:
        conn.execute("delete from otp where phone='"+session["phone"]+"'")
        conn.commit()
        conn.close()
        
        generate_otp()
        client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
        try:
            message=client.messages.create(
                to = session["phone"],
                from_ = TWILIO_NUMBER,
                body = 'OTP :  '+ session["otp"],
            )
        except Exception as errorMessage:
            error="Waiting for Admin to verify number"
            print error
            return render_template("signin.html",error=error)
        error="OTP expired. Re-enter New OTP"
        return render_template("otp.html",error=error)
    if _otp==session["otp"]:
        name=session["name"]
        return render_template("profile.html",name=name)
    else:
        generate_otp()
        client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
        try:
            message=client.messages.create(
                to = session["phone"],
                from_ = TWILIO_NUMBER,
                body = 'OTP :  '+ session["otp"],
            )
        except Exception as errorMessage:
            error="Waiting for Admin to verify number"
            print error
            return render_template("signin.html",error=error)
        return render_template("otp.html")    
    
    
"""On logging out, current session is cleared"""

@app.route('/logOut',methods=['POST','GET'])
def logOut():
    session.clear()        
    return render_template("index.html")


@app.route('/signIn',methods=['POST','GET'])
def signIn():
    print "in Sign In"
    _number = request.form['inputNumber']
    conn = sqlite3.connect(DB_PATH)
    query="select * from users where number='"+_number+"'"
    cursor = conn.execute(query)
    hasresults=False
    for row in cursor:
        session["phone"]=row[0]
        session["countrycode"]=row[1]
        session["number"]=row[2]
        session["country"]=row[3]
        session["name"]=row[4]
        
        hasresults=True
    error=None
    conn.close()
    if not hasresults:
        error="No such number exists"
        return render_template("signin.html",error=error)
    else:
        generate_otp()
        client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
        try:
            message=client.messages.create(
                to = session["phone"],
                from_ = TWILIO_NUMBER,
                body = 'OTP :  '+ session["otp"],
            )
        except Exception as errorMessage:
            error="Waiting for Admin to verify number"
            print error
            return render_template("signin.html",error=error)
        return render_template("otp.html",error=error)


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        error=None
        if request.method =='POST':
            conn = sqlite3.connect(DB_PATH)
            
            _name = request.form['inputName']
            _countrycode = request.form['inputCountryCode']
            _number = request.form['inputNumber']
            _password = request.form['inputPassword']
            _hashed_password = str(generate_password_hash(_password))
            _country= request.form['inputCountry']     
            _phone="+"+_countrycode+_number
            _activetime=datetime.now()
            _status="1"

            
            if _name and _number and _password and _country:    
                
                try:
                    cursor = conn.execute("insert into users (phone,countrycode,number,country,name,activetime,status,password) values (?,?,?,?,?,?,?,?)",(_phone,_countrycode,_number,_country,_name,_activetime,_status,_hashed_password))
                except Exception as e:
                    print e
                    error="User not created successfully"
                    return render_template("signup.html",error=error)
                try:
                    conn.execute("insert into activeusers (phone,country,name) values (?,?,?)",(_phone,_country,_name))
                except Exception as e:
                    print e    
        
                
                conn.commit()    
                cursor.close()
                conn.close() 
                
                error="User created successfully"
                return render_template("signup.html",error=error)

            else:
                error="Enter all values"
                return render_template("signup.html",error=error)
        else :
            return render_template('signup.html',error=error)
        
    except Exception as e:
        print e
        return json.dumps({'error':str(e)})
        
if __name__ == "__main__":
    app.run(port=5002)
