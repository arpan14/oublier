# Oublier
It is a web application created using Flask, HTML/CSS and SQLLite3 which will help in sending reminders to patients suffering from Amnesia. 

The project was given as a task to be completed in a span of one week and certain criterias as the following had to be met :
1. Create a (basic) web based application where one can set his phone number.  
2. Send an SMS every one hour except at night.  
3. Try resending an SMS if it fails, but retry no more than 5 times. (There is only so much you can do!).  
4. The web application should also log all the failed messages and tell an user for how many hours the application has been running.  

#Setting Up and Usage:

1. Install all packages from requirements.txt.
2. Run the script tabledef.py to generate all required tables.

3. We will set up a couple of cron jobs on our system. A cron jab can be set up on Ubuntu by the following commands.
	**crontab -e**  
	
	Append the below line to the file.

	*/2 * * * * /usr/bin/python /home/arpan/gitProjects/oublier/poll_otp.py

   This enables us to run the script poll_otp.py every 2 mins.

#Constraints:

1. Currently the application uses Twilio's Free Trial and therefore we will have to first verify a number from out Twilio Account before sending a message.

2. The app uses Google's geocoding API which has a limit of 2500 calls per day.


