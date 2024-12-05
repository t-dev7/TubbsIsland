#Water_Testing

from datetime import datetime
from datetime import date
from datetime import timedelta
import requests
import sys
import json
from bs4 import BeautifulSoup
from threading import*
import multiprocessing as mp
import time 
import smtplib
import logging
import os
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from time import sleep


class sevenFeet:
    def __init__(self, data, dt):
        self.data = data       # json dictionary data
        self.dt = dt           # "Days Tracked"


class dates:
    def today(self):
        today = date.today()
        today = today.strftime("%Y%m%d")    # format for the search in URL
        return today
    
    #today "Normal Format"
    def todayNF():
        today = date.today()
        return today.strftime("%m-%d-%Y")
    
    #Formatting for comparing and printing 
    def todayWind(self):
       today = date.today()
       return today.strftime("%Y-%m-%d")
    
    def nextWeekWind(self):
        today = date.today()
        nextWeekWind = today + timedelta(weeks=1)
        return nextWeekWind.strftime("%m-%d-%Y")
    
    def beginDate(self):
        today = date.today()
        BeginDate = today + timedelta(weeks=0)
        return BeginDate.strftime("%Y%m%d") #format the days to match how the api queries the data


    def endDate(self):
        today = date.today()
        EndDate = today + timedelta(days=2) #end data processing for three days after the begin processing date
        return EndDate.strftime("%Y%m%d")
    
  
######################################################
#Global Variables
upTimeDays = 1
dateObj = dates()
initialGet = False
wCount = 0
checkWindFlag = False            # flag to tell system to check the wind data for specific days
checkWindCounter = 0             #count the days the wind checker has checked to make sure it falls within the three days of 7ft
toPop = False
daysInARow = 0      # counter for days in a row 7ft occurs
bWind = False           #boolean value if getWind finished with data of day at hand.

threeDaysList = []  # list of json data objects where the water level was greater than 7ft
wind = []
days = {}
threadNum = 0


logger = logging.getLogger("tubbs")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - Line %(lineno)s: %(message)s')


#File Handler to rotate log files ever day and keep 8 backups
#fileHandler = TimedRotatingFileHandler(dates.todayNF() + "_log.log", when='d', interval=1, backupCount=8)

#File handler to rotate log files and rotate once file size reached 50KB
fileHandler = RotatingFileHandler("logs/" + dates.todayNF() + ".log", backupCount=7, maxBytes=50000)
fileHandler.setFormatter(formatter)

stdout = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(fileHandler)
stdout.setLevel(logging.INFO)

logger.addHandler(stdout)
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)

#!##################### Email Functions ####################################

def send_email(message, subject):
    global logger
    try:
        content = message 
        mail=smtplib.SMTP('mail.vsfcd.com', 25)
        mail.ehlo()
        mail.starttls()
        sender='tubbs@vsfcd.com'
        #recipient= ['itdept@vsfcd.com', 'nMuradian@vallejowasterwater.org']
        recipient= ['tdavis@vallejowastewater.org']

        header='To:'+ ", ".join(recipient) + '\n'+'From:' \
        +sender+'\n'+'subject:' + subject + '\n\n'

        msg = header + content
        mail.sendmail(sender, recipient, msg)
        mail.close()
        logger.info("Email Sent")

    except Exception as error:
        logger.error("Water level email FAILED to send")
        

def send_error_email(message):
    try:
        content = message
        mail=smtplib.SMTP('mail.vsfcd.com', 25)
        mail.ehlo()
        mail.starttls()
        sender='tubbs@vsfcd.com'
        #recipient='itdept@vallejowastewater.org'
        recipient='tdavis@vallejowastewater.org'

        header='To:'+ recipient + '\n'+'From:' \
        +sender+'\n'+'subject:Code Error\n\n'

        msg = header + content
        mail.sendmail(sender, recipient, msg)
        mail.close()
    except Exception as error:
        logger.error("Email level email FAILED to send")
        

