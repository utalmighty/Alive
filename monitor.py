import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
import schedule

pings = 0
name_and_urls = []
status = []  # (sum_of_pings, failed_pings)
admins = []


def initialization():
    ''' Read environment varibles '''
    global name_and_urls
    global admins
    services = os.environ['SERVICES'].split(",")
    urls = os.environ['SERVICES_URLS'].split(",")
    name_and_urls = []
    for i, service in enumerate(services):
        name_and_urls.append((service.strip(), urls[i].strip()))
    admins = [admin.strip() for admin in os.environ['ADMINS_EMAILS'].split(",")]
    reset()


def job():
    ''' Periodic request Job '''
    global pings
    global status
    pings += 1
    for i, item in enumerate(name_and_urls):
        start_time = time.time()
        resp = requests.get(item[1]) # No timeout
        if (resp.status_code == 200):
            status[i][0] += int((time.time()-start_time)*1000)
        else:
            # Increase failure count
            status[i][1] += 1


def send_report():
    ''' Email Report '''
    report = "Total Pings: " + str(pings) + "\n"
    for i, item in enumerate(name_and_urls):
        denominator = pings-status[i][1]
        average_ping = "Service unavailable!"
        if denominator > 0:
            average_ping = str(status[i][0]/denominator)+" ms"
        report += "👉" + item[0] + " 🟢Average Ping Latency: " + \
            average_ping + " 🔴Failed Pings: " + str(status[i][1]) + "\n"
    local_time = time.localtime()
    subject = "Report: " + str(local_time.tm_mday) + "-" + \
        str(local_time.tm_mon) + "-" + str(local_time.tm_year)
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(user=os.environ['EMAIL'], password=os.environ['EMAIL_PASSWORD'])
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg.attach(MIMEText(report))
    smtp.sendmail(from_addr='Well Wishers Admin',
                  to_addrs=admins, msg=msg.as_string())
    smtp.quit()
    reset()


def reset():
    '''Reset all the values to default'''
    global pings
    global status
    pings = 0
    status = []
    for i in range(len(name_and_urls)):
        status.append([0, 0])


if __name__ == "__main__":
    initialization()
    schedule.every(int(os.environ['PING_INTERVAL_IN_MINUTES'])).minutes.do(job)
    schedule.every().day.at(os.environ['EMAIL_TIME']).do(send_report)
    while True:
        schedule.run_pending()
