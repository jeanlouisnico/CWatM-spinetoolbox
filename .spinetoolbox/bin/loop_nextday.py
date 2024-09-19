# -----------------------------------------------------------------------------------------
# Name:        loop_nextday
# Purpose:     This routine is used to read the output files created by CWatM
#              and to be passed to FlexTool. The files that needs to be used and modified 
#              are defined here and FlexTool process should be called from here. 
#              FlexTool should return the modified files with the same name. These files are
#              then saved and located in the output folder that will be re-imported into the
#              next daily run of CWatMl
#
# Author:      Jean-Nicolas Louis
#
# Created:     15/07/2024
# Copyright:   (c) JNL 2024
# -----------------------------------------------------------------------------------------

import configparser
from CWatM_Module.management_modules.globals import *
from CWatM_Module.management_modules.messages import *
import difflib  # to check the closest word in settingsfile, if an error occurs
import datetime
from datetime import timedelta
import sys
from spinedb_api import DatabaseMapping
import json
import spinedb_api as api
import collections.abc
#from pathlib import Path
#import os

# get the ini file
inifile = sys.argv[1]

# Get the database URL
url = sys.argv[2]

# Get the alternatives for the scenario looping where variables can be changed into
alt_file = sys.argv[3]
print(alt_file)
with open(alt_file) as f:
    data_alt = json.load(f)

print(data_alt)
# Declare the alternative where the calibration variables have been declared
with DatabaseMapping(url) as db_map:
    real_url = db_map.db_url 
with open("out.dat", "w") as out_file:
    out_file.writelines([f"{real_url}\n"])

class ExtParser(configparser.ConfigParser):
    """
    addition to the parser to replace placeholders

    Example:
        PathRoot = C:/work
        MaskMap = $(FILE_PATHS:PathRoot)/data/areamaps/area.tif

    """

    #implementing extended interpolation
    def __init__(self, *args, **kwargs):
        self.cur_depth = 0
        configparser.ConfigParser.__init__(self, *args, **kwargs)

    def get(self, section, option, raw=False, vars=None, **kwargs):
        """
        def get(self, section, option, raw=False, vars=None
        placeholder replacement

        :param section: section part of the settings file
        :param option: option part of the settings file
        :param raw:
        :param vars:
        :return:
        """

        #h1 = sys.tracebacklimit
        #sys.tracebacklimit = 0  # no long error message
        try:
           r_opt = configparser.ConfigParser.get(self, section, option, raw=True, vars=vars)
        except:
             print(section, option)
             closest = difflib.get_close_matches(option, list(binding.keys()))
             if not closest: closest = ["- no match -"]
             msg = "Error 116: Closest key to the required one is: \"" + closest[0] + "\""
             raise CWATMError(msg)

        #sys.tracebacklimit = h1   # set error message back to default
        if raw:
            return r_opt

        ret = r_opt
        self.cur_depth = self.cur_depth - 1
        return ret

def writealt_to_file(var, alt):
    with open("out.dat", "a") as out_file:
        out_file.writelines([f"{var};{alt} \n"])

def allocate_var_to_alt(var, newvalue, highrank, data_alt, sql_url, ECN):
    #value, value_type = api.to_database(newvalue)
    print(f"{newvalue} of type {type(newvalue)}")
    if isinstance(newvalue, bool) or isinstance(newvalue, str):
        value, value_type = api.to_database(newvalue)
        # Check if it is a string
    elif isinstance(newvalue, datetime.date):
        parsed_value = api.DateTime(newvalue.strftime("%Y-%m-%d"))
        value, value_type = api.to_database(parsed_value)
    elif isinstance(newvalue, collections.abc.Sequence):
        #print(data[key2])
        if isinstance(newvalue, datetime.date):
            parsed_value = api.Array([dates.strftime("%Y-%m-%d") for dates in newvalue])
        else:
            parsed_value = api.Array(newvalue)
            value, value_type = api.to_database(parsed_value)
    elif isinstance(newvalue, float) or isinstance(newvalue, int):
        value, value_type = api.to_database(newvalue)
    # Loop through the alternative and exit when the it is found (from highest to lowest ranked)
    foundalt = False
    while highrank > 0:
        alt_name = data_alt[str(highrank)]
        with DatabaseMapping(sql_url) as db_map:
            param_val = db_map.get_parameter_value_item(entity_class_name=ECN, entity_byname=(ECN,), parameter_definition_name=var, alternative_name=alt_name)
            if not param_val:
                print(f"The variable {var} does not exists in the alternative {alt_name}")
                highrank -= 1
            else:
                foundalt = True
                writealt_to_file(var, alt_name)
                print(f"    The variable {var} exists in the alternative {alt_name}")
                data_spdb = api.from_database(param_val.get("value"), param_val.get("type"))
                try:
                    print(f"    Old value: {str(data_spdb.value)} - New value: {str(value)}")
                except:
                    print("     new value was found")
                highrank = 0

                db_map.get_parameter_value_item(
                    entity_class_name=ECN,
                    entity_byname=(ECN,),
                    parameter_definition_name=var,
                    alternative_name=alt_name,
                    ).update(value=value, type=value_type)
                
                try:
                    db_map.commit_session(f"Updated variable {var} in a loop in alternative {alt_name}")
                    print("Database committed")
                except Exception as error:
                    print("nothing to commit:", error)
        
    
    if not foundalt:
        print(f"The variable {var} was not found in the database")

    return

if not(os.path.isfile(inifile)):
    msg = "Error 302: Settingsfile not found!\n"
    raise CWATMFileError(inifile,msg)

config = ExtParser()
config.optionxform = str
config.sections()
config.read(inifile)

# Get the Stepstart value
spinup = config['TIME-RELATED_CONSTANTS']["SpinUp"]
spinup = datetime.datetime.strptime(spinup, '%d/%m/%Y')
spinup += datetime.timedelta(days=1)
spinup = datetime.datetime.date(spinup)

stepend = config['TIME-RELATED_CONSTANTS']["StepEnd"]
stepend = datetime.datetime.strptime(stepend, '%d/%m/%Y')
stepend += datetime.timedelta(days=1)
stepend = datetime.datetime.date(stepend)

stepinit = config['INITITIAL CONDITIONS']["StepInit"]



load_initial = True

# Look for the variables in the database from the winning alternative to the lowest ranked alternative and change the value
highrank = len(data_alt)
allocate_var_to_alt("SpinUp", spinup, highrank, data_alt, url, "TIME-RELATED_CONSTANTS")
allocate_var_to_alt("StepEnd", stepend, highrank, data_alt, url, "TIME-RELATED_CONSTANTS")
allocate_var_to_alt("load_initial", load_initial, highrank, data_alt, url, "INITITIAL CONDITIONS")

print(stepinit)
