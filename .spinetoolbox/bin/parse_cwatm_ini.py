
import toml
import datetime
import collections.abc
import spinedb_api as api
from spinedb_api import DatabaseMapping
from spinedb_api import purge
import inspect
import sys


settingsFNTOML = "validTOML_settings_CWatM.ini"
sql_url = sys.argv[1] 
alternative = sys.argv[2]
typefile = sys.argv[3]
with open(settingsFNTOML, 'r') as f:
    config = toml.load(f)
class X(object):
    pass

def remove_all(sql_url):
    with DatabaseMapping(sql_url) as db_map:
        # Remove all the scenario
        scenario = db_map.get_scenario_items()
        keys = [entities["name"] for entities in scenario]
        for key in keys:
            db_map.get_scenario_item(name=key).remove()
        # Remove all the entity
        entity_classes = db_map.get_entity_class_items()
        keys = [entities["name"] for entities in entity_classes]
        for key in keys:
            db_map.get_entity_class_item(name=key).remove()
        # Remove all the alternatives but Base
        alternatives = db_map.get_alternative_items()
        keys = [entities["name"] for entities in alternatives]
        for key in keys:
            if not key == "Base":
                db_map.get_alternative_item(name=key).remove()
        try:
            db_map.commit_session("database reset")
            print("nothing to commit")
        except:
            print("All class item, scenario and alternative were removed")

def check_base_alternative(sql_url, entity_name, param):
    with DatabaseMapping(sql_url) as db_map:
        param_val = db_map.get_parameter_value_item(entity_class_name=entity_name, entity_byname=(entity_name,), parameter_definition_name=param, alternative_name="Base")
    #print(param_val)
    if not param_val:
        value = param_val
    else:
        value = param_val["parsed_value"]
    #if inspect.isclass(value):

    return value
def populate_ini(sql_url, config, alternative):
    with DatabaseMapping(sql_url) as db_map:
    # Allocate to the Spine mapping structure
        #param_val =db_map.get_alternative_items()
        #print(param_val)
        db_map.add_alternative_item(check=True, name=alternative)
        alt = db_map.get_alternative_items()
        for key in config:
            # allocate the entity class items for upper layers
            #print(key)
            db_map.add_entity_class_item(name=key, description="Initial data", active_by_default = True)
            data = config[key]
            # add entities to our zero-dimensional classes
            for key2 in data:
                #print("    " + key2)
                db_map.add_entity_item(entity_class_name=key, name=key, description=key)
                db_map.add_parameter_definition_item(entity_class_name=key, name=key2)
                # Check if it is a boolean
                if isinstance(data[key2], bool) or isinstance(data[key2], str):
                    value, type_ = api.to_database(data[key2])
                # Check if it is a string
                elif isinstance(data[key2], datetime.date):
                    parsed_value = api.DateTime(data[key2].strftime("%Y-%m-%d"))
                    value, type_ = api.to_database(parsed_value)
                elif isinstance(data[key2], collections.abc.Sequence):
                    #print(data[key2])
                    if isinstance(data[key2][0], datetime.date):
                        parsed_value = api.Array([dates.strftime("%Y-%m-%d") for dates in data[key2]])
                    else:
                        parsed_value = api.Array(data[key2])
                    value, type_ = api.to_database(parsed_value)
                elif isinstance(data[key2], float) or isinstance(data[key2], int):
                    value, type_ = api.to_database(data[key2])

                value_in_db = check_base_alternative(sql_url, key, key2)

                #print(value_in_db)
                #print(value)
                if value_in_db == api.from_database(value,type_):
                    print("same value, skipping")
                    continue
                else:
                    print(f"not the same value value_in_db={value_in_db} and value_ini={value}")

                
                if key=="CALIBRATION" and typefile=="calibration":
                    # Test if the alternative exists
                    try:
                        next(item for item in alt if item["name"] == "calibration")
                        alternativename = "calibrationxx"                                               
                    except:
                        # The alternative name does not exist
                        alternativename = "calibration"
                    db_map.add_alternative_item(check=True, name=alternativename)
                elif key=="OUTPUT" and typefile=="initfile":
                    # Test if the alternative exists
                    try:
                        next(item for item in alt if item["name"] == "output_" + alternative)
                        alternativename = "output_" + alternative + "xx"                                            
                    except:
                        # The alternative name does not exist
                        alternativename = "output_" + alternative
                    db_map.add_alternative_item(check=True, name=alternativename)
                else:
                    alternativename = alternative


                db_map.add_parameter_value(
                    entity_class_name=key,
                    entity_byname=(key,),
                    parameter_definition_name=key2,
                    alternative_name=alternativename,
                    value=value,
                    type=type_
                    )
        #param_val =db_map.get_parameter_value_items()
        #print(param_val)
        try:
            db_map.commit_session("initalized CWatM database")
            print("Database committed")
        except:
            print("nothing to commit")


with DatabaseMapping(sql_url) as db_map:
    scenario = db_map.get_scenario_items()
    entity_classes = db_map.get_entity_class_items()
    #print(scenario)
    #print(entity_classes)
    if len(sys.argv) == 5:
        update = sys.argv[4].lower() in ['true', '1']
    else:
        if not entity_classes and not scenario:
            update = True
        else:
            update = False
if not update:
	print("No updates has been performed, re-using existing database")
else:
    #remove_all(sql_url)
    print("Importing the database as new")
    populate_ini(sql_url, config, alternative)
