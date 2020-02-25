#!/usr/bin/python
'''
integ v0.3 - Copyright 2020 James Slaughter,
This file is part of integ v0.3.

integ v0.3 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

integ v0.3 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with integ v0.3.  If not, see <http://www.gnu.org/licenses/>.
'''

#python import
import sys
import os
import subprocess
import re
import json
import simplejson
import datetime
import time
import smtplib
import hashlib
import urllib2
import csv
from collections import defaultdict
from datetime import date
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from array import *
from termcolor import colored

#programmer generated imports
from controller import controller
from fileio import fileio
from integclass import integclass
from mms import mms

'''
Usage()
Function: Display the usage parameters when called
'''
def Usage():
    print 'Usage: [optional] --debug --help'
    print 'Example: /opt/integ/integ.py --type manifest --modules buildjscript --debug'
    print 'Required Arguments:'
    print '--type - manifest or hash'
    print '--modules - all or specific'
    print 'Optional Arguments:'
    print '--manifest <input file> - manifest file used to build the target packages.'
    print '--test - use test credentials, manifest and targetting to ensure changes run as desired.'
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
    data = ''
    emailalerting = ''
    emailpassthrough = ''

    try:
        #Conf file hardcoded here
        with open('/opt/integ/integ.conf', 'r') as read_file:
            data = json.load(read_file)
    except:
        print '[x] Unable to read configuration file!  Terminating...'
        FLOG.WriteLogFile(CON.logfile, '[x] Unable to read configuration file!  Terminating...\n')
        return -1
    
    CON.targets = data['targets']
    CON.testtargets = data['test_targets']
    CON.diff = data['diff']
    CON.repo = data['repo']
    CON.output = data['output']
    CON.logfile = data['logfile']
    emailalerting = data['emailalerting']
    if (emailalerting == 'True'): 
        CON.emailalerting = True
    CON.server = data['server']
    CON.serverport = data['server_port']
    emailpassthrough = data['emailpassthrough']
    if (emailpassthrough == 'True'):
        CON.emailpassthrough = True
    CON.recipients = data['recipients']
    CON.testrecipients = data['test_recipients']
    CON.email_subject = data['subject']
    CON.testemail_subject = data['test_subject']
    CON.email = data['email']
    CON.password = data['password']
    CON.types = data['addintypes']
    CON.addins = data['addins']
    CON.modulesdir = data['modulesdir']
  
    if (CON.debug == True):
        print '[DEBUG] data: ', data
        print '[DEBUG] CON.targets: ' + str(CON.targets)
        print '[DEBUG] CON.testtargets: ' + str(CON.testtargets)
        print '[DEBUG] CON.diff: ' + str(CON.diff)
        print '[DEBUG] CON.repo: ' + str(CON.repo)
        print '[DEBUG] CON.output: ' + str(CON.output)
        print '[DEBUG] CON.logfile: ' + str(CON.logfile)
        print '[DEBUG] CON.emailalerting: ' + str(CON.emailalerting)
        print '[DEBUG] CON.server: ' + str(CON.server)
        print '[DEBUG] CON.serverport: ' + str(CON.serverport)
        print '[DEBUG] CON.emailpassthrough: ' + str(CON.emailpassthrough)
        print '[DEBUG] CON.recipients: ' + str(CON.recipients)
        print '[DEBUG] CON.testrecipients: ' + str(CON.testrecipients)
        print '[DEBUG] CON.email_subject: ' + str(CON.email_subject)
        print '[DEBUG] CON.testemail_subject: ' + str(CON.testemail_subject)
        print '[DEBUG] CON.email: ' + str(CON.email)
        print '[DEBUG] CON.password: ' + str(CON.password)
        print '[DEBUG] CON.modulesdir: ' + str(CON.modulesdir)
        print '[DEBUG] CON.types: ' + str(CON.types)
 
        for a_addins in CON.addins: 
            for key, value in a_addins.iteritems():
                print '[DEBUG] CON.addins key: ' + key + ' value: ' + value

    for a_targets in CON.targets:
        for key, value in a_targets.iteritems():
            if (CON.debug == True):
                print '[DEBUG] CON.targets key: ' + key + ' value: ' + value
        if (key == ''):
            print '[x] There do not seem to be any valid targets files defined in the integ.conf file.  Terminating...'
            FLOG.WriteLogFile(CON.logfile, '[x] There do not seem to be any valid targets files defined in the integ.conf file.  Terminating...\n')            
            print ''
            return -1

    for a_testtargets in CON.testtargets:
        for key, value in a_testtargets.iteritems():
            if (CON.debug == True):
                print '[DEBUG] CON.testtargets key: ' + key + ' value: ' + value
        if (key == ''):
            print '[x] There do not seem to be any valid test targets files defined in the integ.conf file.  Terminating...'
            FLOG.WriteLogFile(CON.logfile, '[x] There do not seem to be any valid test targets files defined in the integ.conf file.  Terminating...\n')            
            print ''
            return -1

    for a_diff in CON.diff:
        for key, value in a_diff.iteritems():
            if (CON.debug == True):
                print '[DEBUG] CON.diff key: ' + key + ' value: ' + value
        if (key == ''):
            print '[x] There do not seem to be any valid diff directories defined in the integ.conf file.  Terminating...'
            FLOG.WriteLogFile(CON.logfile, '[x] There do not seem to be any valid diff directories defined in the integ.conf file.  Terminating...\n')            
            print ''
            return -1

    for a_repo in CON.repo:
        for key, value in a_repo.iteritems():
            if (CON.debug == True):
                print '[DEBUG] CON.repo key: ' + key + ' value: ' + value
        if (key == ''):
            print '[x] Please enter a valid "Gold Version" repository directory in the integ.conf file.  Terminating...'
            FLOG.WriteLogFile(CON.logfile, '[x] Please enter a valid "Gold Version" repository directory in the integ.conf file.  Terminating...\n')            
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

        if (CON.emailpassthrough == False): 
            if (len(CON.password) < 3):
                print '[x] Please enter a valid sender e-mail password in the integ.conf file.  Terminating...'
                FLOG.WriteLogFile(CON.logfile, '[x] Please enter a valid sender e-mail password in the integ.conf file.  Terminating...\n')            
                print ''
                return -1
        else:
            print '[*] E-mail passthrough is active, ignoring password...'
            FLOG.WriteLogFile(CON.logfile, '[*] E-mail passthrough is active, ignoring password...\n')

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

    if (CON.emailalerting == True):
        if (CON.test == True):
            try:
                # Read in our list of recipients
                print '[*] Reading test recipients file: ' + CON.testrecipients
                FLOG.WriteLogFile(CON.logfile, '[*] Reading test recipients file: ' + CON.testrecipients)
                with open(CON.testrecipients.strip(),"r") as fd:
                    file_contents2 = fd.read()
                    CON.recipient_list    = file_contents2.splitlines()
            except:
                # Recipients list read failed, bail!
                print '[x] Unable to read recipients file: ' + CON.recipients
                FLOG.WriteLogFile(CON.logfile, '[x] Unable to read recipients file: ' + CON.recipients) 
                return -1
        else:
            try:
                # Read in our list of recipients
                print '[*] Reading recipients file: ' + CON.recipients
                FLOG.WriteLogFile(CON.logfile, '[*] Reading recipients file: ' + CON.recipients)
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

            if option == 'type':
                CON.type = args[i+1]
                print option + ': ' + CON.type

            if option == 'modules':
                CON.modules = args[i+1]
                print option + ': ' + CON.modules

            if option == 'manifest_file':
                CON.manifest = True
                CON.manifest_file = args[i+1]
                print option + ': ' + CON.manifest_file
                print '' 

            if option == 'addline':
                CON.add = True
                CON.add_line = args[i+1]
                print option + ': ' + CON.add_line
                print '' 

            if option == 'test':
                CON.test = True
                print ''

    #listmodules will cause all other params to be ignored
    if option == 'listmodules':
        CON.listmodules = True
        print option + ': ' + str(CON.listmodules)
        print ''

    else:                                        
        #These are required params so length needs to be checked after all 
        #are read through               
    
        if len(CON.modules) < 3:
            print colored('[x] modules is a required argument.', 'red', attrs=['bold'])
            print ''
            return -1

        if len(CON.type) < 1:
            print colored('[x] type is a required argument.', 'red', attrs=['bold'])
            print ''
            return -1 

    return 0

