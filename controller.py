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
controller.py - 
'''

#python imports
import imp
import sys
from array import *

#programmer generated imports


'''
controller
Class: This class is responsible for maintaining key variable values globally
'''
class controller:
    '''
    Constructor
    '''
    def __init__(self):

        self.debug = False
        self.modulesdir = ''
        self.modules = ''
        self.test = False
        self.type = ''
        self.types = ''
        self.addins = ''
        self.targets = ''
        self.testtargets = ''
        self.diff = ''
        self.repo = ''
        self.output = ''
        self.logfile = ''
        self.emailalerting = False
        self.server = ''
        self.serverport = ''
        self.emailpassthrough = False
        self.recipients = ''
        self.testrecipients = ''
        self.email = ''
        self.email_subject = ''
        self.testemail_subject = ''
        self.password = ''
        self.alert_email = []
        self.target_list = ''
        self.recipient_list = ''
        self.csv_filename = ''
        self.outputdir = ''
        self.manifest = False
        self.manifest_file = ''
        self.listmodules = ''
        self.module_manifest = []
        self.add = False
        self.add_line = ''
