from datetime import datetime
from datetime import date
from datetime import timedelta
import requests
from sendEmail import *
import sys
import json
from bs4 import BeautifulSoup
from threading import*
import time 
import logging
import os
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler


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
        BeginDate = today + timedelta(weeks=0)   #TODO: Change criteria here
        return BeginDate.strftime("%Y%m%d") #format the days to match how the api queries the data


    def endDate(self):
        today = date.today()                 #TODO: Change criteria here
        EndDate = today + timedelta(days=2) #end data processing for three days after the begin processing date
        return EndDate.strftime("%Y%m%d")
    
#!#############################################################################################################################################     

#Global Variables
aWind = []                       # Array that holds dates to track in string format 
errorFlag = False
dateObj = dates()                # Date object for date operations and functions
daysInARow = 0                   # Counter Varaible for the days in a row 7ft occurs
highestWeekLevel = {"t": "",     # json Dictionary format that holds data to track the highest tide level/Wind speed for the week
      "v": "0", "tW":"", "s":"0"}
threeDaysList = []               # list/array of json data objects where the water level was greater than 7ft



logger = logging.getLogger("tubbs")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - Line %(lineno)s: %(message)s')

#File Handler to rotate log files ever day and keep 8 backups
fileHandler = TimedRotatingFileHandler("logs/log", when='D', interval=1, backupCount=8, atTime= 'midnight')

#File handler to rotate log files and rotate once file size reached 50KB
#fileHandler = RotatingFileHandler("logs/" + dates.todayNF() + ".log", backupCount=7, maxBytes=50000)
fileHandler.setFormatter(formatter)
stdout = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(fileHandler)
stdout.setLevel(logging.INFO)
logger.addHandler(stdout)
logger.setLevel(logging.INFO)

#!############################################################################################################################################# 

def getErrorFlag():
    global errorFlag
    return errorFlag

#!############################################################################################################################################# 
def setErrorFlag(set):
    global errorFlag
    errorFlag = set
    
#!#############################################################################################################################################   

def getLogger():
    global logger
    return logger

#!#############################################################################################################################################   

#Returns the specified index element of the wind days-to-track array
def wGetIndex(i):
    global aWind
    return aWind[i]

#!#############################################################################################################################################   

# appends tracking date to the days-to-track array
def wAppend(data):
    global aWind
    d = convertDate(data)
    #check to make sure the day isnt already in the list
    #ex) days: 1,2,3 are above Thresh AND days:2,3,4 are above thresh, we DONT want array to look like this [1,2,3,2,3,4]
    if d in aWind:
        return
    else:
        aWind.append(d) 

#!#############################################################################################################################################   

# Deletes the specified index element from the days-to-track array
def wPop(i):
    global aWind
    try:
        aWind.pop(i)
        logger.info("Successfully popped element")
    except Exception as error:
        logger.warning("Could not pop array at index %i : %s", str(error), i,  exc_info=True)

#!#############################################################################################################################################   

# Returns the entire days-to-track array
def wGetArray():
    global aWind
    return aWind

#!#############################################################################################################################################   

def _email(message, code, date=None):
    try:
        if(code == 0):
            send_error_email(message)
            
        #######        
        elif(code == 1):
            send_email(message)
            
        #######        
        elif(code == 2):
            #  Function       msg     date      start             end
            send_water_email(message, date, dateObj.today(), dateObj.endDate())
        #######        
        elif(code == 3):
            #We only track the wind happening today. Start and end date are same for URL
            #  Function      msg     date      start             end
            send_wind_email(message, date, dateObj.today(), dateObj.today())
           
    except Exception as error:
        logger.warning("Email Failed To Send: %s", str(error),  exc_info=True)

#!#############################################################################################################################################   

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

#!#############################################################################################################################################   

def getParsedDay_List(date):
    try:
        split = " "         # character/string to split at
        result = ""         # String to return

        for i in date:
            result = i['t'].partition(split)[0]     # find only the first date and not the time of data set
            break                                   # exit loop after first find
    except Exception as error:
        logger.warning("Trouble parsing the day  : %s", str(error),  exc_info=True)
    return result

#!#############################################################################################################################################   

# Function that get the first date of the data set in formatted form and returns it
def getParsedDay(date):
    split = " "         # character/string to split at
    result = ""         # String to return

    result = date['t'].partition(split)[0]     # find only the first date and not the time of data set
                                          

    return result    

#!#############################################################################################################################################   
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

#!#############################################################################################################################################   

