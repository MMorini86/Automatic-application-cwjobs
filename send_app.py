# second script to launch
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import psycopg2
import getpass


# main
# connection to DB
passw = getpass.getpass("Enter password for the database: ")
try:
    conn = psycopg2.connect(
        dbname='cwjobs',  user='postgres',
        host='localhost', password=passw)
    print("Connection OK")
except psycopg2.Error as e:
    print("I am unable to connect to the database.")
    print(e.pgcode)
    print(e.pgerror)
cur = conn.cursor()

browser = webdriver.Firefox()  # start the session with login
browser.get("https://www.cwjobs.co.uk/Authenticated/Login.aspx?ReturnUrl=%2f")
time.sleep(4)
username = browser.find_element_by_id("txtEmail")
password = browser.find_element_by_id("txtPassword")
umail = input("Enter user name for www.cwjobs.co.uk: ")
username.send_keys(umail)
time.sleep(2)
passcwj = getpass.getpass()  # pass for cwjobs.co.uk
password.send_keys(passcwj)
time.sleep(2)
submit = browser.find_element_by_id('btnLogin')
submit.click()

# filter the application with location and other keys
print("Do you want to restrict your application with:")
loc = input("Aarea? Select your location or return to consider everywhere:")
f = 'c'
print('\nWith Job keys: ')
i = 1
lk = []  # keys list
while f.lower() != 'e':
    lk.append(input("Input your "+str(i)+"° key: "))
    f = input("Press e to start to apply...")
    i = i + 1

# start making the query, to avoid applying twice
query = """SELECT link_app, location, jtitle, jid FROM cwjobs
      WHERE applied = false"""
if loc != "":
    query = query + " AND lower(location) LIKE '%" + loc.lower() + "%'"
if len(lk) != 0:
    query = query+' AND ('
    for i in lk:
        query = query + " lower(jtitle) LIKE '%" + i.lower() + "%' OR"
query = query[:len(query)-3]+');'

# log file with current date and time
now = time.strftime("%c")
now = now.replace(' ', '_').replace('/', '-').replace(':', '-')
file = open("Send_app\Query_executed_" + now + ".txt", "w")
file.write(query)
file.close()
file = open("Send_app\Application_log_" + now + ".txt", "w")
cur.execute(query)

for r in cur.fetchall():
    # control flag on aa = already applied, ea = expired application
    # and b = button
    flagaa, flagea, flagb = False, False, False
    browser.get("https://www.cwjobs.co.uk"+r[0])
    time.sleep(4)

    alreadyapp = browser.find_elements_by_tag_name('h2')
    for aa in alreadyapp:
        if aa.text.find('You applied') != -1:
            flagaa = True
            break
    if flagaa:
        file.write('Already applied--> ID: ' + str(r[3]) + ' ' + r[2] + '\r\n')
        continue

    expiredapp = browser.find_elements_by_tag_name('p')
    for ea in expiredapp:
        if ea.text.find('has now expired') != -1:
            flagea = True
            break
    if flagea:
        file.write('Expired --> ID: ' + str(r[3]) + ' ' + r[2] + '\r\n')
        continue

    continue_app = browser.find_elements_by_id('btnSubmit')
    for ca in continue_app:
        if ca.text.find('Continue application') != -1:
            flagb = True
            break
    if flagb:
        file.write('Continue app --> ID: ' + str(r[3]) + ' ' + r[2] + '\r\n')
        continue

    # still not, APPLY!
    xpa = './/button[@class="clearfix cover-letter-link btn btn-link btn-link-extensions"]'
    browser.find_element_by_xpath(xpa).click()
    submit = browser.find_element_by_id('btnSubmit')
    submit.click()
    time.sleep(3)

file.close()
cur.close()
conn.close()
