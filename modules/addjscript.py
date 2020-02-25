#python imports
import sys
import os
import subprocess
import hashlib
import urllib2
import csv
from termcolor import colored

#third-party imports
#No third-party imports

#programmer generated imports
from fileio import fileio

'''
***BEGIN DESCRIPTION***
Type: add - Description: Allows the addition of new targets to the jscript target file.
***END DESCRIPTION***
'''
def POE(POE):

    error = False
    split_string = ''
    owner_domain = ''
    targets = ''
    repo = ''
    url = ''
    orig_hash_value = ''
    remote_file = ''
    remote_hash_value = hashlib.md5()

    for a_targets in POE.targets: 
        for key, value in a_targets.iteritems():
            if (key == 'jscript'):
                targets = value
    
    if (str(targets) == ''):
        print '[x] Unknown targets file.  Please add one for jscript in the integ.conf file in /opt/integ'
        return -1

    for a_repo in POE.repo: 
        for key, value in a_repo.iteritems():
            if (key == 'jscript'):
                repo = value
    
    if (str(repo) == ''):
        print '[x] Unknown repo directory.  Please add one for jscript in the integ.conf file in /opt/integ'
        return -1

    if (str(POE.add_line) == ''):
        print colored('[x] Add line empty.  Use the --addline flag!', 'red', attrs=['bold'])
        return -1
    elif (POE.add_line.find(',') == -1):
        print colored('[x] Add line not formatted correctly.  Must be \"ownerdomain.com,http://ownerurl.com\"', 'red', attrs=['bold'])
    else:
        split_string = POE.add_line.split(",")
        owner_domain = split_string[0]
        url = split_string[1] 

    with open (targets, mode='a') as target_list:
        writer = csv.writer(target_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if ((owner_domain != '') and (url != '')):
            print '[*] Owner: ' + owner_domain + ' Address: ' + url
            url = url.strip()
            print '[*] Downloading URL...'
            try:
                remote_file = urllib2.urlopen(url)
                data = remote_file.read()
                remote_hash_value.update(data)

                if (POE.debug == True):
                    print '[*] Owner: ' + owner_domain + ' Address: ' + url + ' Remote Hash Value: ' + str(remote_hash_value.hexdigest())

                writer.writerow([owner_domain,url,str(remote_hash_value.hexdigest())])

                if (POE.debug == True):
                    print '[DEBUG] wget --no-check-certificate --output-document=' + diff + str(remote_hash_value.hexdigest()) + '.js ' + url

                print '[*] Writing to repository...'
                #WGet flags: 
                #            --no-check-certificate - Will not balk when a site's certificate doesn't match the target domain.
                #            --output-document - output to given filename.
            
                subproc = subprocess.Popen('wget --output-document=' + repo + str(remote_hash_value.hexdigest()) + '.js ' + url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            except urllib2.HTTPError, e:
                # Something's gone funny at the protocol level and thrown an error...
                print colored('[x] HTTPError: Error connecting to remote host: ' + str(e.code) , 'red', attrs=['bold'])  
            except urllib2.URLError, e:
                # If we're here, there's likely been a connection error to the remote host
                print colored('[x] URLError: Error connecting to remote host: ' + str(e.reason) , 'red', attrs=['bold'])
            except:
                #Something really bad has happened and there isn't a specific error handler for it...
                print colored('[x] General exception handler tripped...', 'red', attrs=['bold']) 
                owner_domain = '' 

            #Try to observe some proper variable hygiene and avoid data leakage between runs of the for loop
            url = ''
            orig_hash_value = ''
            remote_hash_value = hashlib.md5()
            remote_file = ''
            data = ''       

    return 0
