from datetime import datetime
from datetime import date
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from bs4 import BeautifulSoup
from threading import*
from TubbsFunctions import *
from TubbsFunctions import _email
import sys
import time 
import logging
import os

#Global Variables
upTimeDays = 1          # Counter Variable for how long program has bee nup and running for
dateObj = dates()       # Date object for date operations and functions
initialGet = False      # Flag mainly for testing to enter the program before the set time
bWind = False           # boolean value if getWind finished with data of day at hand.
threadNum = 0
logger = getLogger()    # Returns the logger obj from TubbsFunctions.py

#!######################
#? Initial Get (testing), comment and uncomment as necessary
#initialGet = True
#!######################

# Initial while loop so that you can start code at any time and will loop until it 
# satisfies one of the if() conditions
while True:
    dt = datetime.now()
    now = dt.strftime("%H:%M:%S")   # program counter time
    sys.stdout.write("\r" + now)
    sys.stdout.flush()

    if(initialGet == True or  now == "06:03:00"):   # if the code has already been entered once or it is 7:00 am
        logger.info("\nEntered main program loop at %s", now )
        

        # Main loop
        while True:
            dt = datetime.today()
            today = dt.strftime("%Y%m%d")
                                      
            findWater()

            # Make sure tracking array has elements because we dont want to assign empty/null array
            if(len(wGetArray()) > 0):
                logger.info("Wind track array: HAS ELEMENTS")

                # start tracking wind during proper day
                if(today == wGetIndex(0)):
                    logger.info("Today == windDay: TRUE")
                    logger.info("Starting Thread...")
                    bWind = True                                        # Flag to let us know that we are tracking wind data and have to pop a item from the wind array
                    t1 = Thread(target=getWind, args=(wGetIndex(0),))   # DONT delete the comma, necessary syntax
                    t1.start()
                else:
                    logger.info("Today == windDay: FALSE")
            else:
                logger.info("Wind track array: NULL")
 


            #After a week send an email about the status of the data
            if(upTimeDays %7 == 0): 
                logger.info("One week check-in: TRUE, send email") 
                high = getHighestLevels()

                # Determining if thresholds for wind speed was met. Wind will be null if 
                # the thresholds of the tide levels werent met because the wind data gathering depends
                # on the results of the tide level data gathering.
                if(float(high['s']) == 0):
                    _email("One week check in\n Uptime: "+ str(upTimeDays) + 
                        "days  \n\n" + "Highest tide level recorded over a 7 days period was \n" + 
                        high['t'] + ": " + high['v'] + " ft\n\n" +
                        "Highest wind speed was not recorded due to thresholds not being met", 1)
                elif(float(high["s"]) > 0):
                    _email("One week check in\n Uptime: "+ str(upTimeDays) + 
                        "days  \n\n" + "Highest tide level recorded over a 7 days period was \n" + 
                        high['t'] + ": " + high['v'] + " ft\n\n" +
                        "Highest wind speed recorded over a 7 day period was \n" +
                        high['tW'] + ": " + high['s'] + " ft", 1)
                    
                resetHighestLevels()
            else:
                logger.info("One week check-in: FALSE")

            sys.stdout.write("\r" + "Up Time: " + str(upTimeDays) + " day(s)\n")
            sys.stdout.flush()

           
            # time.sleep is in seconds, run the sleep before the thread.join to run concurrently
            logger.info("Starting 24 hour wait")
            time.sleep(86400) 
            logger.info("\n24 Hours over, preparing to start next day get request")

            #after the join we need to pop the day from the list and reset flag
            if(bWind == True):
                logger.info("Wind Tracking Clean-Up: TRUE") 
                logger.info("Joining thread...")
                logger.info("Deleting %s from tracking list", str(wGetIndex(0)))
                t1.join()
                wPop(0)
                bWind = False
                logger.info("Wind Array - Days to track: %s", str(wGetArray()))      #to see what we need to track.
            else:
                logger.info("Wind Tracking Clean-Up: FALSE")    
            
           
            os.system('cls' if os.name == 'nt' else 'clear')    # clear the terminal screen
            logger.info("Terminal Screen Cleared...")
            upTimeDays +=1
           
    


