import sys
import spinedb_api as api
from spinedb_api import DatabaseMapping
import tomlkit
from pathlib import Path
import os

url = sys.argv[1]
#url = "sqlite:///C:/Git/CWatM-spinetoolbox-dev/.spinetoolbox/Data/cwatm_db.sqlite"

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
							str_mod = str_mod + " {}/{}/{}".format(datesplit[2], datesplit[1], datesplit[0])
				else:
					datesplit = strin.split("-")
					str_mod = "{}/{}/{}".format(datesplit[2], datesplit[1], datesplit[0])
		except:
			pass

	return str_mod

def retrieve_db(url):
	with DatabaseMapping(url) as db_map:
		# Do something with db_map
		entity_classes = db_map.get_entity_class_items()
		keys = [entities["name"] for entities in entity_classes]
		my_dictionary = dict.fromkeys(keys)
		param_val = db_map.get_parameter_value_items()
		#print("param_val ")
		#print(param_val)
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
			else:
				data  = api.from_database(values["value"], values["type"])
			dic = {values['parameter_definition_name']: data}
			if not my_dictionary[values['entity_name']]:
				my_dictionary[values['entity_name']] = dic
			else:
				my_dictionary[values['entity_name']].update(dic)
		
		# Create output folders for each scenario and avoid writing errors in files
		outputfolder = my_dictionary["FILE_PATHS"]["PathOut"]
		current_directory = os.getcwd()
		final_directory = os.path.join(current_directory, Path(r"{}".format(outputfolder)))
		if not os.path.exists(final_directory):
			os.makedirs(final_directory)
		# Re-write the path to the dictionnary to be used in the ini file
		my_dictionary["FILE_PATHS"]["PathOut"] = final_directory
		
		'''
		This is checking the valid strings, dates and output in order to
		remove symbols and create an invalid toml file. This is because CWatM
		uses an invalid format of toml as .ini file 
		'''
		dicti = my_dictionary.copy()
		#print(my_dictionary)
		for values in dicti:
			# Replace PathRoot, PathOut, PathMeteo in subsequent strings
			for var in dicti[values]:
				if isinstance(dicti[values][var], str):
					newstr = replace_path(dicti[values][var], dicti, values)
					dicti[values][var] = newstr


		with Path("cwatm_input.ini").open("w") as fout:
			#print(tomlkit.dumps(my_dictionary))
			fout.write(tomlkit.dumps(my_dictionary))

		# Modify the ini file to be in a corrupt version of the CWatM
		# Character to be deleted
		replacetext("cwatm_input.ini", '"', "")	
		#replacetext("cwatm_input.ini", '= [', "= ")	
		#replacetext("cwatm_input.ini", ']', "")	

retrieve_db(url) 