def send_water_email(list):
    global logger
    url = "https://tidesandcurrents.noaa.gov/waterlevels.html?id=9414863&units=standard&bdate=20240131&edate=20240207&timezone=LST/LDT&datum=NAVD&interval=6&action="


    try:
        content = ("Water levels of 7ft were found starting "+ str(dateObj.nextWeekWind()) +"\n" + str(list) + "\n\n" ) 
        mail=smtplib.SMTP('mail.vsfcd.com', 25)
        mail.ehlo()
        mail.starttls()
        sender='tubbs@vsfcd.com'
        recipient= ['tdavis@vallejowastewater.org']
#        recipient= ['itdept@vsfcd.com', 'nMuradian@vallejowasterwater.org']

        header='To:'+ ", ".join(recipient) + '\n'+'From:' \
        +sender+'\n'+'subject:Water Level Warning (TESTING)\n\n'

        msg = header + content
        mail.sendmail(sender, recipient, msg)
        mail.close()
        logger.info("Water level email sent")

    except Exception as error:
        logger.error("Water level email FAILED to send")
        send_error_email(error)

def send_wind_email(list):
    global logger
    try:
        content = ("Water levels of 6.5ft or more were expected for three days consecutive days starting today, "+ str(dateObj.todayWind()) + 
                   "\n\n" + "A wind speed has been recorded at 30mph or greater.\n\n" + 
                    "Speed       |      Direction                |   Gusting     |      Time\n"  + 
                    "---------------------------------------------------------------------------\n" +
                   str(list)) 
        mail=smtplib.SMTP('mail.vsfcd.com', 25)
        mail.ehlo()
        mail.starttls()
        sender='tubbs@vsfcd.com'
        #recipient= ['itdept@vsfcd.com', 'nMuradian@vallejowasterwater.org']
        recipient= ['tdavis@vallejowastewater.org']

        header='To:'+ ", ".join(recipient) + '\n'+'From:' \
        +sender+'\n'+'subject:Wind Speed Warning (TESTING)\n\n'

        msg = header + content
        mail.sendmail(sender, recipient, msg)
        mail.close()
        logger.info("Wind speed email sent")

    except Exception as error:
        logger.error("Wind speed email FAILED to send %s", error, stack_info=True, exc_info=True)
#!##################### END Email Functions #####################################

def deleteOldFiles(f):
    global logger
    n = 7
    cwd = os.getcwd()

    os.chdir(os.path.join(os.getcwd(), f))
    fileList = os.listdir()
    ct = time.time()
    day = 86400
  

    for i in fileList:
        # get the location of the file 
        file_location = os.path.join(os.getcwd(), i) 
        # file_time is the time when the file is modified 
        file_time = os.stat(file_location).st_mtime 
    
        # if a file is modified before N days then delete it 
        if(file_time <= ct - day*n):  
            os.remove(file_location) 
            logger.info("Deleted : %s", i)
    os.chdir(cwd)

#!#############################################################

def getParsedDay_List(date):
    try:
        split = " "         # character/string to split at
        result = ""         # String to return

        for i in date:
            result = i['t'].partition(split)[0]     # find only the first date and not the time of data set
            break                                   # exit loop after first find
    except Exception as error:
        logger.error("Trouble parsing the day  : %s", str(error), stack_info=True, exc_info=True)
    return result

#!#####################################################

# Function that get the first date of the data set in formatted form and returns it
def getParsedDay(date):
    split = " "         # character/string to split at
    result = ""         # String to return

    result = date['t'].partition(split)[0]     # find only the first date and not the time of data set
                                          

    return result    

#!#####################################################
def convertDate(date):
    space = " "
    temp = date.partition(space)[0]
    result = ""

    for i in range(len(temp)):
        if(ord(date[i]) < 48 or ord(date[i]) > 57):
            continue
        else:
            result += date[i]

    return result

#!#####################################################

def wAppend(data):
    global wind
    wind.append(convertDate(data))

#!#####################################################

