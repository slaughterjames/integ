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

integ v0.2

Tool developed in Python that takes known file hash and URL information in and verifies the remote location maintains the same version of the file.
Some legwork is required in order to capture the hash values for each file initially. It is recommended that a local copy is kept so that in the event of a change being detected, a diff may be done between the new and old files to seach for malicious alterations.
Due to some hardcoding, the tool should be deposited in the /opt/integ directory. I'd also recommend putting an integ folder in the /home// to put the targets.txt file and other folders.

Usage - integ.py: Usage: [optional] --debug --help Example: /opt/integ/integ.py --debug Required Arguments: --debug - Prints verbose logging to the screen to troubleshoot issues. Recommend piping (>>) to a text file due to the amount of text... --help - You're looking at it!

CHANGELOG VERSION V0.2:
Added e-mail alerting 

CHANGELOG VERSION V0.1:

First iteration of the tool
