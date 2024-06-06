
import toml
import datetime
import collections.abc
import spinedb_api as api
from spinedb_api import DatabaseMapping
from spinedb_api import purge
import sys


settingsFNTOML = "validTOML_settings_CWatM.ini"
alternative = sys.argv[2] 
with open(settingsFNTOML, 'r') as f:
    config = toml.load(f)
 
def remove_all(sql_url):
    with DatabaseMapping(sql_url) as db_map:
        # Remove all the scenario
        scenario = db_map.get_scenario_items()
        keys = [entities["name"] for entities in scenario]
        for key in keys:
            db_map.get_scenario_item(name=key).remove()
        # Remove all the identity
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

def populate_ini(sql_url, config, alternative):
    with DatabaseMapping(sql_url) as db_map:
    # Allocate to the Spine mapping structure
        #param_val =db_map.get_alternative_items()
        #print(param_val)
        db_map.add_alternative_item(check=True, name=alternative)
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
                db_map.add_parameter_value_item(
                    entity_class_name=key,
                    entity_byname=(key,),
                    parameter_definition_name=key2,
                    alternative_name=alternative,
                    value=value,
                    type=type_
                    )
        param_val =db_map.get_parameter_value_items()
        #print(param_val)
        try:
            db_map.commit_session("initalized CWatM database")
            print("Database committed")
        except:
            print("nothing to commit")

sql_url = sys.argv[1] 
with DatabaseMapping(sql_url) as db_map:
    scenario = db_map.get_scenario_items()
    entity_classes = db_map.get_entity_class_items()
    print(scenario)
    print(entity_classes)
    if len(sys. argv) == 4:
        update = sys.argv[3].lower() in ['true', '1']
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
