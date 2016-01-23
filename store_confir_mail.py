#third script to launch
import imaplib
import email
import getpass
import datetime
import sys
from bs4 import BeautifulSoup
import psycopg2
import re
import base64
import time

def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
        'may':5,
        'jun':6,
        'jul':7,
        'aug':8,
        'sep':9,
        'oct':10,
        'nov':11,
        'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')
    
def pulisci(s):
    return re.sub('[^a-zA-Z0-9-£ ()^/|^&]', '', s)


#login and select "Inbox" on my mail server
print("Login to your mailbox to collect application confirmation mail!")
user = input("User: ")
password = getpass.getpass()
mail = imaplib.IMAP4_SSL('imap.mail.yahoo.com')
mail.login(user, password)
mail.list()
mail.select("Inbox")

#login on my DB server
passdb = getpass.getpass("Input password DB: ")
try:
    conn=psycopg2.connect(dbname='cwjobs',  user ='postgres', host='localhost', password= 'cwj4rr1v0')
    print("Connection OK")
except psycopg2.Error as e:
    print("I am unable to connect to the database.")
    print(e.pgcode)
    print(e.pgerror)
    
cur = conn.cursor()
result, data = mail.search(None, '(FROM cwjobs@cwjobsmail.co.uk)') #Look for mail from cwj...
#log file with current date and time
now = time.strftime("%c")
file = open("Log_mail_stored_"+ now.replace(' ','_').replace('/','-').replace(':','-') +".txt", "w")


for num in data[0].split():
    
    typ, dat = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(dat[0][1])
    #subject decoding 
    if msg['Subject'].find('utf-8') != -1:
        v = msg['Subject'].split()
        middle = v[0][10:len(v[0])-2]+v[1][10:len(v[1])-2]+v[2][10:len(v[2])-2]
        decoded = base64.b64decode(middle)
        subjd = decoded.decode('utf-8')
    else:
        subjd = msg['Subject']
        
    #consider only mail regardind the application confirmation    
    if subjd.strip().find('Application confirmation') != -1 : 
        subjd = subjd[26:]
        date = msg['Date']
        #consider only application after a certain date, first scripts test 21/01/2016
        date = date[:11].strip()
        ad = date.split(' ')
        html = msg.get_payload()
        if datetime.date(int(ad[2]), month_string_to_number(ad[1]) ,int(ad[0])) > datetime.date(2016,1,20):
            file.write("Mail "+str(num)+" Date"+date+ " Subject: "+subjd+"\r\n")
            soup = BeautifulSoup(html, 'html.parser')
            #extracting from mail body of job id number and reference person's mail
            for info in soup.findAll('a', href = True):
                if str(info['href']).find('JobId') != -1:
                   jid = str(info['href'])[str(info['href']).find('JobId') + 6:str(info['href']).find('&')] #get job id
                if str(info['href']).find('mailto') != -1 and str(info['href']).find('matteo.morini994') == -1: #get reference person's mail
                   contact_p = str(info['href'])[7:]
               
            print("Application done on "+pulisci(date)+" for:"+pulisci(subjd)+" (job n."+pulisci(jid) +")")
            file.write("Application done on "+pulisci(date)+" for:"+pulisci(subjd)+" (job n."+pulisci(jid) +")\r")
            #check if it is a new mail 
            query = "SELECT applied FROM cwjobs WHERE jid ="+ jid+ ";"
            cur.execute(query)
            r = cur.fetchone()
            
            if r[0] == False:
               #upd main table with contact mail and changing to true column applied
               input("STOP")
               print("New contatct: "+contact_p+' ID: '+jid+'\r\n')
               file.write("New contatct: "+contact_p+' ID: '+jid+'\r\n')
               file.write('\n')
               query = "UPDATE cwjobs SET contact_p ='"+contact_p+"', applied = true WHERE jid='"+jid+"';" 
               cur.execute(query)
               conn.commit()
               
            else:
               print("Contact already added: "+contact_p+'\n')
               file.write("Contact already added: "+contact_p+'\r\n')
               file.write('\n')


file.close()
cur.close()
conn.close()
mail.close()
mail.logout()
