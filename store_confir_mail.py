#third script to launch
import imaplib
import email
import getpass
from email.parser import HeaderParser
import datetime
import sys
from bs4 import BeautifulSoup
import psycopg2
import re

def pulisci(s):
    return re.sub('[^a-zA-Z0-9-£ ()^/|^&]', '', s)

print("Login to your mailbox to collect application confirmation mail!")
user = input("User: ")
password = getpass.getpass()

mail = imaplib.IMAP4_SSL('imap.mail.yahoo.com')
mail.login(user, password)
mail.list()
mail.select("Inbox")

passdb = getpass.getpass("Input password DB: ")
try:
    conn=psycopg2.connect(dbname='cwjobs',  user ='postgres', host='localhost', password= passdb)
    print("Connection OK")
except psycopg2.Error as e:
    print("I am unable to connect to the database.")
    print(e.pgcode)
    print(e.pgerror)
    
cur = conn.cursor()

result, data = mail.search(None, '(FROM cwjobs@cwjobsmail.co.uk)') #Look for mail from cwj...



for num in data[0].split(): 
    typ, dat = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(dat[0][1])
    
    if str(msg['Subject']).strip().find('Application confirmation') == 0 : #consider only mail regardind the application confirmation
        subj = msg['Subject'][26:]
        date = msg['Date']
        html = msg.get_payload()
        
        soup = BeautifulSoup(html, 'html.parser')
        for info in soup.findAll('a', href = True):
            if str(info['href']).find('JobId') != -1:
               jid = str(info['href'])[str(info['href']).find('JobId') + 6:str(info['href']).find('&')] #get job id
               
            if str(info['href']).find('mailto') != -1 and str(info['href']).find('matteo.morini994') == -1: #get reference person's mail
               contact_p = str(info['href'])[7:]
               
        print("Application done on "+pulisci(date)+" for:"+pulisci(subj)+" (job n."+pulisci(jid) +")\n")       
      
        query = "UPDATE cwjobs SET contact_p ='"+contact_p+"' WHERE jid='"+jid+"';" #upd main table with contact mail
        cur.execute(query)
        conn.commit()
        query = "UPDATE cwjobs SET applied = true WHERE jid = '"+jid+"';" #application done
        cur.execute(query)
        conn.commit()

cur.close()
conn.close()
mail.close()
mail.logout()
