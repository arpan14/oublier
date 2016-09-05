#!/usr/bin/python

"""Script which generates all the tables in our database."""

import sqlite3

conn = sqlite3.connect('test.db')

try:
      conn.execute('''drop table activeusers''')
      #conn.execute('''drop table otp''')
      #conn.execute('''drop table errorlogs''')
      #onn.execute('''drop table users''')
      

except Exception as e:
	print e
	pass


"""The users table which is self explanatory"""


conn.execute('''CREATE TABLE users
       (
            phone CHAR(50) PRIMARY KEY     NOT NULL,
       countrycode CHAR(50) NOT NULL,
       number CHAR(50) NOT NULL,
       country           CHAR(50)    NOT NULL,
       name           CHAR(50)    NOT NULL,
       activetime           CHAR(50)    NOT NULL,
       status           char(2)    NOT NULL,
       password char(50));''')


print "Table created successfully";


"""Table which will help us polling the database to check for OTP collisions"""

conn.execute('''CREATE TABLE otp
       (
            key CHAR(50) PRIMARY KEY     NOT NULL,
            phone CHAR(50) NOT NULL,
            activetime CHAR(50) NOT NULL      );''')

print "Table created successfully";


"""Table which has the list of users who have currently subscribed to the service. This table is polled by the cron job 
every hour and the active users are sent the messages"""
conn.execute('''CREATE TABLE activeusers
       (
            phone CHAR(50) PRIMARY KEY     NOT NULL,
       country           CHAR(50)    NOT NULL,
       name           CHAR(50)    NOT NULL);''')


print "Table created successfully";


"""The table which stores the error logs in case of failure of delievering a message by Twilio Client"""

conn.execute('''CREATE TABLE errorlogs
       (id integer primary key,
       	time CHAR(50)      NOT NULL,
       	phone CHAR(50)      NOT NULL,
       country           CHAR(50)    NOT NULL,
       name           CHAR(50)    NOT NULL,
       message CHAR(1000) NOT NULL);''')



print "Table created successfully";


conn.commit()

print conn.total_changes
conn.close()