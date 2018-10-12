#!/usr/bin/python
'''
integ v0.2 - Copyright 2018 James Slaughter,
This file is part of integ v0.2.

integ v0.2 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

integ v0.2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with integ v0.2.  If not, see <http://www.gnu.org/licenses/>.
'''

#python import
import sys
import os
import subprocess
import datetime
import time
import smtplib
import hashlib
import urllib2
from datetime import date
from email.mime.text import MIMEText
from array import *
from termcolor import colored

#programmer generated imports
from controller import controller
from fileio import fileio

'''
Usage()
Function: Display the usage parameters when called
'''
def Usage():
    print 'Usage: [optional] --debug --help'
    print 'Example: /opt/integ/integ.py --debug'
    print 'Required Arguments:'
    print '--debug - Prints verbose logging to the screen to troubleshoot issues.  Recommend piping (>>) to a text file due to the amount of text...'
    print '--help - You\'re looking at it!'
    sys.exit(-1)

'''
ConfRead()
Function: - Reads in the integ.conf config file and assigns some of the important
            variables
'''
def ConfRead():
        
    ret = 0
    intLen = 0
    FConf = fileio()
    FLOG = fileio()

    try:
        #Conf file hardcoded here
    	FConf.ReadFile('/opt/integ/integ.conf')
    except:
        print '[x] Unable to read configuration file!  Terminating...'
        FLOG.WriteLogFile(CON.logfile, '[x] Unable to read configuration file!  Terminating...\n')
        return -1
    
    for line in FConf.fileobject:
        intLen = len(line)            
        if (CON.debug == True):
            print '[DEBUG]: ' + line
        if (line.find('targets') != -1):                
            CON.targets = line[8:intLen].strip()
        elif (line.find('diff') != -1): 
            CON.diff = line[5:intLen].strip()
        elif (line.find('output') != -1): 
            CON.output = line[7:intLen].strip()
        elif (line.find('logfile') != -1):
            CON.logfile = line[8:intLen].strip()
        elif (line.find('emailalerting') != -1):
            if (line[14:intLen].strip() == 'True'):
                CON.emailalerting = True        
        elif (line.find('recipients') != -1):                
            CON.recipients = line[11:intLen].strip()
        elif (line.find('subject') != -1):
            CON.email_subject = line[8:intLen].strip()
        elif (line.find('email') != -1):
            CON.email = line[6:intLen].strip()
        elif (line.find('password') != -1):
            CON.password = line[9:intLen].strip()
        else:
            if (CON.debug == True): 
                print ''

    if (len(CON.targets) < 3):
        print '[x] Please enter a valid targets file in the integ.conf file.  Terminating...'
        FLOG.WriteLogFile(CON.logfile, '[x] Please enter a valid targets file in the integ.conf file.  Terminating...\n')            
        print ''
        return -1

    if (len(CON.diff) < 3):
        print '[x] Please enter a valid diff directory in the integ.conf file.  Terminating...'
        FLOG.WriteLogFile(CON.logfile, '[x] Please enter a valid diff directory in the integ.conf file.  Terminating...\n')            
        print ''
        return -1

    if (CON.emailalerting == True):
        print '[*] E-mail alerting is active...'
        FLOG.WriteLogFile(CON.logfile, '[*] E-mail alerting is active...\n') 

        if (len(CON.email) < 3):
            print '[x] Please enter a valid sender e-mail address in the integ.conf file.  Terminating...'
            FLOG.WriteLogFile(CON.logfile, '[x] Please enter a valid sender e-mail address in the integ.conf file.  Terminating...\n')            
            print ''
            return -1    

        if (len(CON.password) < 3):
            print '[x] Please enter a valid sender e-mail password in the integ.conf file.  Terminating...'
            FLOG.WriteLogFile(CON.logfile, '[x] Please enter a valid sender e-mail password in the integ.conf file.  Terminating...\n')            
            print ''
            return -1

        if (len(CON.recipients) < 3):
            print '[x] Please enter a valid recipients file in the integ.conf file.  Terminating...' 
            FLOG.WriteLogFile(CON.logfile, '[x] Please enter a valid recipients file in the integ.conf file.  Terminating...\n')           
            print ''
            return -1

        if (len(CON.email_subject) < 3):
            print '[-] No custom e-mail subject entered.  Using: "Integ Alert"'
            FLOG.WriteLogFile(CON.logfile, '[-] No custom e-mail subject entered.  Using: \"Integ Alert\"\n')
            CON.email_subject == 'Integ Alert'            
            print ''

    try:
        # Read in our list of targets
        with open(CON.targets.strip(),"r") as fd:
            file_contents = fd.read()
            CON.target_list      = file_contents.splitlines()
    except:
        # Target list read failed, bail!
        print '[x] Unable to read targets file: ' + CON.targets
        FLOG.WriteLogFile(CON.logfile, '[x] Unable to read targets file: ' + CON.targets)
        return -1

    if (CON.emailalerting == True):
        try:
            # Read in our list of recipients
            with open(CON.recipients.strip(),"r") as fd:
                file_contents2 = fd.read()
                CON.recipient_list    = file_contents2.splitlines()
        except:
            # Recipients list read failed, bail!
            print '[x] Unable to read recipients file: ' + CON.recipients
            FLOG.WriteLogFile(CON.logfile, '[x] Unable to read recipients file: ' + CON.recipients) 
            return -1
         
    print '[*] Finished configuration successfully.\n'
    FLOG.WriteLogFile(CON.logfile, '[*] Finished configuration successfully.\n')
            
    return 0