'''
send_alert()
Function: - Sends the alert e-mail from the address specified
            in the configuration file to potentially several addresses
            specified in the "recipients.txt" file.
'''
def send_alert():

    alert_email = CON.integobject.alert_email
    csv_filename = CON.integobject.csv_filename
    csv_base_filename = 'Integ_' + os.path.basename(csv_filename)
    FLOG = fileio()
    
    email_body = 'Integ has completed a run ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")) + '\n'

    if (CON.debug == True): 
       print '\n[DEBUG] Walking through the output from alert_email ***'
       FLOG.WriteLogFile(CON.logfile, '[DEBUG] Walking through the output from alert_email ***\n')

    if (len(alert_email) == 0):
        print '\n[*] No changes in the monitored scripts have been detected during this run...***'
        FLOG.WriteLogFile(CON.logfile, '[*] No changes in the monitored scripts have been detected during this run...***\n')
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
        msg = MIMEMultipart()
        if (CON.test == True):
            msg['Subject'] = CON.testemail_subject.strip()
        else:
            msg['Subject'] = CON.email_subject.strip()
        msg['From']    = CON.email.strip()
        msg['To']      = recipient_entry
        msg.attach(MIMEText(email_body))

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(csv_filename, "rb").read())
        Encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment; filename=' + csv_base_filename)

        msg.attach(part)
    
        server = smtplib.SMTP(CON.server,int(CON.serverport))
        
        if (CON.emailpassthrough == False):
            server.ehlo()
            server.starttls()
            server.login(CON.email.strip(),CON.password.strip())
        server.sendmail(recipient_entry,recipient_entry,msg.as_string())
        server.quit()
    
        print '[*] Alert email sent!'
        FLOG.WriteLogFile(CON.logfile, '[*] Alert email sent!\n')  
    
    return 0

