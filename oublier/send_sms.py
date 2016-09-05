#!/usr/bin/env python2.7
#*/60 * * * * /usr/bin/python /home/arpan/gitProjects/oublier/send_sms.py
"""The script is run as a  cron job every 1 hour"""
try:
	import sqlite3
	from twilio.rest import TwilioRestClient
	import json
	from datetime import datetime
	from pytz import *
	from geopy import geocoders
	import time
	from config import ACCOUNT_SID ,AUTH_TOKEN ,DB_PATH,TWILIO_NUMBER,SLEEP_TIME
except:
	print "Import Error"


conn = sqlite3.connect(DB_PATH)
cursor = conn.execute("SELECT *  from activeusers")
rows=cursor.fetchall()

for row in rows:
	
	
	to_number=row[0]
	country=row[1]
	name=row[2]
	retry=0

	
	client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
	send_text='Hiii Your name is '+name+". "
	
	"""The time on the server will be different from the time on the client's timezone. We check the client's time using Google API. This is obtained by
	querying for the latitude, longitude of the place using the Country information that we have in our database. 
	The time of user is obtained and if it is less than the sleep time, we send a message."""

	try:
		g = geocoders.GoogleV3()
		place, (lat, lng) = g.geocode(country)
		timezone= g.timezone((lat,lng))
		now=datetime.now(timezone)
	except:
		now=datetime.now()
		pass
	
	errorTime=str(now)
	
	hour_minuteTime=now.strftime('%H:%M:%S')
	print hour_minuteTime
	print SLEEP_TIME
	if hour_minuteTime<SLEEP_TIME:
		"""We take into consideration failure of sending a message by Twilio. In such a case maximum of 5 retries is attempted which was a design goal."""
		while retry<5:
			f=1
			try:
				message=client.messages.create(
				    to = to_number,
				    from_ = TWILIO_NUMBER,
				    body = send_text,
				)

			except Exception as errorMessage:
				errorMessage=str(errorMessage)
				f=0
				print errorMessage
				conn.execute("insert into errorlogs (time,phone, country,name,message) values (?, ? , ? , ? , ?)",
	            (errorTime,to_number,country,name,errorMessage));
				conn.commit()
			if f==1:
				break
			retry+=1
	print row
	
conn.close()