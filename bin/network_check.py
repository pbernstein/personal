#!/usr/bin/python


############################################################ 
#
#
#  network_check.py
#
#  Ping the internet. Log failures. Tattle when I am connected again
#  The assumption is that I am called via cron every 5 min or so
#
#  Update the "unique" var to something meaningful
#
#  Something like:
#	*/5 * * * *  <path>/network_check.py  > /tmp/crontab-network_check.log 2>/tmp/crontab-network_check.err
#
#
############################################################ 

import os
import datetime
import urllib2
import shutil
import send_generic_email_attachment as send_email
import subprocess

url = "http://www.google.com"
email = "pbernstein@gmail.com"
#email = "payton.bissell@gmail.com"
instant = str(datetime.datetime.now()).replace(" ","-")
unique = "Instance Name"


print "Network Check"
print "============="
print instant


try:
	ip_object = urllib2.urlopen("https://api.ipify.org", timeout = 5) # I don't count this as my network test becuase I don't trust this site to be up
	ip = ip_object.read()
	ip = ip.replace("\n","") # Trim the newline
except:
	ip = "Not found"
	

# Scrape the log

try:	
	f = open("/tmp/network_check",'r') # Look for a file to read
	contents =  f.readlines()
	previous_check_time = contents[0].replace("\n","") # Trim the newline
	previous_success_time = contents[1].replace("\n","") # Trim the newline
	previous_check_status = contents[2].replace("\n","") # Trim the newline
	f.close()

except:
	# Clean environment, wahoo!
	previous_check_time = "NA"
	previous_success_time = "NA"
	previous_check_status = "NA"
	
	

try:

	# Can we hit the URL?
	
	FNULL = open(os.devnull, 'w')
	subprocess.check_call(['ping','-w','2','8.8.8.8'], stdout=FNULL, stderr=subprocess.STDOUT)
	print "Successful connection"


	# Is this the first successful hit AFTER a period of failure?

	if previous_check_status == "FAIL":
		# We're back!
		# Send an email
		
		try:


			# Scrape the contents of the failure log
			f = open("/tmp/network_check_fail_log","r")
			body = f.read()

			# If this is huge, take only the first 20 rows, then the last 20 rows

			body_list = body.split("\n")
			if len(body_list) > 50:
				prepped_body_list = body_list[:20] + ["","   XXXXX Omitted for clarity XXXXXXX   ",""] + body_list[-20:]
				body = "\n".join(prepped_body_list)


		except:
			body = "Failed to read failure log."

		body = """I was down for a while.  The last successful test before the failure was: """+previous_success_time+"""

	Error log:	
	==========	
	"""+body


		send_email.mail(email,unique+" Network notification: Back Online", body, "")			
		
		
		
		# Clean up
		try:
			# Move the file out of the way for the next batch of failures
			shutil.move("/tmp/network_check_fail_log","/tmp/network_check_fail_log."+instant)
			
		except:		
			f.open("/tmp/network_check_admin")
			f.write("I failed to move the network_check_fail_log out of the way at "+instant+". You should look into that.")
			f.close()	


	#  Was the machine rebooted?

	if previous_check_status == "NA":
		# We're live!
		# Send an email
		send_email.mail(email,unique+" Network notification: Email Test", "Start up successful. Everything appears to be working.\nIP: "+ip, "")			


	# log it
	f = open("/tmp/network_check",'w') # Create/Overwrite a new file
	f.write("\n")
	f.write(instant)
	f.write("\n")
	f.write("Success")
	f.write("\n")
	f.close()	

	

except:

	# Failed to hit the url


	# Did we have a successful connection before?

	# Make a fancy log	

	body = """
	Connection failed
	================
	Failed url: """+url+"""
	Failed at:  """+instant+"""
	Connection worked as recently as: """+previous_success_time+"""
	================

	"""

	print body

	# Save your fancy log to a file that will be appended to with each failure 
	f = open("/tmp/network_check_fail_log",'a') # Append to an existing file
	f.write(body)
	f.close()

	
	
	# log it

	f = open("/tmp/network_check",'w') # Create a new file
	f.write(instant)
	f.write("\n")
	f.write(previous_success_time)
	f.write("\n")
	f.write("FAIL")
	f.write("\n")
	f.close()	



	




