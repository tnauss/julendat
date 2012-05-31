"""Handle station entries information.
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
"""

__author__ = "Thomas Nauss <nausst@googlemail.com>, Tim Appelhans"
__version__ = "2012-01-17"
__license__ = "GNU GPL, see http://www.gnu.org/licenses/"

import ConfigParser


class Level01Standards():   
    """Instance for handling station inventory information.
    
    This instance handles station inventory information based on the serial
    number of the station.
    """
    def __init__(self, filepath, station_id):
        """Inits StationEntries.
        
        Args (from class DataFile):
            filepath: Full path and name of the data file
            io_asccess: IO access (r-read,w-write,rw-read/write)
        
        Args:
            serial_number: Serial number of the station
        """       
        self.filepath = filepath
        if station_id.find("rad") != -1:
            self.station_id = '000rad'
        else:
            self.station_id = station_id

    def set_level0000_standards(self):
        """Sets station entries information from station id
        """
        config = ConfigParser.ConfigParser()
        config.read(self.filepath)
        self.level0000_column_headers = \
            config.items(self.station_id +  '_header_0000')

    def set_level0000_soil_standards(self, sp_id):
        """Sets station entries from station/plot id for soil parameters
        
        Args:
            sp_id: Station or plot id
        """
        config = ConfigParser.ConfigParser()
        config.read(self.filepath)
        self.level0000_soil_headers = \
            config.items(sp_id +  '_soil_parameters_header_0000')

    def set_level0005_standards(self):
        """Sets station entries information from station id
        """
        config = ConfigParser.ConfigParser()
        config.read(self.filepath)
        temp = config.get(self.station_id +  '_header_0005', 'header_0005')
        temp = temp.rsplit(',\n')
        self.level0005_column_headers = temp

    def set_level0050_standards(self):
        """Sets station entries information from station id
        """
        config = ConfigParser.ConfigParser()
        config.read(self.filepath)
        temp = config.get(self.station_id +  '_header_0050', 'header_0050')
        temp = temp.rsplit(',\n')
        self.level0050_column_headers = temp

    def get_level0000_column_headers(self):
        """Gets column headers of level 0000 file
        
        Returns:
            Column headers of level 0000 file
        """
        try: self.level0000_column_headers
        except:
            self.set_level0000_standards()
        return self.level0000_column_headers

    def get_level0000_soil_headers(self, sp_id):
        """Gets column headers of level 0000 file for soil parameters
        
        Returns:
            Column headers of level 0000 file for soil parameters
        """
        self.set_level0000_soil_standards(sp_id)
        return self.level0000_soil_headers

    def get_level0005_column_headers(self):
        """Gets column headers of level 0005 file
        
        Returns:
            Column headers of level 0005 file
        """
        try: self.level0005_column_headers
        except:
            self.set_level0005_standards()
        return self.level0005_column_headers

    def get_level0050_column_headers(self):
        """Gets column headers of level 0050 file
        
        Returns:
            Column headers of level 0050 file
        """
        try: self.level0050_column_headers
        except:
            self.set_level0050_standards()
        return self.level0050_column_headers
