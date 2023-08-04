import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

class Job:
    ''' Job class '''

    def __init__(self) -> None:
        self.pings = 0
        self.status = []
        self.is_running = False
        self.interval = int(os.environ['PING_INTERVAL_IN_MINUTES'])
        self.day_time = os.environ['EMAIL_TIME']
        self.email = os.environ['EMAIL']
        self.password = os.environ['EMAIL_PASSWORD']
        self.admins = [admin.strip()
                       for admin in os.environ['ADMINS_EMAILS'].split(",")]
        services = os.environ['SERVICES'].split(",")
        urls = os.environ['SERVICES_URLS'].split(",")
        self.name_and_urls = [(service.strip(), urls[i].strip())
                              for i, service in enumerate(services)]
        self.reset_pings()

    def reset_pings(self):
        ''' Resets the value of pings and status '''
        self.pings = 0
        self.status = []
        self.status = [[0, 0] for i in range(len(self.name_and_urls))]

    def job(self):
        ''' Periodic request Job '''
        self.pings += 1
        for i, item in enumerate(self.name_and_urls):
            start_time = time.time()
            resp = requests.get(item[1])  # No timeout
            if resp.status_code == 200 :
                self.status[i][0] += int((time.time()-start_time)*1000)
            else:
                # Increase failure count
                self.status[i][1] += 1

    def send_report(self):
        ''' Email Report '''
        report = "Total Pings: " + str(self.pings) + "\n"
        for i, item in enumerate(self.name_and_urls):
            denominator = self.pings-self.status[i][1]
            average_ping = "Service unavailable!"
            if denominator > 0:
                average_ping = str(self.status[i][0]/denominator)+" ms"
            report += "👉" + item[0] + " 🟢Average Ping Latency: " + \
                average_ping + " 🔴Failed Pings: " + \
                str(self.status[i][1]) + "\n"
        local_time = time.localtime()
        subject = "Report: " + str(local_time.tm_mday) + "-" + \
            str(local_time.tm_mon) + "-" + str(local_time.tm_year)
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(user=self.email,
                   password=self.password)
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg.attach(MIMEText(report))
        smtp.sendmail(from_addr='Well Wishers Admin',
                      to_addrs=self.admins, msg=msg.as_string())
        smtp.quit()
        self.reset_pings()