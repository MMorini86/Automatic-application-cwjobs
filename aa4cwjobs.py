# first script to launch
import urllib.request
import re
import time
from bs4 import BeautifulSoup
import psycopg2
import traceback
import getpass
import requests


def pulisci(s):
    return re.sub('[^a-zA-Z0-9-£ ()^/|^&]', '', s)


# get the link of the page where you can submit your application
def get_link_final_stage(jjid, llink):
    p = s.get('http://www.cwjobs.co.uk' + llink)
    soup1 = BeautifulSoup(p.text, 'html.parser')
    # depending on the adv, final page is in a different tag
    lapp = soup1.find('a', {'id': 'JobToolsTop_AOLOptions_lnkApplyOnline'})
    if lapp is None:
        lapp = soup1.find('li', {'class': 'aol'})
        la = str(lapp)
        la = la[la.find('href') + 6:la.find('id') - 2]
    else:
        la = lapp['href']
    if la.strip() == "":
        lapp = soup1.find('a', {'title': 'Apply'})
        la = lapp['href']

    print('http://www.cwjobs.co.uk' + la)
    # upd the table with last link
    query = "UPDATE cwjobs SET link_app = %s WHERE jid = %s;"
    data = (la, jjid)
    cur.execute(query, data)
    conn.commit()


# main
i = 1
fine = 1
# connection to DB
passw = getpass.getpass("Enter password for the database: ")
try:
    conn = psycopg2.connect(
                            dbname='cwjobs',
                            user='postgres',
                            host='localhost',
                            password=passw)
    print("Connection OK")
except psycopg2.Error as e:
    print("I am unable to connect to the database.")
    print(e.pgcode)
    print(e.pgerror)
    quit()
cur = conn.cursor()

jk = input("""Insert Job title, skills or company to limit
           the search (just enter to select all):""")
jk = jk.strip().replace(" ", '+')
loc = input("""Where do you want to work (if you press just return
            it will be considered everywhere): """)
s = requests.session()
# tags and other names often change
while fine != 0:
    url = "http://www.cwjobs.co.uk/JobSearch/Results.aspx?Keywords=" + jk + \
         "&LTxt=" + loc + "&Radius=10&PageNum=" + str(i)
    print(url)
    r = s.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # section with job title and link to job description
    jobs = soup.findAll('div', {'class': 'hd'})
    # section with main job detail
    jobsd = soup.findAll('ul', {'class': "bd job-details"})

    fine = len(jobsd)
    k = 0
    for j in jobs:
        try:
            h2 = j.find("h2")
            if h2 == None:
                continue
            jd = jobsd[k]
            link = j.find('a', {'href': True})  # link to job description
            # exatract job number
            jid = link['href'][link['href'].find('JobId=') + 6 \
                  : link['href'].find('&')]
            # check if the job has been already added
            query = "SELECT jid FROM cwjobs WHERE jid =" + jid
            cur.execute(query)
            if cur.fetchone() is not None:
                print("Job already added to DB: n." + jid)
                continue

            title = pulisci(link.getText().strip())  # main job details
            print('Job title: ' + title)
            print('Job link: ' + link['href'])
            location = jd.find('span', {'property': 'jobLocation'})
            salary = jd.find('span', {'property': 'baseSalary'})
            company = jd.find('a', {'property': 'name'})
            date_ins = jd.find('meta', {'property': 'datePosted'})

            # add a row in DB
            if (location is not None and
                salary is not None and company is not None):
                location = pulisci(location.getText()).strip()
                salary = pulisci(salary.getText()).strip()
                company = pulisci(company.getText()).strip()
                print('Salary: ' + salary.strip())
                print('Company: ' + company.strip())
                print('Location: ' + location.strip())
                print('Publication date: ' + date_ins['content'])
                query = """INSERT INTO cwjobs (jid, location, salary,
                                               recr_comp, link_desc,
                                               date_post, applied,
                                               job_key, jtitle)
                                               VALUES (%s, %s, %s, %s,
                                               %s, %s, %s, %s, %s);"""
                data = (jid, location, salary, company,
                        link['href'], date_ins['content'],
                        'False', jk, title)
                cur.execute(query, data)
                conn.commit()
                get_link_final_stage(jid, link['href'])
                k = k + 1
                time.sleep(1)
        except ValueError:
            break
    print('\n')
    i = i+1
