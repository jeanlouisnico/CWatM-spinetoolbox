# CWatM-spinetoolbox
This [SpineToolbox](https://github.com/spine-tools/Spine-Toolbox/tree/0.8-dev	"Github Link") project aimed at implementing the [CWatM Model](https://github.com/iiasa/CWatM	"Github Link") and creating the data workflow as well as scenario management . 

# Reading the workflow

To run this workflow, you will first need to setup SpineToolbox on your machine. Please refer to the [SpineToolbox](https://github.com/spine-tools/Spine-Toolbox/tree/0.8-dev	"Github Link") project to install and run it. This workflow was made using the 0.8-dev branch as it includes new features as well as the new SpineDBapi. You may have to clone locally as well the [Spine Database API](https://github.com/spine-tools/Spine-Database-API	"Github link") to use the 0.8-dev version of the spinedbapi.

All initial template files are available in the repo.

# Running the workflow

This workflow does not come with CWatM. Therefore, to use this workflow, you will need to get the CWatM model on your local machine as well. The model is well documented and tutorials are available on YouTube to learn how to install it with its dependency.

Prior to get the workflow working:

1. Make sure you have installed SpineToolbox as instructed and you are using the 0.8-dev branch
2. you are using Spine Database API using the branch 0.8-dev
3. You have cloned CWatM locally in your machine.

## Setting up the workflow

1. using miniconda, create an environment where workflow and CWatM libraries and other dependencies can be installed.

   go to the directory where the workflow will be located e.g. `C:\Git\<YOUR FOLDER>\`

2. _cd_ into your folder `cd C:\Git\<YOUR FOLDER>\`

3. clone the git repo into the folder `git clone git@github.com:jeanlouisnico/CWatM-spinetoolbox.git`

4. create your conda environment and activate it

   `conda create -n cwatm_wf python=3.11`

   `conda activate cwatm_wf`

5. cd in the folder where the cloned git repo is installed  `cd C:\Git\<YOUR FOLDER>\CWatM-spinetoolbox`

6. Install the required libraries for the workflow to work out

   `pip install -r requirements.txt`



You are now ready to run the workflow from SpineToolbox

## Opening the workflow and setting it up

1. run SpineToolbox from your conda environment `$ spinetoolbox`
2. Open the workflow from File>Open project (Locate where you have cloned the project)
3. You can run the workflow as is.



Not that if you already an existing workflow from a previous project, you can change the origin of the ini file from the file you have been previously configuring as shown in the picture below.



![setup](.spinetoolbox\doc\images\prime_ini.png)

## Include CWatM

As CwatM repo is quite large, it is not included in the workflow. Once you have cloned CWatM on your computer, either copy the entire CWatM folder under your workflow repo e.g. `C:\Git\<YOUR FOLDER>\` or you would need to re-link all the files defined in the cwatm tool in the workflow to the folder where CWatM is located

![rellocate_CWatM](.spinetoolbox\doc\images\cwatm_files.png)

# Why using the workflow

One of the main point of using this workflow to run CWatM model, is that you can create all alternatives and scenarios that one needs to run, and parallelise your run automatically. This is done through the UI of the cwatm_db where you can change all input/output data from the model.

NB: if you have already changed the database _cwatnm_db_, while running the entire workflow, make sure that second argument in the ***parse_toml*** tool is set to **<u>false</u>**. This will prevent to overwrite the existing database and loose all your changes. Usually the **<u>true</u>** statement is used only for 1. setting up the database. 2. reset the database to its original settings.  

## Create multiple databases

If one need, you may just create a new spine database if you want to switch from databases and avoid to have everything in a single database.
