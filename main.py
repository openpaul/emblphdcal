from icalendar import Calendar, Event

from bs4 import BeautifulSoup
import urllib.request
import re
import time
import datetime

import sys

if not sys.warnoptions:
    import warnings

# very hacky regex to recognise the date or timerange fields 
# feel free to improve
datereg   = re.compile(r"[\w\s]+[\d]+\.[\d]+\.[\d]+")
timereges = re.compile(r"[\d]+:[\d\s]+-[\d\s]+:[\d\s]+")

class course():
    def __init__(self, url, f):
        # fetching HTML
        fp = urllib.request.urlopen(url)
        htmldoc = fp.read().decode("utf8")
        fp.close()
        # parsing the HTML
        s     = BeautifulSoup(htmldoc, 'html.parser')
        tables = self.findTable(s)
        self.cal = Calendar()
        self.events = []
        
        for table in tables:
            self.parseWeek(table)
        
        self.write(f)
        
    def findTable(self,s):
        return(s.find_all("table", class_="tab-cco-program"))
    
    def asUNIX(self, date, time = None, start = True, defaultStart = "09:00", defaulEnd = "17:00"):
        '''function to transform our text into unix timestamps'''
        d = date.split(" ")[1]
        
        # if a time was given
        if time == None and start:
            d = "{} {}".format(d, defaultStart)
        elif time == None and start == False:
            d = "{} {}".format(d, defaulEnd)
        else:
            d = "{} {}".format(d, time)
        

        # check if the date is 2018 or 18 only:
        Yreg = re.compile(r"20[0-9][0-9]")
        if Yreg.search(d) != None:    
            us = datetime.datetime.strptime(d, "%d.%m.%Y %H:%M")
        else:
            us = datetime.datetime.strptime(d, "%d.%m.%y %H:%M") 
        

        
        return(us)
    
    def parseWeek(self, table):
        '''this function parses a table of a week'''
        
        # basically scan the trs and try to make sense of them
        rows = table.find_all("tr")
        prevdate = False # do we have a date yet?
        for row in rows:
            # first field (td) gives time range
            # if its a date we submit a whole day event 
            # if second field is empty
            fields = row.find_all("td")
            f1 = fields[0].get_text( strip=True)
            f2 = fields[1].get_text( strip=True)
            
            # match our time and date regex
            dm = datereg.match(f1)
            tm = timereges.match(f1)
            if dm:
                prevdate = f1# self.asUNIX(f1)
                # this is a date field
                if f2 =="" :
                    continue
                else:
                    # whole day event, presumingly:
                    eventName  = f2
                    eventStart = self.asUNIX(date = prevdate)
                    eventEnd   = self.asUNIX(date = prevdate, start = False)
            elif tm:
                # figuring the date ranges
                startend   = f1.split(" - ")
                eventStart = self.asUNIX(date = prevdate, time = startend[0])
                eventEnd   = self.asUNIX(date = prevdate, time = startend[1])
                eventName  = f2
            else:
                #print(f1)
                # here we do custom handlers for dates
                # examples are:
                # Afternoon
                # 13:30 onwards
                # From 17:00
                eventName  = f2
                # defining afternoon:
                if f1.lower() == "afternoon":
                    eventStart = self.asUNIX(date = prevdate, time = "12:00")
                    eventEnd   = self.asUNIX(date = prevdate, time = "17:00")
                else:
                    singleTimeReg = re.compile(r"[\d]+:[\d]+")
                    m = singleTimeReg.search(f1)
                    if m:
                        # we have a date:
                        tm = m.group(0)
                        directionalityReg = re.compile(r"onwards|From")
                        if directionalityReg.search(f1):
                            eventStart = self.asUNIX(date = prevdate, time = tm)
                            eventEnd   = self.asUNIX(date = prevdate, start = False)
                        else:
                            warnings.warn("We dont know what time this is: {}".format(f1))
            
            # save the event
            event = Event()
            event.add("dtstart", eventStart)
            event.add("dtend", eventEnd)
            event.add("summary", eventName)
            self.cal.add_component(event)
    
    def ical(self):
        a = self.cal.to_ical()
        b = a.decode('utf-8').replace("\r\n", "\n")
        return b    
   
    def write(self, f):
        with open(f, "w") as file:
            file.write(self.ical())



# starting the class
url = "https://www.embl.de/predoccourse/2018/schedule/index.html"
cs = course(url,
            "Predoc_Course_2018.ics")