def getWind(aWind):
    #aWind is the wind array
    #['t'] = date-time (y-m-d HH:MM 24hr)
    #['s'] = Wind speed (knotts)
    #['d'] = Wind direction (degrees)
    #['dr'] = Wind direction (cardinal)
    #['g'] = Wind gust (knotts)


    windURL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&application=NOS.COOPS.TAC.MET&begin_date=" + aWind[0] + "&end_date=" + aWind[0] + "&station=9415141&time_zone=lst_ldt&units=english&interval=6&format=json"
    wCount = 0
    windList = ""
    windFound = False
    iHighest = 0
    bHigh = False

    
    #Processing
    #Neet to make get Request 239 times because db updated every 6 minutes
    while(wCount < 239):
        try:
            logger.info("Getting data from wind URL")
            t = requests.get(windURL)
            tsoup = BeautifulSoup(t.content, 'html.parser')
            windData = tsoup.prettify()
            windData = json.loads(windData)
            s = windData["data"]      #predictied tide level in feet
            logger.info("Successfully grabbed wind Data")

        except Exception as error:
            logger.critical("Error in findWater() get request: %s", str(error), stack_info=True, exc_info=True)
            send_error_email("Program has been termitated due to error obtaining water data, Error: " + str(error))
        
        try:
            for i in range(len(s)):
                if(i == wCount):
                    speed = float(s[i]["s"])                    # convert string wind speed to float value 
                    speed = round((speed * 1.15), 2)            # knott to mph formula

                    #For New Highs
                    if (speed > iHighest):   #set highest 
                        iHighest = speed
                        bHigh = True

                    #if it meets criteria and it's a new high
                    #TODO: Change criteria after done testing
                    if(iHighest >= 15.00 and bHigh == True):
                        bHigh = False
                        gust = float(s[i]["g"])
                        gust = round((gust * 1.15), 2)

                        #Formatting dateTime to look better ####
                        temp = str(s[i]['t']).partition(' ')
                        sTime = (temp[0] + ", " + temp[2])

                        logger.info("High wind speed found %s mph on - %s", str(iHighest), sTime)

                        #Email content formatted ####
                        windList += (str(iHighest) + " mph  | " + str(s[i]['dr']) + " (" + str(s[i]['d']) + " degrees)  |  " +
                                    str(gust) + " mph  |  " + sTime + "\n")
                        
                        #creates json file to show the data for that day
                        json_object = json.dumps(s, indent=2)
                        with open("data/wind/FOUND_" + dates.todayNF() + ".json", "w") as outfile:
                            outfile.write(json_object)
                        deleteOldFiles("data/wind")
                        
                        send_wind_email(windList)
                        

                    wCount += 1
                    logger.info("Data Count is %i", wCount)


            time.sleep(360)
        except Exception as error:
            logger.error("findWind() error - %s", str(error), stack_info=True, exc_info=True)
            break
            
#!#####################################################

