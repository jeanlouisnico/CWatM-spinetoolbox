# Tutorial

Let's setup an instance of SpineToolbox by creating an empty database, importing the initial init file provided by the example of CWatM. We will then import the calibration file. We will then see how to create alternatives to the base init file or import a new initial file from CWatM. Finally, we will to calibration run, running CWatM as a standalone model and running CWatM model as model coupling with an energy system model.

## New Database

Before starting setting up a totally new workflow, toolbox requires to be linked to a database. In this particular case we are using .*sqlite*, but one can choose between *sqlite* and *mysql*. Create a new database by first selecting the database <img src="images/db_icon.png" alt="database_icon" style="zoom:10%;" />. This will display the *Data Store Properties* (DSP). From the DSP, click the *New Spine db* button to save your database in your environment.

!!! Tip

    Good practices would be that the new database is saved under .\.spinetoolbox\Data\

