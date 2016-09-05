import sqlite3
import uuid as uu
print uu.uuid1()

"""A utility script to display the contents of a particular table"""

conn = sqlite3.connect('test.db')
print "Opened database successfully";

cursor=conn.execute("select * from errorlogs")


'''
hs=False
for i in cursor:
	hs=True
if hs:
	print "there was record"
else :
	print "there is no record"
'''

for row in cursor:
	print row


conn.close()