# Function that finds if the water level meets or exceeds 7ft
def findWater():
    global daysInARow
    global threeDaysList
    global checkWindFlag
    global wind
    vCount = 0          #counter for data points of 1 day in tideData
    sevenFound = False
    waterList = "Date             Time        Lvl\n-----------------------------------------\n"
    global logger
    highest = 0

    tideURL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date=" + dateObj.beginDate() + "&end_date=" + dateObj.endDate() + "&datum=NAVD&station=9414863&time_zone=lst_ldt&units=english&interval=&format=json"
    # Get URL Content
    try:
        logger.info("Getting data from tide URL")
        t = requests.get(tideURL)
        tsoup = BeautifulSoup(t.content, 'html.parser')
        tideData = tsoup.prettify()
        tideData = json.loads(tideData)
        v = tideData["predictions"]      #predictied tide level in feet

    except Exception as error:
        logger.critical("Error in findWater() get request: %s", str(error), stack_info=True, exc_info=True)
        send_error_email("Program has been termitated due to error obtaining water data, Error: " + str(error))
        sys.exit() 



    for i in v:     #loop through the dictionary of the predicted values for that day
        try:
            if(vCount < 239 and sevenFound == False):   # amount of data points for one day.
                level = float(i["v"])                   # cast to float value               

                if (level > highest):   #set highest 
                    highest = level

                if(level >= 5.670):                      # if the level is greater than or equal to 7ft
                    logger.info("%s: %s ft - FOUND high level", i['t'], i['v'])
                    daysInARow += 1
                    sevenFound = True
                    waterList += (str(i['t']) + " - " + str(i['v']) + " ft - FOUND high level\n" )
                    
                    wAppend(i['t'])     #append the date to a list 

                vCount += 1     #increase the counter 
            
            elif(vCount < 239 and sevenFound == True):      # if seven feet was already found anytime during the day
                vCount += 1
                continue

            elif(vCount == 239 and sevenFound == False):    # if seven feet was not found at any point during a day
                logger.info("%s: Water level does not exceed threshold - %s ft", getParsedDay(i), highest)
                waterList += (str(i['t']) + " - " + str(highest) + " ft \n" )
                vCount = 0                                  # set the count back to 0 for the next day
                daysInARow = 0
                highest = 0
            
            elif(vCount == 239 and sevenFound == True):     # if it is the data point of the day and 7ft has been found
                vCount = 0                                  # set the count back to 0 for the next day
                sevenFound = False
                highest = 0

        except Exception as error:
            
            logger.error("findWater() error: %s", str(error), stack_info=True, exc_info=True)
            send_error_email(str(error))


    if(daysInARow >= 3):                    # if there are three days in a row of 7ft
        try:
            logger.info("High water levels were found: %s", getParsedDay_List(v))

            send_water_email(waterList)                            # send an email out (place holder)

            #reset variables for the next getRequest
            waterList = "Date             Time        Lvl\n-----------------------------------------\n"
            daysInARow = 0                                
            
            #creates json file to show the data for that day
            json_object = json.dumps(v, indent=2)
            with open("data/water/FOUND_" + dates.todayNF() + "_waterData.json", "w") as outfile:
                outfile.write(json_object)
            deleteOldFiles("data/water")

        except Exception as error:
            logger.error("Error at dayInARow == 3, stopping program: %s", str(error), stack_info=True, exc_info=True)
            send_error_email("Program was terminated due to error creating a dataObj. Error: " + str(error))
            sys.exit()
    else:
        #creates json file to show the data for that day
        json_object = json.dumps(v, indent=2)
        with open("data/water/" + dates.todayNF() + "_waterData.json", "w") as outfile:
            outfile.write(json_object)
        deleteOldFiles("data/water")
        
#!##################### Main #####################################

# initial entry into the code at a specific time
while True:
    dt = datetime.now()
    now = dt.strftime("%H:%M:%S")   # program counter time
    sys.stdout.write("\r" + now)
    sys.stdout.flush()
    

    if(initialGet == True or  now == "00:07:00"):   # if the code has already been entered once or it is 12:07 am

        logger.info("\nEntered main program loop at %s", now )
        initialGet = True

        while True:
            today = dt.strftime("%Y%m%d")   # format to check array against
            findWater()

            if(today == wind[0]):
                bWind = True
                #start thread to run getWind() with wind array as argument
                t1 = Thread(target=getWind, args=(wind,))
                t1.start()
                
                

            #After a week send an email about the status of the data
            if(upTimeDays %7 == 0):                 #message                                                              subject
                send_email("One week check in\n Uptime: "+ str(upTimeDays), "Tubbs Status")

            sys.stdout.write("\r" + "Up Time: " + str(upTimeDays) + " day(s)\n")
            sys.stdout.flush()

           
            #Join the thread after the sleep so it runs "concurrently" with the main
            time.sleep(86400)   #wait for 24 hours
            logger.info("24 Hours over, preparing to start next day get request")
            t1.join()
            logger.info("Joining thread...")
            
            #after the join we need to pop the day from the list
            if(bWind == True):
                wind.pop(0)
                bWind = False
                logger.info("Deleted %s from tracking list", str(wind[0]))
            
           
            os.system('cls' if os.name == 'nt' else 'clear')    # clear the terminal screen
            logger.info("Terminal Screen Cleared...")
            upTimeDays +=1
            
    