def getWind(date):
    #['t'] = date-time (y-m-d HH:MM 24hr)
    #['s'] = Wind speed (knotts)
    #['d'] = Wind direction (degrees)
    #['dr'] = Wind direction (cardinal)
    #['g'] = Wind gust (knotts)

    global highestWeekLevel
    windURL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=wind&application=NOS.COOPS.TAC.MET&begin_date=" + date + "&end_date=" + date + "&station=9415141&time_zone=lst_ldt&units=english&interval=6&format=json"
    wCount = 0
    windList = ""
    iHighest = 0
    bHigh = False       # Flag to track if a new high value has been recorded. 
                        # we dont want program to send emails everytime speeds are higher than thresh. Only send if the wind is higher
                        # than the previous max

    
    # Processing
    # Need to make get Request. There are 240 (0-based indexing makes it 239) data points in a day 
    while(wCount <= 239):
        try:
            logger.info("Getting data from wind URL...")
            w = requests.get(windURL)
            time.sleep(3)
            tsoup = BeautifulSoup(w.content, 'html.parser')
            windData = tsoup.prettify()
            windData = json.loads(windData)
            s = windData["data"]      #predictied tide level in feet
            logger.info("Successfully Grabbed Wind Data")
            w.close()
        except Exception as error:
            wCount += 1
            logger.warning("findWind() error - %s", str(error), exc_info=True)
            logger.warning("findWind() error - Retrying getWind data pull in 6 minutes...")
            _email("getWind() error - " + str(error), 0)
            w.close()
            time.sleep(360)
            logger.warning("findWind() error - Retrying getWind data pull now...")
            continue

        try:
            # loop through the length of of all of the json data
            for i in range(len(s)):
                # since the wind data is requesting data every 6 minutes 
                    #* include this if statement because it prevents us from processing all of the previous data we already processed
                    #* ex) pull data at 12:00pm, process all of that data, pull data at 12:06 (inludes all of the data 12:00 had added 12:06)
                if(i == wCount):
                    if(s[i]["s"] != ''):
                        speed = float(s[i]["s"])                    # convert string wind speed to float value 
                        speed = round((speed * 1.15), 2)            # knott to mph formula

                        #For New Highs
                        if (speed > iHighest):   #set highest 
                            iHighest = speed
                            bHigh = True 
                            if(iHighest > float(highestWeekLevel['s'])):
                                highestWeekLevel['tW'] = s[i]['t']
                                highestWeekLevel['s'] = str(speed)

                        #if it meets criteria and it's a new high
                        #TODO: Change criteria Here
                        if(iHighest >= 15.00 and bHigh == True):
                            bHigh = False
                            gust = float(s[i]["g"])
                            gust = round((gust * 1.15), 2)

                            #Formatting dateTime to look better ####
                            temp = str(s[i]['t']).partition(' ')
                            sTime = (temp[0] + ", " + temp[2])

                            logger.info("High wind speed found %s mph on - %s", str(iHighest), sTime)

                            #Email content formatted ####
                            windList += format_Email(s[i], str(gust), str(iHighest))  + sTime + "\n"
                        
                            
                            #creates json file to show the data for that day
                            json_object = json.dumps(s, indent=2)
                            with open("data/wind/FOUND_" + dates.todayNF() + ".json", "w") as outfile:
                                outfile.write(json_object)
                            deleteOldFiles("data/wind")
                            
                            _email(windList, 3, temp[0])
                    else:
                        logger.info("%i: Wind at %s - NULL", wCount, s[i]['t'])

                    wCount += 1
                    logger.info("%i: Wind at %s - %i mph", wCount, s[i]['t'], speed)

            # These lines below are important. It helps the program to break out of the while loop at the end when the 
            # thread in the main program is joined. Otherwise it would wait an extra 6 minutes at the end
            if(wCount < 239):
                time.sleep(360)
            else:
                break

        # CATCHES ERROR AND LOGS IT, THEN CONTINUES THE LOOP
            # *alot of times the error is from bad data on the site or maintainance so we keep looping becaise it will 
            # *more than likely be better on the next data pull
        except Exception as error:
            logger.warning("findWind() error - %s", str(error), exc_info=True)
            logger.warning("findWind() error - Retrying getWind data pull in 6 minutes...")
            _email("getWind() error - " + str(error), 0)
            w.close()
            time.sleep(360)
            logger.warning("findWind() error - Retrying getWind data pull now...")
            continue
    
    logger.info("Thread successfully finished")
            
#!#############################################################################################################################################   

