import smtplib

def send_email(message):
    content = message 
    mail=smtplib.SMTP('maildomain.com', n)     #**Change to your parameters
    mail.ehlo()
    mail.starttls()
    sender='sender@domain.com'                  #**Change to your parameters
    recipient= ['recipient@domain.com']         #**Change to your parameters

    header='To:'+ ", ".join(recipient) + '\n'+'From:' \
    +sender+'\n'+'subject:' + "Tubbs Status" + '\n\n'

    msg = header + content
    mail.sendmail(sender, recipient, msg)
    mail.close()

################################################### 

def send_error_email(message):
    content = message
    mail=smtplib.SMTP('maildomain.com', n)     #**Change to your parameters
    mail.ehlo()
    mail.starttls()
    sender='sender@domain.com'                  #**Change to your parameters
    recipient= ['recipient@domain.com']         #**Change to your parameters


    header='To:'+ recipient + '\n'+'From:' \
    +sender+'\n'+'subject:Code Error\n\n'

    msg = header + content
    mail.sendmail(sender, recipient, msg)
    mail.close()

###################################################

def send_wind_email(list, date):
    content = ("Water levels of 6.5ft or more were expected for three days consecutive days starting today, "+ str(date) + 
                "\n\n" + "A wind speed has been recorded at 30mph or greater.\n\n" + 
                "Speed       |      Direction                |   Gusting     |      Time\n"  + 
                "---------------------------------------------------------------------------\n" +
                str(list)) 
    mail=smtplib.SMTP('maildomain.com', n)     #**Change to your parameters
    mail.ehlo()
    mail.starttls()
    sender='sender@domain.com'                  #**Change to your parameters
    recipient= ['recipient@domain.com']         #**Change to your parameters

    header='To:'+ ", ".join(recipient) + '\n'+'From:' \
    +sender+'\n'+'subject:Wind Speed Warning (TESTING)\n\n'

    msg = header + content
    mail.sendmail(sender, recipient, msg)
    mail.close()

###################################################


#send an email concerning water levels
def send_water_email(list, d, s, e):
    URL = "https://tidesandcurrents.noaa.gov/waterlevels.html?id=9414863&units=standard&bdate=" + str(s) +"&edate=" + str(e) + "&timezone=LST/LDT&datum=NAVD&interval=6&action="

    content = ("Water levels of 7ft were found starting "+ str(d) +"\n" + str(list) + "\n\n See link below for more details\n" + URL ) 
    mail=smtplib.SMTP('maildomain.com', n)     #**Change to your parameters
    mail.ehlo()
    mail.starttls()
    sender='sender@domain.com'                  #**Change to your parameters
    recipient= ['recipient@domain.com']         #**Change to your parameters

    header='To:'+ ", ".join(recipient) + '\n'+'From:' \
    +sender+'\n'+'subject:Water Level Warning\n\n'

    msg = header + content
    mail.sendmail(sender, recipient, msg)
    mail.close()
