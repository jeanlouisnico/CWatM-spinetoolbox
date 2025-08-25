# -----------------------------------------------------------------------------------------
# Name:        process_data
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

from os import listdir
from os.path import isfile, join
import netCDF4
import numpy as np
import sys
import xarray
import configparser
from pathlib import Path
from pathlib import PureWindowsPath  
import shutil
from CWatM_Module.management_modules.messages import *
from CWatM_Module.management_modules.globals import *
import difflib  # to check the closest word in settingsfile, if an error occurs
#from chart_studio.plotly import plot, iplot
#from plotly.graph_objs import *
#from scipy.io import netcdf  
#from mpl_toolkits.basemap import Basemap

'''Debugging'''
#filepath = "C:/Users/JLJEAN/.spinetoolbox/work/export_to_ini_calib__9e5c7cb9f5574551a972f8870446f7f4__toolbox/output"
# export_to_ini_calib__1295f83d2f4546cbba34c611141cd901__toolbox
#f_in = filepath
#inifile = "C:/Users/JLJEAN/.spinetoolbox/work/cwatm__17cd71001a9444f382fc61e52230e3d2__toolbox/cwatm_input.ini"
'''in file'''
f_in = "./init"
inifile = sys.argv[1]

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

def get_nc_files():

    ''' Get all the input files '''
    # All *.nc files need to be listed
    all_nc_files = [f for f in listdir(f_in) if isfile(join(f_in, f))]

    '''Save all the nc file in the output folder to be re-imported into the CWatM folder'''

    '''
    # save all files in the output folders NetCDF3
    for f in onlyfiles:
        file2read = netcdf.NetCDFFile("./init/" + f,'r')
        print(file2read.variables.keys())
        #temp = file2read.variables # var can be 'Theta', 'S', 'V', 'U' etc..
    '''
    # for NetCDF4
    for f in all_nc_files:
        file_content = netCDF4.Dataset(f_in + "/" + f)
        print("-------------" + f + "--------------") 
        # Get all the metadata/attributes to be written in the output file
        with netCDF4.Dataset(f,mode='w',format='NETCDF4_CLASSIC') as ncfile:
            for name in file_content.ncattrs():
                # Print("Global attr {} = {}".format(name, getattr(file_content, name)))
                setattr(ncfile, name, getattr(file_content, name))        
                
            # Create dimensions for the .nc file
            for f_dim in file_content.dimensions:
                dim_name = f_dim
                lat_dim = ncfile.createDimension(f_dim, file_content.dimensions[f_dim].size) # latitude axis
                # Get all the variables from each file
            for varname in file_content.variables.keys():
                temp = file_content.variables[varname]
                datatype = temp.datatype
                if datatype.name == "float32":
                    dt_in = np.float32
                elif datatype.name == "float64":
                    dt_in = np.float64
                else:
                    print("Not yet defined: " + datatype.name)
                add_extra = False
                if "_FillValue" in temp.ncattrs() or "_ChunkSizes" in temp.ncattrs():
                    add_extra = True
                var_in = ncfile.createVariable(varname, dt_in, temp.dimensions)
                for var_att in temp.ncattrs():
                    if var_att != "_FillValue" and var_att != "_ChunkSizes":
                        setattr(var_in, var_att, getattr(temp, var_att))

                # Add values to the variable
                if len(temp.dimensions) == 1:
                    var_in[:] = temp[:]
                elif len(temp.dimensions) == 2:
                    var_in[:,:] = temp[:,:]
                elif len(temp.dimensions) == 3:
                    var_in[:,:,:] = temp[:,:,:]
                elif len(temp.dimensions) == 4:
                    var_in[:,:,:,:] = temp[:,:,:,:]
                else:
                    print("missing data dimensions to be added. add more dimensions in the script")
                    
                # Read the data from within the 

def combine_outputs(ini):
    # Read the ini file
    config = ExtParser()
    config.optionxform = str
    config.sections()
    config.read(ini)
    print(config)
    # Select a fixed output path to store the final outputs
    outpath = os.path.join(config['FILE_PATHS']["PathCombinednc"], '')
    # Get the current output to merge with from PathOut
    currentoutput = os.path.join(config['FILE_PATHS']["PathOut"], '')
    # Get a list of each output
    all_nc_files = list(Path(currentoutput).rglob("*.nc"))
    # Get the loop count variable to see if this is the first loop or not
    loopcount = config['OPTIONS']["loopcount"]    
    if loopcount=="false":
            # Copy all the nc files to the final output locations
            print(f"Moving output file to: {outpath}")
            for f in all_nc_files:
                print(f)
                shutil.move(PureWindowsPath(f), outpath)
            return
    # Get the initload path
    #initpath  = config['INITITIAL CONDITIONS']["initLoad"]
    #spath = initpath.replace('\\',' ').replace('/',' ').split()
    #sprevious = spath[:-2]
    #previousoutput = '/'.join(sprevious) + "/output"  
    
    for file in all_nc_files:
        daily = False
        time = True
        var = file.name[:-3]
        if file.name[:-3].split('_')[-1] == 'daily':
            var = var[:-6]
            daily = True

        file_names = file.name
        listfiles = [outpath + "/" + file_names,currentoutput + "/" + file_names]
        if daily:  
            with xarray.open_mfdataset(listfiles,combine = 'nested', concat_dim="time") as combined:
                file_path = Path(f"{outpath}{file_names}")
                # Write the file to a different name to prevent xarray errors
                if file_path.exists():
                    combined.to_netcdf(f"{outpath}bis{file_names}", mode='a')
                else:
                    combined.to_netcdf(f"{outpath}bis{file_names}")
                
                        # Rename the file to its original name after it has been saved
            old_file = f"{outpath}bis{file_names}"
            new_file = f"{outpath}{file_names}"
            original_file = f"{currentoutput}/{file_names}"
            print("Cleaning the place...")
            print(f"    Removing old files: {outpath}{file_names}")
            os.remove(new_file)
            print(f"    Removing original files: {currentoutput}/{file_names}")
            os.remove(original_file)
            print(f"    Renaming output file")
            os.rename(old_file, new_file)
        else:
            # This means the file does not have a time dimension and can simply be replaced by the current output
            if os.path.isfile(outpath + "/" + file_names):
                os.remove(outpath+'/'+ file_names)
                print(file_names, 'has been removed from: ', outpath)   
            shutil.move(os.path.join(currentoutput, file_names), os.path.join(outpath, file_names))
            print("New file has been moved to:", outpath)

debugging = False
if debugging:
    print("nothing to pass")
    print("continue with the next day in CWatM")
else:
    combine_outputs(inifile)
    # For coupling purposes, we can alter the init file that are generated by CWatM. These init file has multiple variables that can be read from the river basin
    # The output files are not re-used by CWatM, so they are as they are.
    #get_nc_files()