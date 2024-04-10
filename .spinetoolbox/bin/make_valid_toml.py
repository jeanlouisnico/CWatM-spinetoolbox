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
#settingsFileName = "C:/Git/CWatM-spinetoolbox-dev/.spinetoolbox/Data/settings_CWatM_template_30min.ini"
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
        if not my_dictionary[sec]:
            my_dictionary[sec] = dic
        else:
            my_dictionary[sec].update(dic)
        return my_dictionary

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
    if not(os.path.isfile(settingsFileName)):
        msg = "Error 302: Settingsfile not found!\n"
        raise CWATMFileError(settingsFileName,msg)
    config = ExtParser()
    config.optionxform = str
    config.sections()
    config.read(settingsFileName)
    my_dictionary = dict.fromkeys(config.sections())
    for sec in config.sections():
        #print sec
        options = config.options(sec)
        check_section = False
        for opt in options:
            if sec=="OPTIONS":
                try:
                    option[opt] = config.getboolean(sec, opt)
                except:
                    option[opt] = config.getint(sec, opt)
                my_dictionary = add_to_dic(my_dictionary, sec, option)
            else:
                dic_temp = dict()
                '''
                # Check if config line = output line
                if opt.lower()[0:4] == "out_":
                    index = sec.lower()+"_"+opt.lower()

                    if opt.lower()[-4:] =="_dir":
                        outDir[sec] = config.get(sec, opt)
                        my_dictionary = add_to_dic(my_dictionary, sec, outDir)
                    else:
                        # split into timeseries and maps
                        if opt.lower()[4:8] == "tss_":
                            outTss[index],check_section = splitout(config.get(sec, opt),check_section)                            
                            my_dictionary = add_to_dic(my_dictionary, sec, outTss)
                        else:
                            outMap[index],check_section = splitout(config.get(sec, opt),check_section)
                            my_dictionary = add_to_dic(my_dictionary, sec, outMap)
                    
                else:
                '''
                    # Testing out what sort of input has the variable
                var = config.get(sec, opt)
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

                dic_temp[opt] = var
                my_dictionary = add_to_dic(my_dictionary, sec, dic_temp)

        if check_section:
            outsection.append(sec)
    with Path("validTOML_settings_CWatM.ini").open("w") as fout:
        print("ini file successfully imported as valid toml file")
        fout.write(tomlkit.dumps(my_dictionary))


parse_configuration(settingsFileName)
    