# Tide Data WebScraper
Grabs tide data and sends and email when the tides are above a certain height.

# Specifics
Grabs NAVD tide level predictions one week in advance. The program sends an email when if one week in advance, there are 3 consecutive days of tide levels above 6.5 ft. The programs runs once a day starting at 12:07 AM. It has a logging systems to keep track of what is going on and if there are any errors. It also dumbs the JSON value (neatly) in subdirectories and deletes them after one week. The program also renames the JSON files to the date in which they pertain to and also includes a renaming convension when there is a day where the levels are "found". The wind portion of the weather station does not provide prospective data so the program has to keep track of what days the tides were high, and when that day comes around the wind portion will start to pull data and track wind speeds in 6 minute intervals (amount of time the station takes to update its data points). 

# Purpose/Mission
A needed trigger to alert engineers to fight flood activities at our place of employment. 


