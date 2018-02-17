#!/usr/bin/python
#   File : GateGuard.py
#   Author: Neechie
#   Date: 17/02/2018
#   Description : Emailer function to be used by GateGuard.py
#   URL : 
#   Version : 1.0
#

#Emailer function to notify staff 

def send_email(user, pwd, recipient, subject, body, name):
    import smtplib
    import time

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'Successfully sent email at '+ time.strftime("%T, %d/%m/%y") 
    except:
        print "Failed to send email"
