# Tutorial

Let's setup an instance of SpineToolbox (hereafter **Toolbox**) by creating an empty database, importing the initial init file provided by the example of CWatM. We will then import the calibration file. We will then see how to create alternatives to the base init file or import a new initial file from CWatM. Finally, we will to calibration run, running CWatM as a standalone model and running CWatM model as model coupling with an energy system model.

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

This section refers [import ini file section](navigating.md/#3-import-cwatm-ini-files) 

The best way to start working with **Toolbox** is to take one of the CWatM setting files for the 30 arcmin or 5 arcmin. In this example we will populate the 5 arcmin setting files but this setup can be done with the 30 arcmin as well.

First, select the data connection box ![input_setting_file_icon_small](images/input_setting_file_icon_small.png)that will link the ini file to **Toolbox**. This will display the Data Connection Properties (DCP) window on the right-hand side. In case a filepath is already present in the File paths field, adding a new file will be made in addition to the current file path. One can safely remove the link by right cliking the filepath and click *remove reference(s)* or click the - button![minus_icon](images/minus_icon.png) while having the filepath selected. By clicking the + icon ![plus_icon](images/plus_icon.png)you can select the ini setting file.

As mentioned earlier, if a tool is marked with an exclamation mark :exclamation:, this means that there is a problem in the workflow. By changing the reference setting file, this will most likely be triggered in the following step but can easily be corrected.

The next step is to ensure that the file is considered in the workflow. Select the *convert_to_valid_toml* tool and it will display its Tool Properties window on the right hand side. If the name of the file from the Tool arguments exist in the Available resources listed in the tool, then this is all good and the tool is configured correctly. In case the tool arguments is displayed in red, this means that the file is not available in the Available resources. It usually happens if the file in the data connection is changed (see previous step). Simply drag and drop the file from the Available resources to the Tool arguments, then remove the link displayed in red by selecting the argument and click the - button ![minus_icon](images/minus_icon.png).

![tool_properties_convertion](images/tool_properties_convertion.png)
