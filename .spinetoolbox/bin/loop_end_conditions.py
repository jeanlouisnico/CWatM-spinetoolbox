from spinedb_api import DatabaseMapping
import sys 
import spinedb_api as api

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
    param_value = db_map.get_parameter_value_item(entity_class_name='TIME-RELATED_CONSTANTS', entity_byname=('TIME-RELATED_CONSTANTS',), parameter_definition_name='StepFlexTool', alternative_name='coupling')
    maxdate = api.from_database(param_value["value"], param_value["type"])

    param_value = db_map.get_parameter_value_item(entity_class_name='TIME-RELATED_CONSTANTS', entity_byname=('TIME-RELATED_CONSTANTS',), parameter_definition_name='StepEnd', alternative_name=var['StepEnd'][1])
    enddate = api.from_database(param_value["value"], param_value["type"])

if enddate > maxdate:
    exit(1) 