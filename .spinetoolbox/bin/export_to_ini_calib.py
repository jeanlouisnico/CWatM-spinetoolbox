import sys
import spinedb_api as api
from spinedb_api import DatabaseMapping
from spinedb_api.filters import tools as filter_tools
from tomlkit import *

from pathlib import Path
import os
import re
import fileinput
import json

url = sys.argv[1]
outfile = sys.argv[2]
calib = sys.argv[3]
#url = "sqlite:///C:/Git/CWatM-spinetoolbox-dev/.spinetoolbox/items/data_store/cwatmdb_new.sqlite"
#outfile = "calib_ini"
def use_regex_date(filein):

	with open (filein, 'r' ) as f:
		content = f.read()
		content_new = re.sub('(\d{4})\-(\d{2})\-(\d{2}|[a-yA-Y]{3})', r'\3/\2/\1', content, flags = re.M)
	with open (filein, 'w' ) as f:
		f.write(content_new) 

	return
def replacetext(file, search_text, replace_text): 
  
    # Opening the file using the Path function 
    file = Path(r"{}".format(file))
  
    # Reading and storing the content of the file in 
    # a data variable 
    data = file.read_text() 
  
    # Replacing the text using the replace function 
    data = data.replace(search_text, replace_text) 
  
    # Writing the replaced data 
    # in the text file 
    file.write_text(data) 
  
    # Return "Text replaced" string 
    return

def replace_path(strin, dic, maincat):
	# identify if this is a path string
	str_mod = strin
	# Modify the root folder if it exist
	if "$" in strin:
		if ":" in strin:
			# This means this is a relative path, then look for the source and the variable in the source
			source = strin[(strin.find("(") + 1):strin.find(":")]
			var = strin[(strin.find(":") + 1):strin.find(")")]
			strori = dic[source][var]
			str_mod = str_mod.replace("$(" + source + ":" + var + ")", "{}")
			str_mod = str_mod.format(strori)
		else:
			source = strin[(strin.find("(") + 1):strin.find(")")]
			strori = dic[maincat][source]
			str_mod = str_mod.replace("$(" + source + ")", "{}")
			str_mod = str_mod.format(strori)
			# This means that it refers to another location in the structure data, extract the data from there	
	else:
		try:
			if isinstance(int(strin[0:4]),int):
				# If the first 4 digit are float then this is a date stored in string format. Reshape it to the CWatM format
				if strin.count(" ") > 0:
					strinsplit = strin.split(" ")
					for date in strinsplit:
						datesplit = date.split("-")
						str_mod_temp = [date.replace("-", "/") for date in strinsplit]
						str_mod = ""
						for idate in str_mod_temp:
							datesplit = idate.split("/")
							str_mod = str_mod + " {}/{}".format(datesplit[2], datesplit[1], datesplit[0])
				else:
					datesplit = strin.split("-")
					str_mod = "{}/{}/{}".format(datesplit[2], datesplit[1], datesplit[0])
		except:
			pass

	return str_mod

