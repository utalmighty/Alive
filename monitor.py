import time

import schedule
from flask import Flask

from Job import Job

app = Flask(__name__)
obj = Job()


@app.route("/start")
def start():
    ''' Start Monitoring if not already running '''
    if not obj.is_running:
        obj.is_running = True
        while obj.is_running:
            schedule.run_pending()
    return "Already Running!"

@app.route("/stop")
def stop():
    ''' Stop Monitoring if running '''
    if obj.is_running:
        obj.is_running = False
        return "Monitoring Stopped!"
    return "Monitoring already stopped!"


@app.route("/")
def hello():
    ''' Say hello '''
    sys_time = time.localtime()
    return "Hello from Alive!! System Time: " + str(sys_time.tm_hour) + ":" + str(sys_time.tm_min) + " Ping count: " + str(obj.pings)


if __name__ == "__main__":
    schedule.every(obj.interval).minutes.do(obj.recurring_job)
    schedule.every().day.at(obj.one_time_job_time).do(obj.one_time_job)
    schedule.every().day.at(obj.day_time).do(obj.send_report)
    app.run(host='0.0.0.0', port=8084)
