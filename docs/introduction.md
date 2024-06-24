# Why integrating hydrology and energy system models

## For Whom?

IRENA FlexTool was primarily designed to be used for planning the energy transition in developing countries. It is developed by VTT for IRENA and it is distributed to IRENA members. IRENA FlexTool is also accessible on GitHub. With the growing complexity of energy system planning, the need to have an understanding of where the water comes from and goes become necessary to better manage hydropower stations that are installed along a river basin. To this extent, 

## How does it work

The first challenge is to identify what each model can perform and provide as an input to the next model. the limitations of each model should be acknowledged in case further improvement or specific challenges need to be tackled. CWatM is very versatile and has integrated many features and sectors over the years. It integrates global weather files and extract the data needed for the studied basin. It can further simulate discharge flows from one cell to another with a daily resolution. It evaluates the reservoirs level and can allocate water resources for agricultural, domestic, industrial, or farming use. Groundwater is also possible to simulate via the existing integration of CWatM and Modflow6 in the core of CWatM. 

![general_concept](images/CWatM_FlexTool_integ.svg)



Translating the concept in regional models



Model interactions in practice for a specific basin



![concept_model](images/flow_chart.svg)

## CWatM-spinetoolbox

This [SpineToolbox](https://github.com/spine-tools/Spine-Toolbox/	"Github Link") workflow aimed at implementing the [CWatM Model](https://github.com/iiasa/CWatM	"Github Link") and creating the data workflow as well as scenario management. 

## Reading the workflow

To run this workflow, you will first need to setup SpineToolbox on your machine. Please refer to the [SpineToolbox](https://github.com/spine-tools/Spine-Toolbox/tree/0.8-dev	"Github Link") project to install and run it. This workflow was made using the 0.8 version as it includes new features as well as the new SpineDBapi.

All initial template files are available in the repo.
