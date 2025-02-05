import smtplib

def send_email(message):
    content = message 
    mail=smtplib.SMTP('enter domain and port number')
    #Example: mail=smtplib.SMTP('mail.domain.com', 25)
    mail.ehlo()
    mail.starttls()
    sender='enter email to send from'
    recipient= ['Enter Email(s) here']

    header='To:'+ ", ".join(recipient) + '\n'+'From:' \
    +sender+'\n'+'subject:' + "Tubbs Status" + '\n\n'

    msg = header + content
    mail.sendmail(sender, recipient, msg)
    mail.close()

################################################### 

def send_error_email(message):
    content = message
    mail=smtplib.SMTP('enter domain and port number')
    #Example: mail=smtplib.SMTP('mail.domain.com', 25)
    mail.ehlo()
    mail.starttls()
    sender='enter email to send from'
    recipient= ['Enter Email(s) here']

    header='To:'+ recipient + '\n'+'From:' \
    +sender+'\n'+'subject:Code Error\n\n'

    msg = header + content
    mail.sendmail(sender, recipient, msg)
    mail.close()

###################################################

def send_wind_email(list, d, s, e):
    # s = start date
    # e = end date
    # d = formatted human readable date
    URL = "https://tidesandcurrents.noaa.gov/met.html?bdate=" + str(s) + "&edate=" + str(e) + "&units=standard&timezone=LST%2FLDT&id=9415141&interval=6"

    content = ("Water levels of 7.5ft or more were expected for three days consecutive days starting today, "+ str(d) + 
                "\n\n" + "A wind speed has been recorded at 30mph or greater.\n\n" + 
                "    Speed      |          Direction              |    Gusting     |      Time\n"  + 
                "---------------------------------------------------------------------------\n" +
                str(list) + "\n\n See link below for more details\n" + URL) 
    
    mail=smtplib.SMTP('enter domain and port number')
    #Example: mail=smtplib.SMTP('mail.domain.com', 25)
    mail.ehlo()
    mail.starttls()
    sender='enter email to send from'
    recipient= ['Enter Email(s) here']

    header='To:'+ ", ".join(recipient) + '\n'+'From:' \
    +sender+'\n'+'subject:Wind Speed Warning (TESTING)\n\n'

    msg = header + content
    mail.sendmail(sender, recipient, msg)
    mail.close()

###################################################


#send an email concerning water levels
def send_water_email(list, d, s, e):
    # s = start date
    # e = end date
    # d = formatted human readable date
    URL = "https://tidesandcurrents.noaa.gov/waterlevels.html?id=9414863&units=standard&bdate=" + str(s) +"&edate=" + str(e) + "&timezone=LST/LDT&datum=NAVD&interval=6&action="

    content = ("Water levels of 7ft were found starting "+ str(d) +"\n" + str(list) + "\n\n See link below for more details\n" + URL ) 
    mail=smtplib.SMTP('enter domain and port number')
    mail.ehlo()
    mail.starttls()
    sender='enter email to send from'
    recipient= ['Enter Email(s) here']

    header='To:'+ ", ".join(recipient) + '\n'+'From:' \
    +sender+'\n'+'subject:Water Level Warning\n\n'

    msg = header + content
    mail.sendmail(sender, recipient, msg)
    mail.close()


