from spinedb_api import DatabaseMapping
import sys 
import spinedb_api as api

url = sys.argv[1]

with DatabaseMapping(url) as db_map:
    param_value = db_map.get_parameter_value_items(entity_class_name='TIME-RELATED_CONSTANTS', entity_byname=('TIME-RELATED_CONSTANTS',), parameter_definition_name='StepFlexTool')
    maxdate = api.from_database(param_value[0].get("value"), param_value[0].get("type"))

    param_value = db_map.get_parameter_value_items(entity_class_name='TIME-RELATED_CONSTANTS', entity_byname=('TIME-RELATED_CONSTANTS',), parameter_definition_name='StepEnd')
    enddate = api.from_database(param_value[0].get("value"), param_value[0].get("type"))

if enddate > maxdate:
    exit(1)