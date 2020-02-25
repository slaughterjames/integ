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

'''
integclass.py - This file is responsible maintaining the integ object as it moves from module to module
'''

#python imports
from array import *

#programmer generated imports
from controller import controller

'''
integclass - This file is responsible maintaining the integ object as it moves from module to module
'''
class integclass:
    '''
    Constructor
    '''
    def __init__(self, debug, test, targets, testtargets, diff, repo, output, logfile, csv_filename, outputdir, manifest_file, add_line, emailalerting, alert_email):

        self.debug = debug
        self.test = test
        self.targets = targets
        self.testtargets = testtargets
        self.diff = diff
        self.repo = repo
        self.output = output
        self.logfile = logfile
        self.csv_filename = csv_filename
        self.outputdir = outputdir
        self.manifest_file = manifest_file
        self.emailalerting = emailalerting  
        self.alert_email = alert_email
        self.add_line = add_line
