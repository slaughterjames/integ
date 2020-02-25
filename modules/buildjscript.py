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
Type: manifest - Description: Builds the target list for the jscript module.
***END DESCRIPTION***
'''
def POE(POE):

    error = False
    targets = ''
    diff = ''
    repo = ''
    split_string = ''
    owner_domain = ''
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

    if (str(POE.manifest_file) == ''):
        print '[x] Unknown manifest file.  Use the --manifest_file flag!'
        return -1

    with open (targets, mode='w') as target_list:
        writer = csv.writer(target_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Owner Domain','URL','Original Hash Value'])
        with open(POE.manifest_file) as manifest_file:
            reader = csv.reader(manifest_file, delimiter=',')
            read_count = 0        
            for row in reader:
                if (read_count == 0):
                    if (POE.debug == True):
                        print 'Column names are: ' + ', '.join(row)
                    read_count +=1
                else:    
                    if (POE.debug == True):
                        print '\n[DEBUG] ' + ', '.join(row)
                    else:
                        if (row[1] != ''):
                            print 'Owner: ' + row[0] + ' Address: ' + row[1]
                            url = row[1].strip()
                            print '[*] Downloading URL...'
                            try:
                                remote_file = urllib2.urlopen(url)
                                data = remote_file.read()
                                remote_hash_value.update(data)

                                if (POE.debug == True):
                                    print '[*] Owner: ' + row[0] + ' Address: ' + row[1] + ' Remote Hash Value: ' + str(remote_hash_value.hexdigest())

                                writer.writerow([row[0],row[1],str(remote_hash_value.hexdigest())])

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
