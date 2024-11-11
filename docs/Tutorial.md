# Tutorial

Let's setup an instance of SpineToolbox (hereafter **Toolbox**) by creating an empty database, importing the initial init file provided by the example of CWatM. We will then import the calibration file. We will then see how to create alternatives to the base init file or import a new initial file from CWatM. Finally, we will to calibration run, running CWatM as a standalone model and running CWatM model as model coupling with an energy system model.

![cwatm_integration](C:\Git\CWatM-spinetoolbox-dev\docs\images\cwatm_integration.png)

## New Database

### Setting the database

Before starting setting up a totally new workflow, **Toolbox** requires to be linked to a database. In this particular case we are using .*sqlite*, but one can choose between *sqlite* and *mysql*. Create a new database by first selecting the database ![databaseicon](images/db_icon_small.png). This will display the *Data Store Properties* (DSP). From the DSP, click the *New Spine db* button to save your database in your environment.

!!! Tip

    Good practices would be that the new database is saved under \.spinetoolbox\Data\

You will then need to:

- Edit the path of the database in the following data store (copy/paste the relative path or select the file from the file icon ![fileicon](images/file_icon.png))
  - *Data Store*
  - *data_store_loop*
  - *best_calib*

This step will create an empty database with one alternative called *Base*. This alternative will be empty and we can now start populating the data from the **.ini* file into the database

### Populating the database

!!! Tip

    This section refers to the [import ini file section](navigating.md/#3-import-cwatm-ini-files) part of the workflow

The best way to start working with **Toolbox** is to take one of the CWatM setting files for the 30 arcmin or 5 arcmin. In this example we will populate the 5 arcmin setting files but this setup can be done with the 30 arcmin as well.

First, select the data connection box ![input_setting_file_icon_small](images/input_setting_file_icon_small.png)that will link the ini file to **Toolbox**. This will display the Data Connection Properties (DCP) window on the right-hand side. In case a filepath is already present in the File paths field, adding a new file will be made in addition to the current file path. One can safely remove the link by right cliking the filepath and click *remove reference(s)* or click the - button![minus_icon](images/minus_icon.png) while having the filepath selected. By clicking the + icon ![plus_icon](images/plus_icon.png)you can select the ini setting file.

As mentioned earlier, if a tool is marked with an exclamation mark :exclamation:, this means that there is a problem in the workflow. By changing the reference setting file, this will most likely be triggered in the following step but can easily be corrected.

The next step is to ensure that the file is considered in the workflow. Select the *convert_to_valid_toml* tool and it will display its Tool Properties window on the right hand side. If the name of the file from the Tool arguments exist in the Available resources listed in the tool, then this is all good and the tool is configured correctly. In case the tool arguments is displayed in red, this means that the file is not available in the Available resources. It usually happens if the file in the data connection is changed (see previous step). Simply drag and drop the file from the Available resources to the Tool arguments, then remove the link displayed in red by selecting the argument and click the - button ![minus_icon](images/minus_icon.png).

![tool_properties_convertion](images/tool_properties_convertion.png)

The second tool *parse_toml* is very important and the end-user wants to put attention into the arguments that are passed to the tool. Since there can be multiple *ini* files that are imported into the *Spine Database*, each variable should be loaded into a different **alternative**. If the **alternative** name is not changed, it will overwrite the previously imported *ini* file.

![wf3](images/import_ini.png)

The second argument :one:: is the name of the *alternative* where the ini file *parameters* will be imported in, in this tutorial we will name it *5_arcmin_base*. The :two: argument define that it will update the values and should be always set to *true* if you want to update the existing alternative, if not set it to *false*. Select the 3 tool together and run only the selection ![selection_run_icon](images/selection_run_icon.png). Running only this section will import your CWatM *ini* file into the Spine Database.

!!! Tip

    In case you have multiple *ini* file that you want to import, repeat these steps as many times as necessary. You can try this out by duplicating the original setting file and change some values in it. Relink the file in the workflow as explained in this section but allocate it to a different alternative. It will create a new alternative and import only the variables that differ from the base database that we first imported into the database.



### Fix the database for Toolbox

!!! Tip

    This section refers to the [database section](navigating.md/#4-the-spine-database) part of the workflow

The **Toolbox** database will be displaying exactly what was in the ini file originally. Therefore, the path to weather files and others should be correct. However, if the setting file was imported as is, the path filepaths need to be updated.

The most important one is the ***PathRoot*** parameter_name in the FILE_PATHS entity. Locate where the input files were saved on the machine. Other filepaths that needs attention are: **FILE_PATHS\PathMeteo**, and if necessary the **FILE_PATHS\Excel_settings_file parameter_names**.

The last parameter that requires to be changed is due to the use of Toolbox, this is the output folder location FILE_PATHS\PathOut.

One of the feature of running CWatM with Toolbox is that you can run all your scenarios in parallel. These parallelisation of the runs is automatically handled by Toolbox. However, since CWatM is writing outputs after every loop, the output folder will need to be defined relative to the path of the scenario. Simply replace the string in the **FILE_PATHS\PathOut** to `./output`. Toolbox will then create an output folder for every scenario and will avoid reading and writing to the same output files.

#### Other changes

Cold and Warm starts are possible in CWatM. The settings are located under the entity class INITITIAL CONDITIONS. The parameter **initLoad** and **initSave** should be modified similarly to the output folder and making it relative path to the project e.g. *./init/<FILENAME>* and similarly initLoad should resemble the same pattern *./init/<FILENAME>.nc*

With these settings, the database can be modified (adding alternatives and scenario) and can run CWatM as a standalone application. 

!!! Tip

    After every modification of the database, it needs to be commited by ctrl+enter or click the icon commit 

