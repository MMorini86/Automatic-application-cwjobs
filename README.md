# Automatic-application-cwjobs
Send automatic applications to cwjobs.co.uk using python 

Purpose: show to recruiters that I have knowledges in programming languages, DB and web.


At the moment I wrote 4 scripts in python to launch sequentially:
  1. aa4cwjobs.py: scrape the site http://www.cwjobs.co.uk/ to look for jobs to apply to. You can filter the scraping by location and other                    keys. All the data are stored in a DB called cwjobs. DBMS used: POSTGRE.
                   Table query:

                   CREATE TABLE public.cwjobs
                   (
                      jid bigint NOT NULL,
                      location character varying(100),
                      salary character varying(100),
                      recr_comp character varying(100),
                      link_desc character varying(255),
                      link_app character varying(255),
                      date_post date,
                      applied boolean,
                      job_key character varying(50),
                      jtitle character varying(100),
                      contact_p character varying(80),
                      mail_sent boolean,
                      CONSTRAINT cwjobs_pkey PRIMARY KEY (jid)
                    )
  2. send_app.py: using Selenium I will apply only one to all jobs present in the table cwjobs. Option: filter again on the location.
  3. store_confir_mail.py: store application confirmation through application confirmation mail received, updating main table with the                                reference person's mail and updating the column applied from false to true.
  4. send_mail_2ref: send mail with a note to each reference person.
  
The scripts at the moment don't contain sophisticated controls, most important thing is APPLYING!!
   