'''
Parse() - Parses program arguments
'''
def Parse(args):        
    option = ''
                    
    print '[*] Arguments: \n'
    for i in range(len(args)):
        if args[i].startswith('--'):
            option = args[i][2:]

            if option == 'help':
                return -1  

            if option == 'debug':
                CON.debug = True
                print option + ': ' + str(CON.debug)

'''
send_alert()
Function: - Sends the alert e-mail from the address specified
            in the configuration file to potentially several addresses
            specified in the "recipients.txt" file.
'''
def send_alert(alert_email):

    FLOG = fileio()
    
    email_body = 'Integ has completed a run ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")) + '\n'

    if (CON.debug == True): 
       print '\n[DEBUG] Walking through the output from alert_email ***'
       FLOG.WriteLogFile(CON.logfile, '[DEBUG] Walking through the output from alert_email ***\n')

    if (len(alert_email) == 0):
        print '\n[DEBUG] No changes in the monitored scripts have been detected during this run...***'
        FLOG.WriteLogFile(CON.logfile, '[DEBUG] No changes in the monitored scripts have been detected during this run...***\n')
        email_body += '\r\rNo changes in the monitored scripts have been detected during this run...'
    else:
        # Walk through the output from alert_email    
        for result in alert_email:
            if (CON.debug == True):        
                print '\n[DEBUG] Result: ' + result.strip()
                FLOG.WriteLogFile(CON.logfile, '[DEBUG] Result: ' + result.strip() + '\n')
  
            email_body += '\r\rResult: ' + result.strip()

    for recipient_entry in CON.recipient_list:
        print '\r\n[-] Sending e-mail to: ' + recipient_entry                        
        FLOG.WriteLogFile(CON.logfile, '[-] Sending e-mail to: ' + recipient_entry + '\n')

        # Build the email message
        msg = MIMEText(email_body)
        msg['Subject'] = CON.email_subject.strip()
        msg['From']    = CON.email.strip()
        msg['To']      = recipient_entry
    
        server = smtplib.SMTP("smtp.gmail.com",587)
    
        server.ehlo()
        server.starttls()
        server.login(CON.email.strip(),CON.password.strip())
        server.sendmail(recipient_entry,recipient_entry,msg.as_string())
        server.quit()
    
        print '[*] Alert email sent!'
        FLOG.WriteLogFile(CON.logfile, '[*] Alert email sent!\n')  
    
    return 0

