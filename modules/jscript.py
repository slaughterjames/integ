#python imports
import sys
import os
import subprocess
import hashlib
import urllib2
import csv
import datetime
import time
from datetime import date
from array import *
from termcolor import colored

#third-party imports
#No third-party imports

#programmer generated imports
from fileio import fileio

'''
***BEGIN DESCRIPTION***
Type: hash - Description: Compares the local vs remote MD5 hash of a 3rd party JavaScript file.
***END DESCRIPTION***
'''
def POE(POE):

    FLOG = fileio()
    FCSV = fileio()
    error = False
    targets = ''
    diff = ''
    repo = ''
    owner_domain = ''
    url = ''
    orig_hash_value = ''
    remote_file = ''
    remote_hash_value = hashlib.md5() 
    change = False
    notes = ''
    POE.csv_filename = POE.output + str(datetime.datetime.now().strftime("%d-%m-%Y_%I:%M")) + '.csv'
    wget_data = ''
    Count = 0 
    read_count = 0

    if (POE.test == True):
        for a_targets in POE.testtargets: 
            for key, value in a_targets.iteritems():
                if (key == 'jscript'):
                    targets = value
    
        if (str(targets) == ''):
            print '[x] Unknown targets file.  Please add one for jscript in the integ.conf file in /opt/integ'
            return -1
    else:
        for a_targets in POE.targets: 
            for key, value in a_targets.iteritems():
                if (key == 'jscript'):
                    targets = value
    
        if (str(targets) == ''):
            print '[x] Unknown targets file.  Please add one for jscript in the integ.conf file in /opt/integ'
            return -1

    for a_diff in POE.diff: 
        for key, value in a_diff.iteritems():
            if (key == 'jscript'):
                diff = value
    
    if (str(diff) == ''):
        print '[x] Unknown diff directory.  Please add one for jscript in the integ.conf file in /opt/integ'
        return -1

    for a_repo in POE.repo: 
        for key, value in a_repo.iteritems():
            if (key == 'jscript'):
                repo = value
    
    if (str(repo) == ''):
        print '[x] Unknown repo directory.  Please add one for jscript in the integ.conf file in /opt/integ'
        return -1

    FCSV.WriteLogFile(POE.csv_filename, 'Owner Domain,URL,Original Hash Value,Remote Hash Value,Change?,Notes\n')        


    #Iterate through target list: 
    with open(targets.strip()) as target_file_b:
        reader = csv.reader(target_file_b, delimiter=',')
        for row in reader:
            if (read_count == 0):
                if (POE.debug == True):
                   print '[DEBUG] Column names are: ' + ', '.join(row)
                read_count +=1
            else:
                owner_domain = row[0].strip()
                url = row[1].strip()
                orig_hash_value = row[2].strip()

                print '\n[*] Owner Domain: ' + owner_domain.strip()
                FLOG.WriteLogFile(POE.logfile, '\n[*] Owner Domain: ' + owner_domain.strip() + '\n')
                print '[*] URL: ' + url.strip()
                FLOG.WriteLogFile(POE.logfile, '[*] URL: ' + url.strip() + '\n')
                print '[*] Original Hash Value: ' + orig_hash_value.strip()
                FLOG.WriteLogFile(POE.logfile, '[*] Original Hash Value: ' + orig_hash_value.strip() + '\n')
        
                print '[*] Downloading URL...'
                try:
                    remote_file = urllib2.urlopen(url)
                    data = remote_file.read()
                    remote_hash_value.update(data)

                    print '[*] Remote Hash Value: ' + str(remote_hash_value.hexdigest())
                    FLOG.WriteLogFile(POE.logfile, '[*] Remote Hash Value: ' + str(remote_hash_value.hexdigest()) + '\n')
                except urllib2.HTTPError, e:
                    # Something's gone funny at the protocol level and thrown an error...
                    error = True
                    print colored('[x] HTTPError: Error connecting to remote host: ' + str(e.code) , 'red', attrs=['bold'])
                    FLOG.WriteLogFile(POE.logfile, '[x] Error connecting to remote host: ' + str(e.code) + '\n')
                    notes = str(e.code)  
                except urllib2.URLError, e:
                    # If we're here, there's likely been a connection error to the remote host
                    error = True
                    print colored('[x] URLError: Error connecting to remote host: ' + str(e.reason) , 'red', attrs=['bold'])
                    FLOG.WriteLogFile(POE.logfile, '[x] Error connecting to remote host: ' + str(e.reason) + '\n')
                    notes = str(e.reason)
                except:
                    #Something really bad has happened and there isn't a specific error handler for it...
                    error = True
                    print colored('[x] General exception handler tripped...', 'red', attrs=['bold'])
                    FLOG.WriteLogFile(POE.logfile, '[x] General exception handler tripped...\n')
                    notes = 'General exception handler tripped...'

                if (error == True):
                    print colored('[-] Skipping to next target due to error...\n', 'yellow', attrs=['bold'])
                    FCSV.WriteLogFile(POE.csv_filename, owner_domain + ',' + url + ',' + str(orig_hash_value) + ',' + '---------------------------------------------------------' + ',' + str(change) + ',' + notes + '\n')

                    if (POE.emailalerting == True):
                        POE.alert_email.append('An error was encountered for OWNER: ' + owner_domain + ' - URL: ' + url + ' - ORIG MD5: ' + str(orig_hash_value) + ' - NOTES: ' + notes + '\n')
                else:
                    if (str(remote_hash_value.hexdigest()) == orig_hash_value.strip()):
                        print colored('[*] Original and remote MD5 hashes match!', 'green', attrs=['bold'])
                        FLOG.WriteLogFile(POE.logfile, '[*] Original and remote MD5 hashes match!\n')
                        notes = 'N/A'
                        FCSV.WriteLogFile(POE.csv_filename, owner_domain + ',' + url + ',' + str(orig_hash_value) + ',' + str(remote_hash_value.hexdigest()) + ',' + str(change) + ',' + notes + '\n')
                    else:
                        print colored('[x] Original and remote MD5 hashes DO NOT match!', 'red', attrs=['bold'])
                        FLOG.WriteLogFile(POE.logfile, '[*] Original and remote MD5 hashes DO NOT match!!\n')
                        change = True
                        if (POE.emailalerting == True):
                            POE.alert_email.append('Original and remote MD5 hashes DO NOT match for OWNER: ' + owner_domain + ' - URL: ' + url + ' - ORIG MD5: ' + str(orig_hash_value) + ' - REMOTE MD5: ' + str(remote_hash_value.hexdigest()) + '\n')

                        print '[*] Downloading additional version...'
                        FLOG.WriteLogFile(POE.logfile, '[*] Downloading additional version...\n')

                        #Validate if the remote file has already been downloaded and bail if it already has.
                        if os.path.exists(diff + str(remote_hash_value.hexdigest()) + '.js'):
                            print '[*] File previously downloaded to: ' + diff + str(remote_hash_value.hexdigest()) + '.js '
                            FLOG.WriteLogFile(POE.logfile, '[*] File previously downloaded to: ' + diff + str(remote_hash_value.hexdigest()) + '.js \n')
                            notes += ' - File previously downloaded to: ' + diff + str(remote_hash_value.hexdigest()) + '.js' 
                        else: 
                            if (POE.debug == True):
                                print '[DEBUG] wget --no-check-certificate --output-document=' + diff + str(remote_hash_value.hexdigest()) + '.js ' + url

                            #WGet flags: 
                            #            --no-check-certificate - Will not balk when a site's certificate doesn't match the target domain.
                            #            --output-document - output to given filename.
            
                            subproc = subprocess.Popen('wget --output-document=' + diff + str(remote_hash_value.hexdigest()) + '.js ' + url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            if (POE.debug == True):
                                print '\n[DEBUG] Printing WGet output ***'
                                for wget_data in subproc.stdout.readlines():
                                    print '[DEBUG] ' + wget_data

                            print '[*] File downloaded to: ' + diff + str(remote_hash_value.hexdigest()) + '.js '
                            FLOG.WriteLogFile(POE.logfile, '[*] File downloaded to: ' + diff + str(remote_hash_value.hexdigest()) + '.js \n')

                            notes += ' - File downloaded to: ' + diff + str(remote_hash_value.hexdigest()) + '.js' 
                
                        FCSV.WriteLogFile(POE.csv_filename, owner_domain + ',' + url + ',' + str(orig_hash_value) + ',' + str(remote_hash_value.hexdigest()) + ',' + str(change) + ',' + notes + '\n')

                #Prior to clearing variable values, print under debug for troubleshooting.
                if (POE.debug == True):
                    print '\n[DEBUG] Printing variable info prior to wiping ***'
                    print '[DEBUG] owner_domain: ' + owner_domain
                    print '[DEBUG] url: ' + url 
                    print '[DEBUG] orig_hash_value: ' + orig_hash_value 
                    print '[DEBUG] remote_hash_value: ' + str(remote_hash_value.hexdigest())
                    print '[DEBUG] change: ' + str(change)
                    print '[DEBUG] notes: ' + notes
                    print '[DEBUG] remote_file: ' + str(remote_file)
                    print '[DEBUG] POE.alert_email: ' + str(POE.alert_email)  
        
                #Try to observe some proper variable hygiene and avoid data leakage between runs of the for loop.
                owner_domain = '' 
                url = ''
                orig_hash_value = ''
                remote_hash_value = hashlib.md5()
                change = False
                error = False
                notes = ''
                remote_file = ''
                data = ''

                #Move the counter ahead to access the next element in the target list.
                Count += 1


        print colored('\n[*] Output file created at: ' + POE.csv_filename, 'green', attrs=['bold'])
        FLOG.WriteLogFile(POE.logfile, '[*] Output file created at: ' + POE.csv_filename + '\n')
                               
    return 0

