#second script to launch
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import psycopg2
import getpass





passw = getpass.getpass("Enter password for the database: ") #connection to DB
try:
    conn=psycopg2.connect(dbname='cwjobs',  user ='postgres', host='localhost', password= passw)
    print("Connection OK")
except psycopg2.Error as e:
    print("I am unable to connect to the database.")
    print(e.pgcode)
    print(e.pgerror)
cur = conn.cursor()

browser = webdriver.Firefox() #start the session with login
browser.get("https://www.cwjobs.co.uk/Authenticated/Login.aspx?ReturnUrl=%2f")
time.sleep(4)
username = browser.find_element_by_id("txtEmail")
password = browser.find_element_by_id("txtPassword")
time.sleep(2)
umail = input("Enter user name for www.cwjobs.co.uk: ")
username.send_keys(umail)
time.sleep(2)
passcwj = getpass.getpass() #pass for cwjobs.co.uk
password.send_keys(passcwj)
time.sleep(2)
submit = browser.find_element_by_id('btnLogin')
submit.click()


print("Do you want to restrict your application with:") #filter the application with location and other keys
loc = input("Aarea? Select your location or return to consider everywhere:")
f= 'c'
print('\nWith Job keys: ')
i=1
lk = []
while f.lower() != 'e':
     lk.append(input("Input your "+str(i)+"° key: "))
     f = input("Press e to start to apply...")
     i = i+1
    
query = "SELECT link_app, location, jtitle FROM cwjobs WHERE applied = false" #avoid applying twice

if loc != "":
    query = query + " AND lower(location) LIKE '%" + loc.lower() + "%'" 

if len(lk) != 0:
    query = query+' AND '
    for i in lk:
        query = query + " lower(jtitle) LIKE '%" + i.lower() + "%' OR"

query = query[:len(query)-3]+';'

file = open("Query_in_execution.txt", "w")
file.write(query)
file.close()

cur.execute(query)
for r in cur.fetchall():
    
    browser.get("http://www.cwjobs.co.uk"+r[0])
    time.sleep(4)
    browser.find_element_by_xpath('.//button[@class="clearfix cover-letter-link btn btn-link btn-link-extensions"]').click() #I'm modifyng this part to avoid errors
    time.sleep(5)
    submit = browser.find_element_by_id('btnSubmit')
    submit.click()
    time.sleep(5)
       


cur.close()
conn.close()
