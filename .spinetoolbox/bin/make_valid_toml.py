from CWatM_Module.management_modules.globals import *

import configparser
from CWatM_Module.management_modules.messages import *
import tomlkit
import os
import difflib  # to check the closest word in settingsfile, if an error occurs
from pathlib import Path
from datetime import datetime
import sys

settingsFileName = sys.argv[1]
#settingsFileName = "C:/Users/JLJEAN/tunexus/CWatM/Tutorials/09_Calibration/settings_fast_2.txt"
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
        '''
        re_newintp1 = r'\$\((\w*):(\w*)\)'  # other section
        re_newintp2 = r'\$\((\w*)\)'  # same section

        re_old1 = re.findall('\$\(\w*:\w*\)', r_opt)
        re_old2 = re.findall('\$\(\w*\)', r_opt)

        m_new1 = re.findall(re_newintp1, r_opt)
        m_new2 = re.findall(re_newintp2, r_opt)
        
        if m_new1:
             i = 0
             for f_section, f_option in m_new1:
                 self.cur_depth = self.cur_depth + 1
                 if self.cur_depth < configparser.MAX_INTERPOLATION_DEPTH:
                     sub = self.get(f_section,f_option, vars=vars)
                     ret = ret.replace(re_old1[i], sub)
                     i += 1
                 else:
                     raise configparser.InterpolationDepthError(option, section, r_opt)

        if m_new2:
             i = 0
             for l_option in m_new2:
                 self.cur_depth = self.cur_depth + 1
                 if self.cur_depth < configparser.MAX_INTERPOLATION_DEPTH:
                     sub = self.get(section, l_option, vars=vars)
                     ret = ret.replace(re_old2[i], sub)
                     i += 1
                 else:
                     raise configparser.InterpolationDepthError(option, section, r_opt)
        '''
        self.cur_depth = self.cur_depth - 1
        return ret
        
def parse_configuration(settingsFileName):
    """
    Parse settings file

    :param settingsFileName: name of the settings file
    :return: parameters in list: binding, options in list: option
    """
    def add_to_dic(my_dictionary, sec, dic):
        print("This is the dic: ", dic)
        print("This is the sec: ", sec)
        for k, v in dic.items():
            var = k
            data = v
        print("This is the var: ", var)
        print("This is the data: ", data)
        if not my_dictionary[sec]:
            my_dictionary[sec] = dic
            tomldoc[sec].add(var, data)
        else:
            my_dictionary[sec].update(dic)
            tomldoc[sec][var] = data
        return my_dictionary, tomldoc

    def splitout(varin, check):
        """
        split variable in several one, seperator = ,

        :param varin:
        :param check:
        :return: list with several variables
        """

        out = list(map(str.strip, varin.split(',')))
        if out[0] == "": out[0]="None"
        if out[0] != "None": check = True
        return out, check
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
    def extractdata(var, sec, opt, check_section=None):
        try:
            int(var[0])
            # The first instance is a number. It can be either a date or set of coordinates
            split = False
            if var.find(" ") > 0:
                '''this means that there are multiple input and should be stored as an array'''
                split = True
            if var.find("/") > 0:
                '''this means that this is a date format'''
                if split:
                    var = var.split(" ")
                    var = [datetime.strptime(i, '%d/%m/%Y') for i in var]
                else:
                    var = datetime.strptime(var, '%d/%m/%Y')
            else:
                '''This means this is a float'''
                if split:
                    var = var.split(" ")
                    var = [eval(i) for i in var]
                else:
                    if var.find(".") > 0:
                        var = config.getfloat(sec, opt)
                    else:
                        var = config.getint(sec, opt)
        except:
                    # binding: all the parameters which are not output or option are collected
            try:
                var = config.getboolean(sec, opt)
            except:
                try:
                    var = config.getint(sec, opt)
                except:
                    try: 
                        var = config.getfloat(sec, opt)
                    except:
                        '''Look for a single string or a list of strings'''
                        var = config.get(sec, opt)
                        if var.find(" ") > 0 and opt!="title":
                            '''this means that there are multiple input and should be stored as an array'''
                            var,check_section = splitout(config.get(sec, opt),check_section) 
        return var
     
    if not(os.path.isfile(settingsFileName)):
        msg = "Error 302: Settingsfile not found!\n"
        raise CWATMFileError(settingsFileName,msg)
    config = ExtParser()
    config.optionxform = str
    config.sections()
    config.read(settingsFileName)
    keys = config.sections()
    my_dictionary = dict.fromkeys(keys)

    doc = tomlkit.document()
    doc.add(tomlkit.comment("This is a TOML document is automatically generated by SpineToolbox"))

    tomldoc = dict.fromkeys(keys)
    for key in keys:
        tomldoc[key] = tomlkit.table()

    ''' Check if there is a defulat section in the init file. If there is a Defaults section
    then list all the keys and exclude them from the other options list as they will appear by default
    in all the options as an entry. If there is no default section, then disregard this step'''
    if "DEFAULT" in list(config.keys()):
        print(config.defaults())
        if bool(config.defaults()):
            # Create a default section in the dictionnary
            my_dictionary['DEFAULT'] = None
            tomldoc['DEFAULT'] = tomlkit.table()
            defaultsec = True
            for opt in config.defaults():
                dic_temp = dict()
                var = config['DEFAULT'][opt]
                parsedvar = extractdata(var, 'DEFAULT', opt)
                dic_temp[opt] = parsedvar
                my_dictionary, tomldoc = add_to_dic(my_dictionary, 'DEFAULT', dic_temp)
        else:
            defaultsec = False
    else:
        defaultsec = False

    for sec in config.sections():
        #print sec
        options = config.options(sec)
        check_section = False
        for opt in options:
            if defaultsec and opt in list(config.defaults().keys()):
                continue
            
            dic_temp = dict()
            # Testing out what sort of input has the variable
            var = config.get(sec, opt)
            parsedvar = extractdata(var, sec, opt, check_section)
 
            dic_temp[opt] = parsedvar
            my_dictionary, tomldoc = add_to_dic(my_dictionary, sec, dic_temp)

        if check_section:
            outsection.append(sec)
    
    # Store the tomldoc values in the toml document
    for key in tomldoc:
        doc.add(key, tomldoc[key])

    emptykey = list() 
    for key in my_dictionary:
        """ if my_dictionary[key] == None and calib=="true" and key=="OUTPUT":
            # If the OUTPUT key exist but is not assign
            print("adding output section")
            doc.pop(key)
            addemptyoutput = True
            print(key)
            emptykey.append(key) """
        if my_dictionary[key] == None:
            print("adding output section: " + key)
            addemptyoutput = True
            emptykey.append(key)
            doc.pop(key)
        else: 
            addemptyoutput = False
    if addemptyoutput:
            # Convert the dictionnary into a tomlkit valid document
        for emkey in emptykey:
            output = tomlkit.table()
            output.add(tomlkit.comment("This is an empty section variable"))
            doc.add(emkey, output)

    with Path("validTOML_settings_CWatM.ini").open("w") as fout:
        print("ini file successfully imported as valid toml file")
        print(my_dictionary)
        #fout.write(tomlkit.dumps(my_dictionary))
        fout.write(tomlkit.dumps(doc))


parse_configuration(settingsFileName)
    