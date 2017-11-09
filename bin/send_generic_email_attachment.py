#!/usr/bin/python

import smtplib 
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
import sys

gmail_user = ""  # add user name
gmail_pwd = ""   # add pw

def mail(to, subject, text, attach=""):
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        part = MIMEBase('application', 'octet-stream')
        if attach != "":
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attach, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
            msg.attach(part)
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmail_user, gmail_pwd)
        mailServer.sendmail(gmail_user, to, msg.as_string())
        #Should be mailServer.quit(), but that crashes...
        mailServer.close()



def main(user,subject,header,attachment):
	mail(str(user),
        	str(subject),
	        str((os.linesep).join([header])),
	      	str(attachment))
	

if __name__ == '__main__':
	user = sys.argv[1]
	subject = sys.argv[2]
	header = sys.argv[3]
	attachment = sys.argv[4]
	main(user,subject,header,attachment) 


