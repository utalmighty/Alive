import requests
import time
import schedule
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

sender = os.environ['EMAIL']
password = os.environ['EMAIL_PASSWORD']
pingInterval = int(os.environ['PING_INTERVAL_IN_MINUTES'])
mailTime = os.environ['EMAIL_TIME']
servicesName = os.environ['SERVICES']
servicesUrls = os.environ['SERVICES_URLS']
adminsEmails = os.environ['ADMINS_EMAILS']

pings = 0
name_and_urls = []
status = [] #(sum_of_pings, failed_pings)
admins = []

def initialization() :
    global name_and_urls
    global admins
    services = servicesName.split(",")
    urls = servicesUrls.split(",")
    admins = adminsEmails.split(",")
    name_and_urls = []
    for i in range(len(services)) :
        name_and_urls.append((services[i].strip(), urls[i].strip()))
    for i in range(len(admins)) :
        admins[i] = admins[i].strip()


def job() :
    global pings
    global status
    pings += 1
    for i, item in enumerate(name_and_urls) :
        start_time = time.time()
        resp = requests.get(item[1])
        if (resp.status_code == 200) :
            status[i][0] += int((time.time()-start_time)*1000)
        else :
            # Increase failure count
            status[i][1] += 1 

def sendReport() :
    
    report = "Total Pings: " + str(pings) + "\n"
    for i, item in enumerate(name_and_urls) :
        denominator = pings-status[i][1]
        averagePing = "Service unavailable!"
        if (denominator > 0) :
            averagePing = str(status[i][0]/denominator)+" ms"
        report += "👉" + item[0] + " 🟢Average Ping Latency: " + averagePing + " 🔴Failed Pings: " + str(status[i][1]) + "\n"

    t = time.localtime()
    subject = "Report: "+ str(t.tm_mday) + "-" + str(t.tm_mon) + "-" + str(t.tm_year)
    
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender, password)
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg.attach(MIMEText(report))
    smtp.sendmail(from_addr='Well Wishers Admin', to_addrs=admins, msg=msg.as_string())
    smtp.quit()
    reset()

def reset() :
    global pings
    global status
    pings = 0
    status = []
    for i in range(len(name_and_urls)) :
        status.append([0,0])

if __name__ == "__main__" :
    reset()
    initialization()
    schedule.every(pingInterval).minutes.do(job)
    schedule.every().day.at(mailTime).do(sendReport)
    while (True) :
        schedule.run_pending()
