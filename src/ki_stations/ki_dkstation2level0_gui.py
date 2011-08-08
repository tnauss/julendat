'''Move Driesen and Kern logger data to level 0 folder structure (DFG-Kilimanjaro).
Copyright (C) 2011 Thomas Nauss, Tim Appelhans

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Please send any comments, suggestions, criticism, or (for our sake) bug
reports to nausst@googlemail.com

@author: Thomas Nauss, Tim Appelhans
@version: 2010-08-06
@license: GNU General Public License
'''

__author__ = "Thomas Nauss <nausst@googlemail.com>, Tim Appelhans"
__version__ = "2010-08-06"
__license__ = "GNU GPL, see http://www.gnu.org/licenses/."

from julendat.processtools.stations.DKStation2Level0 import DKStation2Level0

def main():
    '''Main program function
    Move data from initial logger import to level 0 folder structure.
    '''
    print
    print 'Module: ki_dkstation2level0_gui'
    print 'Version: ' + __version__
    print 'Author: ' + __author__
    print 'License: ' + __license__
    print   
    
    DKStation2Level0(configFile='ki_stations.cnf')
        
if __name__ == '__main__':
    main()

