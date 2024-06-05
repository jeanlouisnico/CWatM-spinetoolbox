import datetime
import collections.abc
import spinedb_api as api
from spinedb_api import DatabaseMapping
from spinedb_api import purge
import sys

url = sys.argv[1]

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
            
if sys.argv[2].lower() in ['false', '0']:
	print("No updates has been performed, re-using existing database")
else:
    sql_url = sys.argv[1] 
    print("Cleaning the database")
    remove_all(sql_url)