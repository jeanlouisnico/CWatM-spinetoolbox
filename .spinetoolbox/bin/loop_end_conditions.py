from spinedb_api import DatabaseMapping
import sys 
import spinedb_api as api
from datetime import timedelta
from datetime import datetime

file_path = sys.argv[1]
var = {}
with open(file_path, 'r') as file:
    for line in file:
        str_test = line.strip()
        if str_test.find(";")>0:
            print(line.strip())
            variables = str_test.split(";")
            var[variables[0]] = variables[1]
        else:
            url = str_test
            print(url)

with DatabaseMapping(url) as db_map:
    param_value = db_map.get_parameter_value_item(entity_class_name='TIME-RELATED_CONSTANTS', entity_byname=('TIME-RELATED_CONSTANTS',), parameter_definition_name='StepFlexTool', alternative_name=var['StepEnd'])
    maxdate = api.from_database(param_value["value"], param_value["type"])
    print(maxdate)

    param_value = db_map.get_parameter_value_item(entity_class_name='TIME-RELATED_CONSTANTS', entity_byname=('TIME-RELATED_CONSTANTS',), parameter_definition_name='StepStart', alternative_name=var['StepEnd'])
    startdate = api.from_database(param_value["value"], param_value["type"])
    print(startdate)

date2compare = startdate.value + timedelta(days=1)

if startdate.value > maxdate.value:
    exit(1) 
    print("exiting loop")
else:
    print("continue loop to the next step")
