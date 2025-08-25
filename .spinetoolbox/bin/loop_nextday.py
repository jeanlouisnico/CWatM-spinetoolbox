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
import glob 
#from pathlib import Path
#import os

# get the ini file
inifile = sys.argv[1]
#inifile = "C:/Users/JLJEAN/.spinetoolbox/work/process_to_flextool__92b8877f66b04dcbba370bca4ebb5c39__toolbox/cwatm_input.ini"
# Get the database URL
url = sys.argv[3]
#url="sqlite:///c:\git\cwatm-spinetoolbox-dev\.spinetoolbox\items\data_store\cwatmdb_new.sqlite"
# Get the alternatives for the scenario looping where variables can be changed into
#alt_file = "C:/Users/JLJEAN/.spinetoolbox/work/export_to_ini_calib__3577b232e0bb442d9a5c21c5364fa51b__toolbox/alt_list.json"
alt_file = sys.argv[2]
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
        print(f"The variable {var} with value {newvalue} is of type bool or str")
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
        print(f"The variable {var} with value {newvalue} is of type float or int")
        value, value_type = api.to_database(newvalue)
    # Loop through the alternative and exit when the it is found (from highest to lowest ranked)
    foundalt = False
    highrankmax = highrank
    while highrank > 0:
        alt_name = data_alt[str(highrank)]
        with DatabaseMapping(sql_url) as db_map:
            param_val = db_map.get_parameter_value_item(entity_class_name=ECN, entity_byname=(ECN,), parameter_definition_name=var, alternative_name=alt_name)
            if not param_val:
                print(f"The variable {var} does not exists in the alternative {alt_name}")
                highrank -= 1
                if highrank == 0:
                    # This means this is the last loop and the variable does not exist in any alternative. Create the variable in the last alternative and 
                    # Commit the database
                    alt_name = data_alt[str(highrankmax)]
                    print(f"The variable {var} does not exists in any alternative. Allocating it to alternative {alt_name}")
                    
                    # Add the parameter definition as it does not seem to exist
                    try:
                        db_map.add_parameter_definition(
                            entity_class_name=ECN,
                            name = var
                        )
                    except:
                        print(f"there's already a parameter_definition with 'entity_class_name': {ECN}, 'name': {var}")   
                    # Add a value to this parameter. This will not work if the coupling alternative is not present in the list of alternatives
                    db_map.add_parameter_value(
                        entity_class_name=ECN,
                        entity_byname=(ECN,),
                        parameter_definition_name=var,
                        alternative_name=alt_name,
                        value=value,
                        type=value_type
                        )
                    try:
                        db_map.commit_session(f"Updated variable {var} in a loop in alternative {alt_name}")
                        print("Database committed")
                    except Exception as error:
                        print("nothing to commit:", error)
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

def convert_time(date):
    if isinstance(date, datetime.datetime):
        date = date.date()
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%d/%m/%Y')
        date = date.date()
    return date

def getncfilename(filepath):
    spath = filepath.replace('\\',' ').replace('/',' ').split()
    #filename = spath.pop()
    print(spath)
    spath.pop()
    print(spath)
    realpath = '/'.join(spath)
    
    print(realpath)
    allncfiles = glob.glob(realpath + "/*.nc")
    
    # Get all the nc file as a list
    output_list = []
    for x in allncfiles:
        xpath = x.replace('\\',' ').replace('/',' ').split()
        output_list.append(xpath.pop())

    print(output_list)
    ncfilepath = "./"
    if len(output_list)>1:
        # Get the latest saved files
        ncfilepath=max(allncfiles, key=os.path.getctime) 
    elif len(output_list) == 0:
        print("no nc file in the path indicated. You might need to run CWatM to get them generated.")
    else:
        ncfilepath = realpath + '/' + output_list[0]
    return ncfilepath

if not(os.path.isfile(inifile)):
    msg = "Error 302: Settingsfile not found!\n"
    raise CWATMFileError(inifile,msg)

config = ExtParser()
config.optionxform = str
config.sections()
config.read(inifile)

# Get the Looping time 
RollFlexTool = config['TIME-RELATED_CONSTANTS']["RollFlexTool"]
RollFlexToolnum = int(RollFlexTool.replace('D', ''))
# Get the Stepend value
stepend = config['TIME-RELATED_CONSTANTS']["StepEnd"]
stepend = convert_time(stepend)

# Set the start date when it previously stopped to enhance a warm start and go straight to the spinup time
stepstart = stepend + timedelta(days=1)

spinup = stepstart
spinup = convert_time(spinup)

# Define the new end date based on the rolling horizon
stepend = stepstart + timedelta(days=RollFlexToolnum)

StepFlexTool = config['TIME-RELATED_CONSTANTS']["StepFlexTool"]
StepFlexTool = convert_time(StepFlexTool)

if type(stepstart) != type(StepFlexTool):
    stepstart = convert_time(stepstart)
    StepFlexTool = convert_time(StepFlexTool)

if type(stepend) != type(StepFlexTool):
    stepend = convert_time(stepend)
    StepFlexTool = convert_time(StepFlexTool)

#if stepstart > StepFlexTool:
#    stepend = min(stepend,StepFlexTool)
#if stepend > StepFlexTool:
stepend = min(stepend,StepFlexTool)

# Either set it to 1D (for debugging purposes) or to stepend to get the last day of the simulation
stepinit = "01/01/1932 1d"

if "loopcount" in config['OPTIONS']:
    loopcount = True
    print(f"The variable loopcount was found in the database, its value is {loopcount} of type {type(loopcount)}")
else:
    loopcount = False
    print(f"The variable loopcount was not found in the database, its value is set to {loopcount}  of type {type(loopcount)}")


load_initial = True

# Need to find the initfile where it is saved and find its name
initfolderload = config['INITITIAL CONDITIONS']["initSave"]

# Get the nc file name from the last day that was generated by CWatM
ncfilepath = getncfilename(initfolderload)

# Set the start date when it previously stopped to enhance a warm start and go straight to the spinup time
 

# Combine the output files with the same name by concatenating the files.

# Look for the variables in the database from the winning alternative to the lowest ranked alternative and change the value
highrank = len(data_alt)
allocate_var_to_alt("StepInit", stepinit, highrank, data_alt, url, "INITITIAL CONDITIONS")
allocate_var_to_alt("StepStart", stepstart, highrank, data_alt, url, "TIME-RELATED_CONSTANTS")
allocate_var_to_alt("SpinUp", spinup, highrank, data_alt, url, "TIME-RELATED_CONSTANTS")
allocate_var_to_alt("StepEnd", stepend, highrank, data_alt, url, "TIME-RELATED_CONSTANTS")
allocate_var_to_alt("load_initial", load_initial, highrank, data_alt, url, "INITITIAL CONDITIONS")
allocate_var_to_alt("loopcount", loopcount, highrank, data_alt, url, "OPTIONS")
# Re-allocate the path of the init load based on the init save path
allocate_var_to_alt("initLoad", ncfilepath, highrank, data_alt, url, "INITITIAL CONDITIONS")

print(stepinit)