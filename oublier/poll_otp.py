#!/usr/bin/env python2.7
#*/2 * * * * /usr/bin/python /home/arpan/gitProjects/oublier/poll_otp.py
"""The script polls the database and whenever we find a OTP that has stayed for more than 1 minutes, we remove it from the database.
	This minimises the chances of collisions while generating a unique OTP across all existing sessions"""

try:
	import sqlite3
	from twilio.rest import TwilioRestClient
	import json
	from datetime import datetime
	from pytz import *
	from geopy import geocoders
	import time
	from config import ACCOUNT_SID ,AUTH_TOKEN ,DB_PATH
except Exception as e:
	print "Import Error:"+ str(e)


conn = sqlite3.connect(DB_PATH)

cursor=conn.execute("select * from otp")
rows=cursor.fetchall()
for row in rows:
	
	time=datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f')
	diff = datetime.now()-time
	diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)
    
	
	if diff_minutes > 1:
		conn.execute("delete from otp where key ='"+row[0]+"'")
		conn.commit()

conn.commit()
conn.close()

