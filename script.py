import schedule
import time
import os

def job1():
    os.system("python3 EventsTogetherScripts/allevents_parse.py")

def job2():
    os.system("python3 EventsTogetherScripts/eventbrite_parse.py")

def job3():
    os.system("python3 EventsTogetherScripts/soldouttickets_parse.py")

schedule.every().sunday.at("07:00").do(job1)
schedule.every().sunday.at("07:00").do(job2)
schedule.every().sunday.at("07:00").do(job3)

while True:
    schedule.run_pending()
    time.sleep(1)