# Function that finds if the water level meets or exceeds 7ft
def findWater():
    global daysInARow
    global highestWeekLevel
    global threeDaysList
    global aWind
    global logger
    vCount = 0                  # counter for data points of 1 day in tideData
    threshFound = False         # Flag to determine if the threshold has been found
    waterList = "Date             Time        Lvl\n-----------------------------------------\n"
    highest = 0

    tideURL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date=" + dateObj.beginDate() + "&end_date=" + dateObj.endDate() + "&datum=NAVD&station=9414863&time_zone=lst_ldt&units=english&interval=&format=json"
    # Get URL Content
    try:
        logger.info("Getting data from tide URL")
        t = requests.get(tideURL)
        time.sleep(3)
        tsoup = BeautifulSoup(t.content, 'html.parser')
        tideData = tsoup.prettify()
        tideData = json.loads(tideData)
        v = tideData["predictions"]      #predictied tide level in feet
        t.close()

    # catches error, logs it, emails, and exits out of the method
        # * this pulls three days worth of data ONCE. So if it fails the pull there is no point in continuing with the 
        # * rest of the code. It will be bad data or no data at all so we can't process it
    except Exception as error:
        logger.warning("Error in findWater() get request: %s", str(error),  exc_info=True)
        _email("Could not grab water data, Error: " + str(error), 0)
        t.close()
        return



    for i in v:     # Dictionary loop
        try:
            if(vCount < 239 and threshFound == False):   # amount of data points for one day.
                level = float(i["v"])                   # cast to float value               

                # Setting/Tracking the highest levels
                if (level > highest):    
                    highest = level
                    # Tracking the highest water level found over 7 day period
                    if (highest > float(highestWeekLevel['v'])):
                        highestWeekLevel['t'] = i['t']
                        highestWeekLevel['v'] = i['v']

                 #TODO: Change criteria Here
                if(level >= 5.070):                      # if the level is greater than or equal to 7ft
                    logger.info("%s: %s ft - FOUND high level", i['t'], i['v'])
                    daysInARow += 1
                    threshFound = True
                    waterList += (str(i['t']) + " - " + str(i['v']) + " ft - FOUND high level\n" )
                    

                vCount += 1     #increase the counter 
            
            elif(vCount < 239 and threshFound == True):      # if seven feet was already found anytime during the day
                vCount += 1
                continue

            elif(vCount == 239 and threshFound == False):    # if seven feet was not found at any point during a day
                logger.info("%s: Water level does not exceed threshold - %s ft", getParsedDay(i), highest)
                waterList += (str(i['t']) + " - " + str(highest) + " ft \n" )
                vCount = 0                                  # set the count back to 0 for the next day
                daysInARow = 0
                highest = 0
            
            elif(vCount == 239 and threshFound == True):     # if it is the data point of the day and 7ft has been found
                vCount = 0                                  # set the count back to 0 for the next day
                threshFound = False
                highest = 0

        except Exception as error:
            logger.warning("findWater() error: %s", str(error),  exc_info=True)
            _email(str(error), 0)

            #################################################################################
    if(daysInARow >= 3):                   
        try:
            logger.info("High water levels were found: %s", getParsedDay_List(v))


            wDate = str(v[0]['t']).partition(' ')
            _email(waterList, 2, wDate[0])                            # send an email out (place holder)

            #Loop 3 times, index count 240 (1 days worth of data)
            #*Adds the 3 consecutive days in a list to track
            for i in range(0, 720, 240): 
                wAppend(v[i]['t'])    

            #reset variables for the next getRequest
            waterList = "Date             Time        Lvl\n-----------------------------------------\n"
            daysInARow = 0   
            logger.info("Wind Array - Days to track: %s", str(wGetArray()))                             
            
            #creates json file to show the data for that day
            json_object = json.dumps(v, indent=2)
            with open("data/water/FOUND_" + dates.todayNF() + "_waterData.json", "w") as outfile:
                outfile.write(json_object)
            deleteOldFiles("data/water")

        except Exception as error:
            logger.warning("Error at dayInARow == 3, stopping program: %s", str(error), exc_info=True)
            _email("Error: " + str(error),0)
            return
    else:
        #creates json file to show the data for that day
        json_object = json.dumps(v, indent=2)
        with open("data/water/" + dates.todayNF() + "_waterData.json", "w") as outfile:
            outfile.write(json_object)
        deleteOldFiles("data/water")

#!#############################################################################################################################################     
        
def format_Email(data, gust, speed):
#['t'] = date-time (y-m-d HH:MM 24hr)
#['s'] = Wind speed (knotts)
#['d'] = Wind direction (degrees)
#['dr'] = Wind direction (cardinal)
#['g'] = Wind gust (knotts)
#windList += (str(iHighest) + " mph  | " + str(s[i]['dr']) + " (" + str(s[i]['d']) + " degrees)  |  " +
#                                    str(gust) + " mph  |  " + sTime + "\n")
    
    # grab lengths one time so cpu doesnt have to check length everytime
    row = ""
    speed_Length = len(speed)
    cardinal_Length = len(data['dr'])
    degree_Length = len(data['d'])
    gust_Length = len(gust)

    #Goal is to align the columns because the degrees, direction, and mph can change
    ############# Speed ###############
    if(speed_Length == 4):
        row +=  speed + " mph    | "
    elif(speed_Length == 5):
        row +=  speed + " mph  | "
    
    ############# Cardinal ##############
    if (cardinal_Length == 1):            
        row += data['dr'] + "     ("
        
    elif (cardinal_Length == 2):
        row += "   " + data['dr'] + "   ("
    else:
         row += data['dr'] + "("

    ############# Degrees ##############
    if (degree_Length == 4):
        row += data['d'] + " degrees)      |  "

    elif (degree_Length == 5):
        row += data['d'] + " degrees)    |  "
        
    elif (degree_Length == 6):
        row += data['d'] + " degrees)  |  "

    ############# Gusting ##############
    if (gust_Length == 4):
        row += gust + "   mph   |  "
    elif (gust_Length == 5):
        row += gust + " mph  |  "
    

    return row

###############################################################################
def getHighestLevels():
    global highestWeekLevel
    return highestWeekLevel

def resetHighestLevels():
    global highestWeekLevel
    highestWeekLevel = {"t": "", 
      "v": "0", "tW":"", "s":"0"}