def retrieve_db(url, outfile, calib):
	doc = document()
	doc.add(comment("This is a TOML document is automatically generated by SpineToolbox"))
	with DatabaseMapping(url) as db_map:
		# Do something with db_map
		entity_classes = db_map.get_entity_class_items()
		keys = [entities["name"] for entities in entity_classes]
		print("This is the list of keys to be exported: ", keys)
		my_dictionary = dict.fromkeys(keys)
		param_val = db_map.get_parameter_value_items()
		#print(keys)
		#print("param_val ")
		# print(param_val)
		tomldoc = dict.fromkeys(keys)
		for key in keys:
			tomldoc[key] = table()

		for values in param_val:
			#print(values["value"])
			if values["type"] == 'array':
				data_spdb = api.from_database(values["value"], values["type"])
				datatemp = data_spdb._values
				try:
					# Check if the array contains float or integer values
					parse_as_digit = False
					if isinstance(datatemp[0],int) or isinstance(datatemp[0],float):
						parse_as_digit = True
					# Check if the digit is stored as string e.g. dates are stored as string
					elif datatemp[0].find("-") > 0:
						if isinstance(int(datatemp[0][0:4]), int):
							# Then this is a dates
							parse_as_digit = True
						else:
							# Then it might be a string with dash inside
							parse_as_digit = False
					if parse_as_digit:
						data = ' '.join([str(elem) for elem in datatemp])
					else:
						data = ', '.join([str(elem) for elem in datatemp])
				except:
					data = ', '.join([str(elem) for elem in datatemp])
				
			elif values["type"] == 'date_time':
				data_spdb = api.from_database(values["value"], values["type"])
				data = data_spdb.value.strftime("%Y-%m-%d")
			elif values["type"] == 'duration':
				data_spdb = api.from_database(values["value"], values["type"])
				data = str(data_spdb)
				print(type(data))
			else:
				data  = api.from_database(values["value"], values["type"])

			# This section is only used for the calibration run, where we discard the outputs
			if calib.lower() in ['false', '0'] and values['entity_name']=="CALIBRATION" and values['parameter_definition_name'] in ['OUT_Dir', 'OUT_TSS_Daily', 'OUT_TSS_MonthAvg']:
				continue
			
			dic = {values['parameter_definition_name']: data}
			'''
			print("Adding entity_name: ", values['entity_name'])
			print("     parameter_definition_name: ", values['parameter_definition_name'])
			print("     data: ", data)
			'''
			if not my_dictionary[values['entity_name']]:
				my_dictionary[values['entity_name']] = dic
				tomldoc[values['entity_name']].add(values['parameter_definition_name'], data)
			else:
				my_dictionary[values['entity_name']].update(dic)
				tomldoc[values['entity_name']][values['parameter_definition_name']]=data
		
		# This section is meant for the coupling loops where we replace the name of the init file to the appropriate file
		if not my_dictionary["INITITIAL CONDITIONS"] == None:
			param_val = db_map.get_parameter_value_items(entity_class_name="INITITIAL CONDITIONS", entity_byname=("INITITIAL CONDITIONS",), parameter_definition_name="load_initial")
			data_init_load  = api.from_database(param_val[0]["value"], param_val[0]["type"])
			param_val = db_map.get_parameter_value_items(entity_class_name="INITITIAL CONDITIONS", entity_byname=("INITITIAL CONDITIONS",), parameter_definition_name="save_initial")
			data_init_save  = api.from_database(param_val[0]["value"], param_val[0]["type"])
			if data_init_load == True or data_init_save == True:
				# Look for the Spinup date and the file name from the initSave variable to build the filename to be loaded
				param_val_bis = db_map.get_parameter_value_items(entity_class_name="TIME-RELATED_CONSTANTS", entity_byname=("TIME-RELATED_CONSTANTS",), parameter_definition_name="SpinUp")
				timesaved = api.from_database(param_val_bis[0]["value"], param_val_bis[0]["type"])

				param_val_initsave = db_map.get_parameter_value_items(entity_class_name="INITITIAL CONDITIONS", entity_byname=("INITITIAL CONDITIONS",), parameter_definition_name="initLoad")
				initpath = api.from_database(param_val_initsave[0]["value"], param_val_initsave[0]["type"])
				# Get the file name and change the name of the init file based on the spinup values. This will not change the path, just the file name to be saved
				if "/" in initpath:
					splitstr = initpath.split("/")
					initfile = splitstr[-1]
				elif "\\" in initpath:
					splitstr = initpath.split("\\")
					initfile = splitstr[-1]
				else:
					initfile = initpath
					print(timesaved.value)
				data = initfile + timesaved.value.strftime("%Y%m%d") + ".nc"

				tomldoc["INITITIAL CONDITIONS"]["initLoad"] = data

			# Change the StepInit to the value of StepEnd in case the initSave value is true

		# Create output folders for each scenario and avoid writing errors in files
		#print(my_dictionary)
		if not my_dictionary["FILE_PATHS"] == None:
			print("Creating the directory")
			outputfolder = my_dictionary["FILE_PATHS"]["PathOut"]
			initfoldersave = my_dictionary["INITITIAL CONDITIONS"]["initSave"]
			initfolderload = my_dictionary["INITITIAL CONDITIONS"]["initLoad"]
			# If the paths are relative, re-write them. !!!! Path should be relative to work in Toolbox !!!!
			current_directory = os.getcwd()
			final_directory = os.path.join(current_directory, Path(r"{}".format(outputfolder)))
			final_directory_init = os.path.join(current_directory, Path(r"{}".format(initfoldersave)))
			final_directory_init_save = os.path.join(current_directory, Path(r"{}".format(initfolderload)))
			if not os.path.exists(final_directory):
				os.makedirs(final_directory)
			if not os.path.exists(final_directory_init):
				os.makedirs(final_directory_init)
			if not os.path.exists(final_directory_init_save):
				os.makedirs(final_directory_init_save)
            # Re-write the path to the dictionnary to be used in the ini file
			tomldoc["FILE_PATHS"]["PathOut"]=final_directory
			my_dictionary["FILE_PATHS"]["PathOut"] = final_directory
			tomldoc["INITITIAL CONDITIONS"]["initSave"]=final_directory_init
			my_dictionary["INITITIAL CONDITIONS"]["initSave"] = final_directory_init 
			tomldoc["INITITIAL CONDITIONS"]["initLoad"]=final_directory_init_save
			my_dictionary["INITITIAL CONDITIONS"]["initLoad"] = final_directory_init_save 
		else:
			try:
				del my_dictionary['FILE_PATHS']
			except:
				print("Variable FILE_PATHS is not defined")

			try:
				print()	
				doc.pop("FILE_PATHS")
			except:
				print("Variable FILE_PATHS is not defined")
		
		# Store the tomldoc values in the toml document
		for key in tomldoc:
			doc.add(key, tomldoc[key])
		
		#my_dictionary.pop("OUTPUT", None)
		#doc.pop("OUTPUT")
		# Check for empty key
		emptykey = list() 
		addemptyoutput = False
		doccheck = doc.copy()
		for key in doccheck:
			#print(key, ": ", doccheck[key])
			if not doccheck[key] and calib.lower() in ['true', '1'] and key=="OUTPUT":
				# If the OUTPUT key exist but is not assign
				print("adding output section")
				doc.pop(key)
				addemptyoutput = True
				# print(key)
				emptykey.append(key)
			elif not doccheck[key]:
				doc.pop(key)

		#print(doc)
		#print(emptykey)
		'''
		This is checking the valid strings, dates and output in order to
		remove symbols and create an invalid toml file. This is because CWatM
		uses an invalid format of toml as .ini file 
		'''
		# dicti = my_dictionary.copy()
		# #print(my_dictionary)
		# for values in dicti:
		# 	# Replace PathRoot, PathOut, PathMeteo in subsequent strings
		# 	if not dicti[values] == None:
		# 		for var in dicti[values]:
		# 			if isinstance(dicti[values][var], str):
		# 				newstr = replace_path(dicti[values][var], dicti, values)
		# 				dicti[values][var] = newstr
		# 	else:
		# 		del my_dictionary[values]
		if addemptyoutput:
			# Convert the dictionnary into a tomlkit valid document
			for emkey in emptykey:
				output = table()
				output.add(comment("This is an empty output file"))
				doc.add(emkey, output)
		print("Writing the toml object into the ini file")
		with Path(outfile+".ini").open("w") as fout:
				#print(tomlkit.dumps(my_dictionary))
			fout.write(dumps(doc))
		
		# Modify the ini file to be in a corrupt version of the CWatM
		# Character to be deleted
		replacetext(outfile+".ini", '"', "")	
		replacetext(outfile+".ini", "\\\\", "\\")
		use_regex_date(outfile+".ini")

# Write to a cwatm compatible ini file
retrieve_db(url, outfile, calib) 

# Get the alternative for each scenario where it writes the scenario and the winning alternative in a separate file

""" with DatabaseMapping(url) as db_map:
	filter_configs = db_map.get_filter_configs()
	for config in filter_configs:
		scenario_name = filter_tools.name_from_dict(config)
		if scenario_name is not None:
			break
		else:
			raise RuntimeError("no scenario filter in database mapping")
		
	scenario_alternatives = db_map.get_scenario_alternative_items(scenario_name=scenario_name)
	scenario_item = db_map.get_scenario_item(name=scenario_name)
	print(f"alt: {scenario_item['alternative_name_list']}")
	setofalt = dict()
	#for i in scenario_item['alternative_name_list']:
	#	setofalt[i] = None
	for item in scenario_alternatives: 
		#print(f"alt: {item['alternative_name']} rank: {item['rank']} (highest rank wins)")
		print(f"ordered alternatives {scenario_item['alternative_name_list']} (last alt wins)")
		setofalt[item['rank']] = item['alternative_name']
	
	with open('alt_list.json', 'w') as json_file:     
		json.dump(setofalt, json_file) """