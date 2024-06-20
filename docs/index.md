# Welcome to FlexTool/CWatM User Guide!



<img src="images\flex_cwatm_logo.png" alt="flex_cwatm_logo" style="zoom:20%;height: auto; object-fit: cover;" />

## The genesis

In an effort to support the energy transition and consider the impact of climate change, needs to understand better the interaction between water cycles and its impact on water availability for hydropower stations is becoming of utmost important. This is in particular importance in regions where hydropower is the main source of power and where water has conflicting usage between sectors e.g. energy, agriculture. As a technical research institute, VTT has been committed to develop state-of-the-art energy system models, such as IRENA FlexTool, but also many others. 

On the other hand, hydrology modelling has seen a leap in taking at hand the development of models that consider the nexus dilemma in their modelling approach. One of these models is CWatM, an open source hydrology model developed by IIASA. CWatM covers multiple water-dependent sectors such as the agriculture and energy. It includes the water demand both from domestic and industrial usage. It can evaluate the water demand from crops depending on the type of crops that is being grown in the water basin. Recently, CWatM has integrated the groundwater model Modflow6 in its heart, offering more possibility to track down where the water goes. The time resolution goes down to daily simulation of the water flow, and the geographical resolution starts from 30 arc min down to a 1 km resolution. It grids the area where the water is extracted and has a module for integrating water reservoirs and its discharge over time. However, the hydropower representation in CWatM is very simple, and does not consider its integration into an energy system. This is where our motivation to create a bridge between these two established and open source models is born. 

Unlike CWatM, IRENA FlexTool is an optimisation energy system model that aims at minimising the system costs in its operations at an hourly resolution. It is highly flexible and technologies can be specific to a single power plant or aggregated by energy sources. It offers investments decision on power production technology development and infrastructure reinforcements or capacity expansion. Simple to use, the third version of FlexTool now runs through an open-source user interface, also co-developed by VTT, SpineToolbox. SpineToolbox is a data flow, scenario, and alternative management interface. SpineToolbox is model agnostic and can run natively any models developed in Python, Julia, and GAMS. Moreover, SpineToolbox can run any *.exe software, or run batch files within its terminal. It is a cross platform tool that can be used on Windows, Linux, and MacOS. Since CWatM does not have any user interface, the first step towards model integration was to give CWatM an interface where all its scenario can be handled in a single database (instead of being scattered through multiple, self-managed *.ini files). SpineToolbox can further handle the parallelisation of the runs by isolating each instance of every models.

## Support

Currently, the model coupling is supported by the Finnish Ministry of Foreign Affairs and the Research Council of Finland via the TU-Nexus project. The University of Oulu brings their expertise in hydrology while VTT provides the energy system modelling expertise as well as the model coupling competences.

## How to cite

At the moment, we are still in the early phase of the model integration, therefore no scientific publication is yet available. However, in an effort of transparency, we are making the development available for anyone interested in this integration, and invite any experts in the field to test it out and provide us feedback on its usability. We are trying to keep the research community up-to-date via this documentation page.

## Go further

Learn more about CWatM here --> 

Learn more about IRENA FlexTool here -->

Learn more about SpineToolbox here and the Spine Family suite.

## The team

VTT is the Technical Research of Finland in which the Design and Operation of Energy System team is leading the development of energy system modelling tools. 

<table style="border-collapse: collapse; border: none; border-spacing: 0px;">
	<tr>
		<td style="border-top: 1px solid rgb(0, 0, 0); text-align: center; padding-right: 3pt; padding-left: 3pt;">
			<img src="images\people\JNL.png" alt="JNL" style="zoom:100%;" />
			<br>
			Research Team Leader
			<br>
            Model coupling and CWatM 
            <br>
            integration in SpineToolbox
            <br>
		</td>
		<td style="border-top: 1px solid rgb(0, 0, 0); text-align: center; padding-right: 3pt; padding-left: 3pt;">
			<img src="images\people\JK.png" alt="JNL" style="zoom:100%;" />
			<br>
			Principal Scientist
            <br>
            Model coupling
            <br>
		</td>
		<td style="border-top: 1px solid rgb(0, 0, 0); text-align: center; padding-right: 3pt; padding-left: 3pt;">
			<img src="images\people\NP.png" alt="JNL" style="zoom:100%;" />
			<br>
			Research Scientist
            <br>
            FlexTool model
            <br>
		</td>
		<td style="border-top: 1px solid rgb(0, 0, 0); text-align: center; padding-right: 3pt; padding-left: 3pt;">
			<img src="images\people\RA.png" alt="JNL" style="zoom:100%;" />
			<br>
			Research Scientist
            <br>
            FlexTool model
            <br>
		</td>
	</tr>
	<tr>
		<td colspan="2" style="border-bottom: 1px solid rgb(0, 0, 0); text-align: center; padding-right: 3pt; padding-left: 3pt;">
			<img src="images\people\DU.png" alt="Doniyor Urishov" style="zoom:70%;" />
			<br>
			Research Scientist
            <br>
            Local interaction
            <br>
		</td>
		<td colspan="2" style="border-bottom: 1px solid rgb(0, 0, 0); text-align: center; padding-right: 3pt; padding-left: 3pt;">
            <img src="images\people\AT.png" alt="Arttu Tupala" style="zoom:70%;" />
			<br>
			Research Trainee
            <br>
            FlexTool model
            <br>
		</td>
	</tr>
</table>

The University of Oulu is located in the north of Finland and has a strong water research team developed in the water, energy, and environmental engineering research unit.