'''
ListModules()
Function: - List all available modules and their descriptions
'''
def ListModules():
    FConf = fileio()
    count = 0
    addins = ''

    for addins in CON.addins: 
        for key, value in addins.iteritems():
            FConf.ReadFile(CON.modulesdir.strip() + value.strip() + '.py')
            for line in FConf.fileobject:
                if (count == 1):
                    print '[*] ' + value + ': ' + line
                    count = 0
                    break
                if (line.find('***BEGIN DESCRIPTION***') != -1):
                    count = 1              

    return 0

'''
Terminate()
Function: - Attempts to exit the program cleanly when called  
'''     
def Terminate(exitcode):
    sys.exit(exitcode)

'''
Execute()
Function: - Does the doing
'''
def Execute():

    ret = MMS.OrganizeModules(CON.integobject)
    if (ret !=0 ):
        print '[x] Unable to continue module execution.  Terminating...'
        Terminate(ret)  
 
    #send_alert()
       
    return 0

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
    if (ret == -1):
        print '[x] Terminated reading the configuration file...'
        Terminate(ret)

    if (CON.listmodules == True):
        ListModules()
        Terminate(0)

    if (CON.type in CON.types):
        print '[*] Type is ' + CON.type
        for addins in CON.addins: 
            for key, value in addins.iteritems():
                if (key == CON.type):
                    CON.module_manifest.append(value)
            MMS = mms(CON.module_manifest, CON.modulesdir, CON.modules, CON.debug) 
    else:
        print '[x] Type ' + str(CON.type) + ' is not recognized...\n'
        print 'Type must be one of the following:'
        for types in CON.types:
            print types
        print '[x] Terminating...'
        Terminate(-1)   

    if (CON.debug == True):
        print '[DEBUG]: ', CON.module_manifest

    print '[*] Begining run: ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    FLOG.WriteLogFile(CON.logfile, '[*] Begining run: ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")) + '\n')
    print '[*] Executing integ.py v0.3...'
    FLOG.WriteLogFile(CON.logfile, '[*] Executing integ.py v0.3...\n')

    CON.integobject = integclass(CON.debug, CON.test, CON.targets, CON.testtargets, CON.diff, CON.repo, CON.output, CON.logfile, CON.csv_filename, CON.outputdir, CON.manifest_file, CON.add_line, CON.emailalerting, CON.alert_email)
    Execute()

    # Validate the integrity list of remote target urls using MD5 (yes, I know it's not as good as SHA256!!!)
    if ((CON.manifest == False) and (CON.add == False)):
        if (CON.emailalerting == True):
            if (CON.debug == True):
                print '\n[DEBUG] Passing data to send_alert() ***'

            send_alert()

    del CON.integobject

    print '\n[*] Program Complete: ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")) 
    FLOG.WriteLogFile(CON.logfile, '[*] Program Complete: ' + str(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")) + '\n')
    FLOG.WriteLogFile(CON.logfile, '*******************************************************************************************\n')

    Terminate(ret)

'''
END OF LINE
'''
