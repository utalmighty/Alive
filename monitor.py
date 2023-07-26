import time

import schedule
from flask import Flask

from Job import Job

app = Flask(__name__)
obj = Job()

@app.route("/start")
def start():
    if not obj.is_running :
        obj.is_running = True
        while True :
            schedule.run_pending()
    return "Already Running"

@app.route("/")
def hello():
    sys_time = time.localtime()
    return "Hello from Alive!! System Time: "+ str(sys_time.tm_hour) + ":" + str(sys_time.tm_min)

if __name__ == "__main__":
    schedule.every(obj.interval).minutes.do(obj.job)
    schedule.every().day.at(obj.day_time).do(obj.send_report)
    app.run(port=8084)