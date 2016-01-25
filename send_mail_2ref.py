# last script to launch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
import psycopg2
import getpass
import time


def attach(filename, m):
    attachment = open(filename, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        "attachment; filename= %s" % filename)
    m.attach(part)
    return

passdb = getpass.getpass("Input password DB: ")  # Connection to the DB
try:
    conn = psycopg2.connect(
         dbname='cwjobs', user='postgres', host='localhost',
         password=passdb)
    print("Connection OK")
except psycopg2.Error as e:
    print("I am unable to connect to the database.")
    print(e.pgcode)
    print(e.pgerror)
cur = conn.cursor()


print("Login to your mailbox to collect application confirmation mail!")
umail = input("User: ")
password = getpass.getpass()
print(password)
# send mail where I'm applied
query = """SELECT contact_p,jid FROM cwjobs WHERE applied= true
      AND mail_sent = false;"""
cur.execute(query)
# mail sent log file
now = time.strftime("%c")
now = now.replace(' ', '_').replace('/', '-').replace(':', '-')
file = open("Log_mail_sent_" + now + ".txt", "w")
# attachments
fa = ['160112_Matteo_Morini_CV_en.pdf', '160112_cover_letter_Matteo.pdf']
i = 1

try:
    msg = MIMEMultipart()
    msg['From'] = umail
    s = smtplib.SMTP("smtp.mail.yahoo.com", 587, timeout=10)
    s.set_debuglevel(1)
    s.starttls()
    s.login(umail, password)

    for r in cur.fetchall():
        name = r[0].split('.')[0]
        bodym1 = "Dear " + name + ",\n"
        bodym2 = """This application has been sent with scripts written in
                 python using several libraries such as BeautifulSoup,
                 Selenium, Requests and Psycopg2...I would show that I can
                 manage rather well these kind of stuffs. You can find on
                 github -->
                 https://github.com/MMorini86/Automatic-application-cwjobs
                 the source code of the  scripts that I used to apply for
                 this position.
                 Looking forward to hearing from you."""
        bodym3 = """\nBest regards\nMatteo Morini\nMail: """ + umail + """
        Mobile: mymobile"""
        bodym = bodym1 + " ".join(bodym2.split()) + bodym3
        subj = """README: Note on job application (cwjob reference
             n.""" + str(r[1]) + """) - Matteo Morini"""

        recipients_emails = r[0]
        file.write("Mail n. " + str(i) + " sent to: " + recipients_emails +
                   " ID:" + str(r[1]) + " - " + now + "\r\n")
        msg['Subject'] = subj
        msg['To'] = recipients_emails
        msg.attach(MIMEText(bodym, 'plain'))

        for z in range(len(fa)):
            attach(fa[z], msg)

        s.sendmail(msg['From'], recipients_emails, msg.as_string())
        s.quit()
        query = "UPDATE cwjobs SET mail_sent = true WHERE jid = "+str(r[1])+"""
                AND contact_p = '""" + r[0] + "';"
        cur.execute(query)
        conn.commit()
        time.sleep(3)
        i = i + 1
finally:
    cur.close()
    conn.close()