'''
validate_hash()
Function: - connects to a remote host to verify the target file's hash matches the one on record
'''
def validate_hash():

    FI = fileio()
    FLOG = fileio()
    FCSV = fileio()
    error = False
    split_string = ''
    owner_domain = ''
    url = ''
    orig_hash_value = ''
    remote_file = ''
    remote_hash_value = hashlib.md5() 
    change = False
    notes = ''
    alert_email = []
    target_count = len(CON.target_list)
    csv_filename = CON.output + str(datetime.datetime.now().strftime("%d-%m-%Y_%I:%M")) + '.csv'
    wget_data = ''
    Count = 0    

    FCSV.WriteLogFile(csv_filename, 'Owner Domain,URL,Original Hash Value,Remote Hash Value,Change?,Notes\n')

    print colored('\n[*] There are ' + str(target_count) + ' targets being examined...', 'green', attrs=['bold'])
    FLOG.WriteLogFile(CON.logfile, '[*] There are ' + str(target_count) + ' targets being examined...\n')

    for i in CON.target_list: 
 
        print colored('\r\n[*] Executing against target ' + str(Count+1) + ' of ' + str(target_count), 'green', attrs=['bold'])
        FLOG.WriteLogFile(CON.logfile, '[*] Executing against target ' + str(Count+1) + ' of ' + str(target_count) + '\n')
        print '[*] Target list data: ' + CON.target_list[Count]
        FLOG.WriteLogFile(CON.logfile, '[*] Target list data: ' + CON.target_list[Count] + '\n')
        print '[*] Splitting string...'
        owner_domain, url, orig_hash_value = CON.target_list[Count].split(';')
        print '[*] Owner Domain: ' + owner_domain.strip()
        FLOG.WriteLogFile(CON.logfile, '[*] Owner Domain: ' + owner_domain.strip() + '\n')
        print '[*] URL: ' + url.strip()
        FLOG.WriteLogFile(CON.logfile, '[*] URL: ' + url.strip() + '\n')
        print '[*] Original Hash Value: ' + orig_hash_value.strip()
        FLOG.WriteLogFile(CON.logfile, '[*] Original Hash Value: ' + orig_hash_value.strip() + '\n')
        
        print '[*] Downloading URL...'
        try:
            remote_file = urllib2.urlopen(url)
            data = remote_file.read()
            remote_hash_value.update(data)

            print '[*] Remote Hash Value: ' + str(remote_hash_value.hexdigest())
            FLOG.WriteLogFile(CON.logfile, '[*] Remote Hash Value: ' + str(remote_hash_value.hexdigest()) + '\n')
        except urllib2.HTTPError, e:
            # Something's gone funny at the protocol level and thrown an error...
            error = True
            print colored('[x] HTTPError: Error connecting to remote host: ' + str(e.code) , 'red', attrs=['bold'])
            FLOG.WriteLogFile(CON.logfile, '[x] Error connecting to remote host: ' + str(e.code) + '\n')
            notes = str(e.code)  
        except urllib2.URLError, e:
            # If we're here, there's likely been a connection error to the remote host
            error = True
            print colored('[x] URLError: Error connecting to remote host: ' + str(e.reason) , 'red', attrs=['bold'])
            FLOG.WriteLogFile(CON.logfile, '[x] Error connecting to remote host: ' + str(e.reason) + '\n')
            notes = str(e.reason)
        except:
            #Something really bad has happened and there isn't a specific error handler for it...
            error = True
            print colored('[x] General exception handler tripped...', 'red', attrs=['bold'])
            FLOG.WriteLogFile(CON.logfile, '[x] General exception handler tripped...\n')
            notes = 'General exception handler tripped...'

        if (error == True):
            print colored('\n[-] Skipping to next target due to error...', 'yellow', attrs=['bold'])
            FCSV.WriteLogFile(csv_filename, owner_domain + ',' + url + ',' + str(orig_hash_value) + ',' + '---------------------------------------------------------' + ',' + str(change) + ',' + notes + '\n')
            if (CON.emailalerting == True):
                alert_email.append('An error was encountered for OWNER: ' + owner_domain + ' - URL: ' + url + ' - ORIG MD5: ' + str(orig_hash_value) + ' - NOTES: ' + notes + '\n')
        elif (str(remote_hash_value.hexdigest()) == orig_hash_value.strip()):
            print colored('[*] Original and remote MD5 hashes match!', 'green', attrs=['bold'])
            FLOG.WriteLogFile(CON.logfile, '[*] Original and remote MD5 hashes match!\n')
            notes = 'N/A'
            FCSV.WriteLogFile(csv_filename, owner_domain + ',' + url + ',' + str(orig_hash_value) + ',' + str(remote_hash_value.hexdigest()) + ',' + str(change) + ',' + notes + '\n')
        else:
            print colored('[x] Original and remote MD5 hashes DO NOT match!', 'red', attrs=['bold'])
            FLOG.WriteLogFile(CON.logfile, '[*] Original and remote MD5 hashes DO NOT match!!\n')
            change = True
            if (CON.emailalerting == True):
                alert_email.append('Original and remote MD5 hashes DO NOT match for OWNER: ' + owner_domain + ' - URL: ' + url + ' - ORIG MD5: ' + str(orig_hash_value) + ' - REMOTE MD5: ' + str(remote_hash_value.hexdigest()) + '\n')

            print '[*] Downloading additional version...'
            FLOG.WriteLogFile(CON.logfile, '[*] Downloading additional version...\n')

            if (CON.debug == True):
                print '[DEBUG] wget --no-check-certificate --output-document=' + CON.diff + str(remote_hash_value.hexdigest()) + '.js ' + url

            #WGet flags: 
            #            --no-check-certificate Will not balk when a site's certificate doesn't match the target domain.
            #            --output-documentoutput to given filename.
            

            subproc = subprocess.Popen('wget --output-document=' + CON.diff + str(remote_hash_value.hexdigest()) + '.js ' + url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if (CON.debug == True):
                print '\n[DEBUG] Printing WGet output ***'
                for wget_data in subproc.stdout.readlines():
                    print '[DEBUG] ' + wget_data

            print '[*] File downloaded to: ' + CON.diff + str(remote_hash_value.hexdigest()) + '.js '
            FLOG.WriteLogFile(CON.logfile, '[*] File downloaded to: ' + CON.diff + str(remote_hash_value.hexdigest()) + '.js \n')

            notes += ' - File downloaded to: ' + CON.diff + str(remote_hash_value.hexdigest()) + '.js'
            FCSV.WriteLogFile(csv_filename, owner_domain + ',' + url + ',' + str(orig_hash_value) + ',' + str(remote_hash_value.hexdigest()) + ',' + str(change) + ',' + notes + '\n')

        #Prior to clearing variable values, print under debug for troubleshooting
        if (CON.debug == True):
            print '\n[DEBUG] Printing variable info prior to wiping ***'
            print '[DEBUG] owner_domain: ' + owner_domain
            print '[DEBUG] url: ' + url 
            print '[DEBUG] orig_hash_value: ' + orig_hash_value 
            print '[DEBUG] remote_hash_value: ' + str(remote_hash_value.hexdigest())
            print '[DEBUG] change: ' + str(change)
            print '[DEBUG] notes: ' + notes
            print '[DEBUG] remote_file: ' + str(remote_file)
            print '[DEBUG] data: ' + str(data)
            print '[DEBUG] alert_email: ' + alert_email  
        
        #Try to observe some proper variable hygiene and avoid data leakage between runs of the for loop
        owner_domain = '' 
        url = ''
        orig_hash_value = ''
        remote_hash_value = hashlib.md5()
        change = False
        notes = ''
        remote_file = ''
        data = ''

        #Move the counter ahead to access the next element in the target list
        Count += 1

    if (CON.emailalerting == True):
        if (CON.debug == True):
            print '\n[DEBUG] Passing data to send_alert() ***'

        send_alert(alert_email)

    print colored('\n[*] Output file created at: ' + csv_filename, 'green', attrs=['bold'])
    FLOG.WriteLogFile(CON.logfile, '[*] Output file created at: ' + csv_filename + '\n')
                               
    return 0

'''
Terminate()
Function: - Attempts to exit the program cleanly when called  
'''     
def Terminate(exitcode):
    sys.exit(exitcode)

'''
This is the mainline section of the program and makes calls to the 
various other sections of the code
'''
if __name__ == '__main__':

    ret = 0 
    count = 0  

    CON = controller()
    FLOG = fileio() 

    ret = Parse(sys.argv)
    if (ret == -1):
        Usage()
        Terminate(ret) 


    ret = ConfRead()    
    if (ret != 0):
        # Something bad happened reading the conf file...bail! 
        Terminate(ret) 

    print '[*] Begining run: ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    FLOG.WriteLogFile(CON.logfile, '[*] Begining run: ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")) + '\n')
    print '[*] Executing integ.py v0.1...'
    FLOG.WriteLogFile(CON.logfile, '[*] Executing integ.py v0.1...\n')

    # Validate the integrity list of remote target urls using MD5 (yes, I know it's not as good as SHA256!!!)
    validate_hash()

    print '\n[*] Program Complete: ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")) 
    FLOG.WriteLogFile(CON.logfile, '[*] Program Complete: ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")) + '\n')
    FLOG.WriteLogFile(CON.logfile, '*******************************************************************************************\n')

    Terminate(ret)

'''
END OF LINE
'''

