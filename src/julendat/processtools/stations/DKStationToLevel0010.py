"""Convert D&K level 0 logger data to level 1.
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
__version__ = "2012-01-04"
__license__ = "GNU GPL, see http://www.gnu.org/licenses/"

import sys
import csv
import os
import string
import ConfigParser
from julendat.processtools import time_utilities
from julendat.filetools.stations.dkstations.DKStationDataFile import DKStationDataFile
import shutil
import time
import datetime
from julendat.metadatatools.stations.StationDataFilePath import StationDataFilePath
from julendat.metadatatools.stations.StationInventory import StationInventory
from julendat.metadatatools.stations.StationEntries import StationEntries
from julendat.metadatatools.stations.Level01Standards import Level01Standards
from julendat.filetools.DataFile import DataFile

class DKStationToLevel0010:   
    """Instance for converting D&K logger level 0 to level 1data.
    """

    def __init__(self, filepath, config_file,run_mode="auto"):
        """Inits DKStationToLevel0010. 
        
        Args:
            filepath: Full path and name of the level 0 file
            config_file: Configuration file.
            run_mode: Running mode (auto, manual)
        """
        self.set_run_mode(run_mode)
        self.configure(config_file)
        self.init_filenames(filepath)
        if self.get_run_flag():
            self.run()

    def set_run_mode(self,run_mode):
        """Sets run mode.
        
        Args:
            run_mode: Running mode (default: auto)
        """
        self.run_mode = run_mode

    def get_run_mode(self):
        """Gets run mode.
        
        Returns:
            Running mode
        """
        return self.run_mode

    def configure(self,config_file):
        """Reads configuration settings and configure object.
    
        Args:
            config_file: Full path and name of the configuration file.
        """
        self.config_file = config_file
        config = ConfigParser.ConfigParser()
        config.read(self.config_file)
        self.station_entries = config.get('logger', 'station_entries')
        self.logger_time_zone = config.get('logger', 'logger_time_zone')
        self.tl_data_path = config.get('repository', 'toplevel_processing_plots_path')
        self.station_inventory = config.get('inventory','station_inventory')
        self.project_id = config.get('project','project_id')
        self.level_0005_timezone = config.get('project','level_0005_timezone')
        self.level0010_standards = config.get('general','level0010_standards')
        self.r_filepath = config.get('general','r_filepath')

    def init_filenames(self, filepath):
        """Initializes D&K station data file.
        
        Args:
            filepath: Full path and name of the level 0 file
        """
        try:
            self.filenames = StationDataFilePath(filepath=filepath, \
                                toplevel_path=self.tl_data_path, \
                                logger_time_zone=self.logger_time_zone, \
                                level_0005_time_zone=self.level_0005_timezone)
            self.run_flag = True
        except:
            self.run_flag = False

    def get_run_flag(self):
        """Gets runtime flag information.
        
        Returns:
            Runtime flag.
        """
        return self.run_flag

    def run(self):
        """Executes class functions according to run_mode settings. 
        """
        if self.get_run_mode() == "manual":
            pass
        elif self.get_run_mode() == "auto":
            self.auto()

    def auto(self):
        """Executes class functions in default auto mode.
        """
        self.main()

    def move_data(self):
        """Moves files.
        """
        shutil.move(self.source,self.destination)

    def main(self):
        """Processes level 0000 station files to level 0010.
        """
        self.init_level_0000_ascii_file()
        
        if self.get_run_flag():
            self.get_station_inventory_information()
        
        if self.get_run_flag():
            self.process_level_0005()
        
        print "...finished."

    def init_level_0000_ascii_file(self):
        """Initializes level 000 ascii file.
        """
        try:
            self.level_0000_ascii_file = DKStationDataFile(filepath= \
                self.filenames.get_filename_dictionary()[\
                "level_0000_ascii-filepath"])
            self.run_flag = self.level_0000_ascii_file.get_file_exists()
        except:
            print "Error: level 0000 ascii file could not be read"
            self.run_flag = False

    def get_station_inventory_information(self):
        """Get meta-information from station inventory.
        """
        inventory = StationInventory(filepath=self.station_inventory, \
            serial_number=self.level_0000_ascii_file.get_serial_number())
        self.level_0000_ascii_file.set_header_lines(inventory.get_header_lines())
        self.calibration_coefficients_headers = \
            inventory.get_calibration_coefficients_headers()
        self.calibration_coefficients = inventory.get_calibration_coefficients()
        if self.filenames.get_raw_plot_id() != inventory.get_plot_id():
            print "Error: plot-id does not match"
            self.run_flag = False
            
        elif self.filenames.get_station_id() != inventory.get_station_id():
            print "Error: station-id does not match"
            self.run_flag = False

    def get_level0005_standards(self):
        """Sets format standards for level 1 station data files
        """
        level0005_standard = Level01Standards(\
            filepath=self.level0010_standards, \
            station_id=self.filenames.get_station_id())
        self.level0000_column_headers = \
            level0005_standard.get_level0000_column_headers()
        self.level0005_column_headers = \
            level0005_standard.get_level0005_column_headers()

    def reorder_station_coloumn_entries(self,input_headers,output_headers):
        """Reorder station column entries to match the level 1 standards.
        """
        reorder = [1,2]
        for entry_sce in range (0,len(input_headers)):
            for entry_lce in range(0,len(output_headers)):
                if string.strip(output_headers[entry_lce]) ==  \
                    string.strip(input_headers[entry_sce]):
                        reorder.append(entry_lce+1)
        self.reorder = reorder

    def rename_level0000_headers(self):
        """Rename level 0000 headers to 0005+ convention
        """
        #print self.level_0000_ascii_file.get_column_headers()
        #print self.level0000_column_headers
        ascii_headers = self.level_0000_ascii_file.get_column_headers()
        for col_old in range(0, len(ascii_headers)):
            for col_new in self.level0000_column_headers:
                if col_new[0][0:4] == str.lower(ascii_headers[col_old][0:4]):
                    ascii_headers[col_old] = col_new[1]
        self.level_0000_ascii_file.set_column_headers(ascii_headers)


    def process_level_0005(self):
        """Process level 0000 to level 0005 data set
        """
        self.get_level0005_standards()
        self.rename_level0000_headers()
        
        self.reorder_station_coloumn_entries(\
            self.level_0000_ascii_file.get_column_headers(), \
            self.level0005_column_headers)

        self.write_level_0005()
        
    def write_level_0005(self):
        """Write level 0005 dataset.
        """
        output=[]
        for row in self.level_0000_ascii_file.get_data():
            act_time = time_utilities.convert_timezone( \
                datetime.datetime.strptime(row[0]+row[1],"%d.%m.%y%H:%M:%S"), \
                self.level_0005_timezone).strftime("%Y-%m-%d %H:%M:%S")
            act_out=      [act_time, \
                           self.level_0005_timezone, \
                           self.filenames.get_aggregation(), \
                           self.filenames.get_plot_id(), \
                           'NaN', \
                           self.filenames.get_station_id(), \
                           self.filenames.get_calibration_level(), \
                           '0000']
            for i in range(2, len(self.reorder)):
                act_out = act_out + [float(row[self.reorder[i]-7])] 
            output.append(act_out)
        print output[0]        
        
        output_path = self.filenames.get_filename_dictionary()\
                      ["level_0005_ascii-path"]
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        outfile = open(self.filenames.get_filename_dictionary()\
                       ["level_0005_ascii-filepath"],"w")
        
        outfile.write(', '.join(str(i) for i in self.level0005_column_headers) + '\n')
        writer = csv.writer(outfile,delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for row in output:
            writer.writerow(row)
        outfile.close()
        
        '''
        if self.filenames.get_station_id().find("wxt") != -1:
            self.check_wxt()
            r_input_filepath = \
                'asciipath="' + \
                self.filenames.get_filename_dictionary()\
                ["temp_filepath"] + '",'
        else:
            r_input_filepath = \
                'asciipath="' + \
                self.filenames.get_filename_dictionary()\
                ["level_0000_ascii-filepath"] + '",'
        '''
        sys.exit()
            
    
    def level_005(self):
        """Compute level 0.5 station data sets
        """
        if not os.path.isdir(self.filenames.get_filename_dictionary()["level_0005_ascii-path"]):
            os.makedirs(self.filenames.get_filename_dictionary()["level_0005_ascii-path"])
        time_difference_in_seconds = \
            time_utilities.timezone_difference(self.level_0005_timezone)
        r_source = 'source("' + self.r_filepath + os.sep + \
            'ComputeLevel005File.R")'
        r_keyword = "compute_level_005_file"
        #If station is wxt, create temporary file and check for comments
        if self.filenames.get_station_id().find("wxt") != -1:
            self.check_wxt()
            r_input_filepath = \
                'asciipath="' + \
                self.filenames.get_filename_dictionary()\
                ["temp_filepath"] + '",'
        else:
            r_input_filepath = \
                'asciipath="' + \
                self.filenames.get_filename_dictionary()\
                ["level_0000_ascii-filepath"] + '",'
        r_output_filepath = 'outpath="' + \
            self.filenames.get_filename_dictionary()\
            ["level_0005_ascii-filepath"] + '",'
        r_plot_id = 'plotID="' + self.filenames.get_raw_plot_id() + '",'
        r_station_id = 'loggertype="' + \
            self.filenames.get_station_id() + '",'
        r_calibration_coefficients = 'cf=c('  + \
           self.convert_floatlist2string(self.calib_coefficients) + '),'
        self.reorder_station_coloumn_entries()
        r_reorder = 'reorder=c('+ self.convert_floatlist2string(self.reorder) + '),'
        r_skip = 'skip=' + str(self.header_lines) + ','
        #r_quality = 'quality=' + self.filenames.get_quality() + ','
        r_quality = 'quality=0005,'
        r_adjust_time = 'adjust_time=' + str(time_difference_in_seconds) + ','
        r_order_out = 'order_out=c(' + \
            self.convert_list2string(self.level10_column_entries) + ')'
            
        r_cmd = r_source + "\n" + \
            r_keyword + " (\n" + \
            r_input_filepath + "\n" + \
            r_output_filepath + "\n" + \
            r_plot_id + "\n" + \
            r_station_id + "\n" + \
            r_calibration_coefficients + "\n" + \
            r_reorder + "\n" + \
            r_skip + "\n" + \
            r_quality + "\n" + \
            r_adjust_time + "\n" + \
            r_order_out  + ") \n"
        r_script = "compute_level_005_file.R" 
        f = open(r_script,"w")
        f.write(r_cmd)
        f.close()
        r_cmd = "R --no-save < " + r_script
        os.system(r_cmd)
        #Delete temporary file created for wxt processing
        if self.filenames.get_station_id() == "wxt":
            cmd = "rm " + self.filenames.get_filename_dictionary()\
                ["temp_filepath"]
            os.system(cmd)
            
    def level_010(self):
        """Compute level 1.0 station data sets
        """
        #Check if monthly combined target file for level 0.6 already exists
        filenumber = len(self.filenames.get_filename_dictionary()\
                         ["level_010_ascii-filepath"])

        level_010_file = []
        for act_file in range(0, filenumber):
            level_010_file.append(DataFile(\
                 self.filenames.get_filename_dictionary()\
                 ["level_010_ascii-filepath"][act_file]))
            if not os.path.isdir(self.filenames.get_filename_dictionary()["level_010_ascii-path"][act_file]):
                os.makedirs(self.filenames.get_filename_dictionary()["level_010_ascii-path"][act_file])
            if level_010_file[act_file].get_file_exists() != True:
                self.init_level_010_file(level_010_file[act_file].get_filepath())
            self.compute_level_010_file(\
                 self.filenames.get_filename_dictionary()\
                 ["level_0005_ascii-filepath"], \
                 level_010_file[act_file].get_filepath())
            
    def init_level_010_file(self, filepath):
        """Init level 1.0 file
        """
        r_source = 'source("' + self.r_filepath + os.sep + \
            'InitLevel010File.R")'
        r_keyword = "init_level_010_file"
        r_output_filepath = 'outpath="' + filepath + '",'
        r_start_time = 'start_time="' + os.path.split(filepath)[1][19:31] + '00",'
        r_end_time = 'end_time="' + os.path.split(filepath)[1][32:44] + '01",'
        r_time_step = 'time_step=' + str(self.filenames.get_time_step_delta()) + ''
        #TODO(tnauss): Read time aggregation from configuration file,
        #and adjust output filenames.
        #2012-01-04 10:22:58 UTC
        r_time_step = str(60*5.0)
        r_cmd = r_source + "\n" + \
            r_keyword + " (\n" + \
            r_output_filepath + "\n" + \
            r_start_time + "\n" + \
            r_end_time + "\n" + \
            r_time_step + ")\n"
        r_script = "init_level_010_file.R" 
        f = open(r_script,"w")
        f.write(r_cmd)
        f.close()
        r_cmd = "R --no-save < " + r_script
        print r_cmd
        os.system(r_cmd)

    def compute_level_010_file(self,station_filepath,level_010_filepath):
        """Fill level 1.0 file
        """
        station_file = open(station_filepath)
        for header_lines in range (0,1):
            station_header = station_file.next()
        reader = csv.reader(station_file,delimiter=',', \
                            quoting=csv.QUOTE_NONNUMERIC)
        station_input =[]
        for row in reader:
            station_input.append(row)
        station_file.close()

        level_010_file = open(level_010_filepath)
        for header_lines in range (0,1):
            level_010_header = level_010_file.next()
        reader = csv.reader(level_010_file,delimiter=',', \
                            quoting=csv.QUOTE_NONNUMERIC)
        level_10_input =[]
        for row in reader:
            level_10_input.append(row)
        level_010_file.close()

        level_10_counter = 0
        out = []
        for level_10_row in level_10_input:
            found = False
            station_counter = 0
            for station_10_row in station_input:
                if level_10_input[level_10_counter][0] == station_input[station_counter][0]:
                    out.append(station_input[station_counter])
                    found = True
                    break
                station_counter = station_counter + 1
            if found != True:
                out.append(level_10_input[level_10_counter])
            level_10_counter = level_10_counter + 1


        outfile = open(level_010_filepath,"w")
        outfile.write(station_header)
        writer = csv.writer(outfile,delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for row in out:
            writer.writerow(row)
        outfile.close()
        
        """
        r_source = 'source("' + self.r_filepath + os.sep + \
            'ComputeLevel010File.R")'
        r_keyword = "compute_level_010_file"
        r_station_file = 'station_file="' + station_file + '",'
        r_level_010_file = 'level_010_file="' + level_010_file + '"'
        r_quality = 'quality=' + self.filenames.get_quality() + ','
        r_cmd = r_source + "\n" + \
            r_keyword + " (\n" + \
            r_station_file + "\n" + \
            r_level_010_file + "\n" + \
            r_quality + ")\n"
        r_script = "compute_level_010_file.R" 
        f = open(r_script,"w")
        f.write(r_cmd)
        f.close()
        r_cmd = "R --no-save < " + r_script
        print r_cmd
        #os.system(r_cmd)
        """
           
    def convert_list2string(self,list):
        """Convert list of strings to one string.
        
        Returns:
            Combined string extracted from list.
        """
        output = list[0]
        for i in range(1, len(list)):
            output = output + "," + list[i]
        return output

    def convert_floatlist2string(self,list):
        """Convert list of floats to one string.
        
        Returns:
            Combined string extracted from float value list.
        """
        output = str(list[0])
        for i in range(1, len(list)):
            output = output + "," + str(list[i])
        return output
            


    def check_wxt(self):
        """Check level 0 wxt logger file for comment lines within the data rows.
        """
        original_file = open(self.filenames.get_filename_dictionary()\
                            ["level_0000_ascii-filepath"],'r')
        target_file = open(\
            self.filenames.get_filename_dictionary()["temp_filepath"],'w')
        row_counter = 0
        
        for row in original_file:
            if row_counter < 7:
                target_file.write(row)
                row_counter = row_counter + 1
            try:
                time.strptime(row[0:8], "%d.%m.%y")
                target_file.write(row)
            except:
                continue
