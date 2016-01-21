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

def get_link_final_stage(jjid, llink): #get the link of the page where you can submit your application

    p = s.get('http://www.cwjobs.co.uk'+llink)
    soup1 = BeautifulSoup(p.text, 'html.parser')
    lapp = soup1.find('a', {'id' : 'JobToolsTop_AOLOptions_lnkApplyOnline'}) #depending on the adv, final page is in a different tag
    if lapp is None: 
         lapp = soup1.find('li', {'class' : 'aol'}) 
         la = str(lapp)
         la = la[la.find('href')+6:la.find('id')-2]
    else:
         la = lapp['href']
    if la.strip() == "":
         lapp = soup1.find('a', {'title' : 'Apply'})
         la = lapp['href']
         
    print('http://www.cwjobs.co.uk'+la)
    query = "UPDATE cwjobs SET link_app = %s WHERE jid = %s;" #upd the table with last link
    data = (la, jjid)
    cur.execute(query, data)
    conn.commit()
       
#main
i = 1
fine = 1

passw = getpass.getpass("Enter password for the database: ") #connection to DB
try:
    conn=psycopg2.connect(dbname='cwjobs',  user ='postgres' ,host='localhost', password= passw)
    print("Connection OK")
except psycopg2.Error as e:
    print("I am unable to connect to the database.")
    print(e.pgcode)
    print(e.pgerror)
    print(traceback.format_exc())
    quit()


cur = conn.cursor()

jk = input("Insert Job title, skills or company to limit the search (just enter to select all):")
jk = jk.strip().replace(" ",'+')
loc = input("Where do you want to work (if you press just return it will be considered everywhere): ")
s = requests.session()
#tags and other names often change
while fine != 0:
    
    url= "http://www.cwjobs.co.uk/JobSearch/Results.aspx?Keywords="+jk+"&LTxt="+loc+"&Radius=10&PageNum="+str(i)
    
    print(url)
    r = s.get(url)
   
    soup = BeautifulSoup(r.text, 'html.parser')
    jobs = soup.findAll('div', {'class' : 'hd'}) #section with job title and link to job description
    jobsd = soup.findAll('ul',{'class' : "bd job-details"}) #section with main job detail

    fine = len(jobsd)
    #fine=0
    k=0
   
    
    for j in jobs:
        try:
           h2 = j.find("h2")
           if h2 == None:
               continue
           jd=jobsd[k]    
           link = j.find('a', {'href' : True}) #link to job description
           jid = link['href'][link['href'].find('JobId=')+6:link['href'].find('&')] #exatract job number

           query = "SELECT jid FROM cwjobs WHERE jid ="+jid #check if the job has been already added
           cur.execute(query)
           if cur.fetchone() is not None: 
               print("Job already added to DB: n."+jid)
               continue
            
           title = pulisci(link.getText().strip()) #main job details
           print('Job title: '+ title)
           print('Job link: '+link['href'])
           location = jd.find('span', {'property' : 'jobLocation'})
           salary = jd.find('span', {'property' : 'baseSalary'})
           company = jd.find('a', {'property' : 'name'})
           date_ins = jd.find('meta', {'property' : 'datePosted'})  
           
           
           if location is not None and salary is not None and company is not None: #add a row in DB
                 location = pulisci(location.getText()).strip()
                 salary = pulisci(salary.getText()).strip()
                 company = pulisci(company.getText()).strip()
                 print('Salary: '+salary.strip())
                 print('Company: '+company.strip())
                 print('Location: '+location.strip())
                 print('Publication date: '+date_ins['content'])
                 query = "INSERT INTO cwjobs (jid, location, salary, recr_comp, link_desc, date_post, applied, job_key, jtitle) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                 data = (jid, location, salary, company, link['href'], date_ins['content'],'False', jk, title)
                 
                 cur.execute(query, data)
                 conn.commit()
                 get_link_final_stage(jid, link['href'])
           
           k = k+1
           time.sleep(1)
        except ValueError:
           break
    print('\n')
    i = i+1    
   
    




