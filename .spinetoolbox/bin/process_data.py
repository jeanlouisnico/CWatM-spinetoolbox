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


print("nothing to pass")
print("continue with the next day in CWatM")

'''Debugging'''
#filepath = "C:/Git/CWatM-spinetoolbox-dev/.spinetoolbox/items/cwatm/output/coupling_6a8468e9a6358dcd504b5174a21e940989e0e61e/2024-07-18T09.50.32/output"
#f_in = filepath

'''in file'''
f_in = "./init"

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