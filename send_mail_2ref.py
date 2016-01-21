#last script to launch
import smtplib
from email.mime.text import MIMEText
from email.header    import Header
import psycopg2
import getpass
import time

passdb = getpass.getpass("Input password DB: ") #Connection to the DB
try:
    conn=psycopg2.connect(dbname='cwjobs' , user ='postgres', host='localhost', password= passdb)
    print("Connection OK")
except psycopg2.Error as e:
    print("I am unable to connect to the database.")
    print(e.pgcode)
    print(e.pgerror)

cur = conn.cursor()
query = "SELECT contact_p,jid FROM cwjobs WHERE applied= true" #send mail where I'm applied
cur.execute(query)

smtp_host = 'smtp.mail.yahoo.com'  # yahoo
print("Login to your mailbox to collect application confirmation mail!")

umail = input("User: ")
password = getpass.getpass()
s = smtplib.SMTP(smtp_host, 587, timeout=10)
s.set_debuglevel(1)
z=0
try:
    s.starttls()
    s.login(umail, password)
    
    for r in cur.fetchall():
        name = r[0].split('.')[0] 
        bodym = " Dear "+ name +",\nThis application has been sent with scripts written in python using several libraries such as BeautifulSoup, Selenium, Requests and Psycopg2...I would show that I can manage rather well these kind of stuffs. You can find on github --> https://github.com/MMorini86/Automatic-application-cwjobs the source code of the  scripts that I used to apply for this position.\n Looking forward to hearing from you. \n Best regards\n Matteo Morini\n Mail: "+ umail +" \n Mobile: myMobile"""
        
        subj = "README: Note on job application (cwjob reference n."+str(r[1])+ ") - Matteo Morini"
        if z == 0:
            recipients_emails = r[0]+", ma_mo@tiscali.it"
            z=z+1
        else:
            recipients_emails = r[0]
        print(recipients_emails)
        print(name)
        msg = MIMEText(bodym, 'plain', 'utf-8')
        msg['Subject'] = Header(subj, 'utf-8')
        msg['From'] = umail
        msg['To'] = recipients_emails
        s.sendmail(msg['From'], recipients_emails, msg.as_string())
        time.sleep(5)
finally:
    cur.close()
    conn.close()
    s.quit()
    
