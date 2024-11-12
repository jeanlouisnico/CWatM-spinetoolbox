# -------------------------------------------------------------------------
# Name:        INITCONDITION
# Purpose:	   Read/write initial condtions for warm start
#
# Author:      PB
#
# Created:     19/08/2016
# Copyright:   (c) PB 2016
# -------------------------------------------------------------------------

from cwatm.management_modules.data_handling import *
import importlib
# importlib to import pandas as pd in has crop sentitive version is used
# import pandas as pd

class initcondition(object):

    """
    READ/WRITE INITIAL CONDITIONS
    all initial condition can be stored at the end of a run to be used as a **warm** start for a following up run


    **Global variables**

    =====================================  ======================================================================  =====
    Variable [self.var]                    Description                                                             Unit 
    =====================================  ======================================================================  =====
    modflow                                Flag: True if modflow_coupling = True in settings file                  --   
    Crops_names                            Internal: List of specific crops                                        --   
    includeCrops                           1 when includeCrops=True in Settings, 0 otherwise                       bool 
    Crops                                  Internal: List of specific crops and Kc/Ky parameters                   --   
    includeDesal                                                                                                   --   
    unlimitedDesal                                                                                                 --   
    desalAnnualCap                                                                                                 --   
    reservoir_transfers                    [['Giving reservoir'][i], ['Receiving reservoir'][i], ['Fraction of li  array
    wwt_def                                                                                                        --   
    wastewater_to_reservoirs                                                                                       --   
    loadInit                               Flag: if true initial conditions are loaded                             --   
    initLoadFile                           load file name of the initial condition data                            --   
    saveInit                               Flag: if true initial conditions are saved                              --   
    saveInitFile                           save file name of the initial condition data                            --   
    coverTypes                             land cover types - forest - grassland - irrPaddy - irrNonPaddy - water  --   
    =====================================  ======================================================================  =====

    **Functions**
    """


    def __init__(self, model):
        self.var = model.var
        self.model = model

    def crops_initialise(self, xl_settings_file_path):
        pd = importlib.import_module("pandas", package=None)
        df = pd.read_excel(xl_settings_file_path, sheet_name='Crops')

        # Crops = [ [planting date, [length of growth stage i from planting, kc_i, ky_i]_i]_crop]
        Crops = []
        Crops_names = []
        for i in df.index:
            crop = [df['Planting month'][i]]
            growth_stage_end_month = 0

            # crop = [planting date, [GS1, KC1, KY1], [GS1+GS2, KC2, KY2], ..., [GS1+GS2+GS3+GS4, KC4, KY4]]
            for gs in range(1, 5):
                growth_stage_end_month += df['GS' + str(gs)][i]
                gs_parameters = [growth_stage_end_month, df['KC' + str(gs)][i], df['KY' + str(gs)][i]]
                crop.append(gs_parameters)

            # If the crop inputs are given in days, we pre-calculate the annual cycle of crop coefficients
            # using the first three crop coefficients and four growth stages, following the
            # flat - linear increase - flat - linear decrease standard FAO/AEZ crop coefficient timeseries

            # We detect if the crop inputs are given in days if the total growing season is less than 36:
            # This assumes crops have growing to harvest lengths of less than 60 months and a minimum of 60 days
            self.var.daily_crop_KC = False
            if growth_stage_end_month > 60:
                self.var.daily_crop_KC = True

                KC_crop_daily_stage_1 = [df['KC1'][i]]*df['GS1'][i]
                KC_crop_daily_stage_2 = [df['KC1'][i] * (1 - (d / df['GS2'][i])) + df['KC2'][i] * (d / df['GS2'][i]) for
                                         d in range(df['GS2'][i])]
                KC_crop_daily_stage_3 = [df['KC2'][i]]*df['GS3'][i]
                KC_crop_daily_stage_4 = [df['KC2'][i] * (1 - (d / df['GS4'][i])) + df['KC3'][i] * (d / df['GS4'][i]) for
                                         d in range(df['GS4'][i])]

                # crop = [planting date,
                #        [length of growth stage i from planting, kc_i, ky_i]_i,
                #        [growing cycle of daily KCs]]

                crop.append(
                    KC_crop_daily_stage_1 + KC_crop_daily_stage_2 + KC_crop_daily_stage_3 + KC_crop_daily_stage_4)

            Crops.append(crop)
            Crops_names.append(df['Crop'][i])

        return Crops, Crops_names

    def reservoir_transfers(self, xl_settings_file_path):
        pd = importlib.import_module("pandas", package=None)
        df = pd.read_excel(xl_settings_file_path, header=None, sheet_name='Reservoir_transfers')

        # reservoir_transfers = [ [Giving reservoir, Receiving reservoir, [366-day array of releases]] ]
        reservoir_transfers = []

        for col in list(df)[5:]:
            releases = [df[col][4+day] for day in range(366)]
            transfer = [int(df[col][1]), int(df[col][2]), releases]
            reservoir_transfers.append(transfer)

        return reservoir_transfers
 
    # To initialize wastewater2reservoir; and wastewater attributes
    def wastewater_to_reservoirs(self, xl_settings_file_path):
        # fix - build an object with wwtp_id as key and res as values.
        # get unique wwtp_id and iterate
        pd = importlib.import_module("pandas", package=None)
        df = pd.read_excel(xl_settings_file_path, sheet_name='Wastewater_to_reservoirs')
        
       
        wwtp_to_reservoir = {}

        for wwtpid in df['Sending WWTP'].unique():
            wwtp_to_reservoir[wwtpid] = df[df['Sending WWTP'] == wwtpid]['Receiving Reservoir'].tolist()
            #transfer = [df['Sending WWTP'][i], df['Receiving Reservoir'][i]]
            #wwtp_to_reservoir.append(transfer)
        #print(wwtp_to_reservoir)
        return wwtp_to_reservoir
    
    def wasterwater_def(self, xl_settings_file_path):
        pd = importlib.import_module("pandas", package=None)
        df = pd.read_excel(xl_settings_file_path, sheet_name='Wastewater_def')
        
        cols = ['From year', 'To year', 'Volume (cubic m per day)', 'Treatment days', 'Treatment level', 'Export share', 'Domestic', 'Industrial', 'min_HRT']
        wwtp_definitions = {}
        for wwtpid in df['WWTP ID'].unique():
            wwtp_definitions[wwtpid] = df[df['WWTP ID'] == wwtpid][cols].to_numpy()
        return wwtp_definitions
    
    def desalinationCapacity(self, xl_settings_file_path):
        pd = importlib.import_module("pandas", package=None)
        df = pd.read_excel(xl_settings_file_path, sheet_name='Desalination')
        
        s_year = globals.dateVar['dateBegin'].year
        e_year = globals.dateVar['dateEnd'].year
        
        desalCap = {}
        lastDesal = 0
        for year in range(s_year, e_year + 1):
            if np.in1d(year, df['Year']):
                lastDesal = df[df['Year'] == year]['Capacity'].to_list()[0]
            desalCap[year] = lastDesal
        return desalCap
        
    
    def initial(self):
        """
        initial part of the initcondition module
		Puts all the variables which has to be stored in 2 lists:

		* initCondVar: the name of the variable in the init netcdf file
		* initCondVarValue: the variable as it can be read with the 'eval' command

		Reads the parameter *save_initial* and *save_initial* to know if to save or load initial values
        """

        # list all initiatial variables
        # Snow & Frost
        number = int(loadmap('NumberSnowLayers'))
        for i in range(number):
            initCondVar.append("SnowCover"+str(i+1))
            initCondVarValue.append("SnowCoverS["+str(i)+"]")
        initCondVar.append("FrostIndex")
        initCondVarValue.append("FrostIndex")

        if checkOption('includeRunoffConcentration'):
            for i in range(10):
                initCondVar.append("runoff_conc" + str(i + 1))
                initCondVarValue.append("runoff_conc[" + str(i) + "]")

        # soil / landcover
        i = 0
        self.var.coverTypes = list(map(str.strip, cbinding("coverTypes").split(",")))

        # soil paddy irrigation
        initCondVar.append("topwater")
        initCondVarValue.append("topwater")

        for coverType in self.var.coverTypes:
            if coverType in ['forest', 'grassland', 'irrPaddy', 'irrNonPaddy']:
                for cond in ["interceptStor", "w1","w2","w3"]:
                    initCondVar.append(coverType+"_"+ cond)
                    initCondVarValue.append(cond+"["+str(i)+"]")
            if coverType in ['sealed']:
                for cond in ["interceptStor"]:
                    initCondVar.append(coverType+"_"+ cond)
                    initCondVarValue.append(cond+"["+str(i)+"]")
            i += 1

        self.var.includeCrops = False
        if "includeCrops" in option:
            self.var.includeCrops = checkOption('includeCrops')

        if self.var.includeCrops:

            if 'Excel_settings_file' in binding:
                xl_settings_file_path = cbinding('Excel_settings_file')
                self.var.Crops, self.var.Crops_names = self.crops_initialise(xl_settings_file_path)
            else:
                msg = "The Excel settings file needs to be included into the settings file:\n" \
                      "Excel_settings_file ="+r"*PATH*\cwatm_settings.xlsx"+"\n"
                raise CWATMError(msg)

            initCondVar.append('frac_totalIrr_max')
            initCondVarValue.append('frac_totalIrr_max')

            initCondVar.append('frac_totalnonIrr_max')
            initCondVarValue.append('frac_totalnonIrr_max')

            for c in range(len(self.var.Crops)):

                initCondVar.append('monthCounter_'+ str(c))
                initCondVarValue.append('monthCounter['+str(c)+']')

                initCondVar.append('fracCrops_Irr_'+ str(c))
                initCondVarValue.append('fracCrops_Irr['+str(c)+']')

                initCondVar.append('fracCrops_nonIrr_'+ str(c))
                initCondVarValue.append('fracCrops_nonIrr['+str(c)+']')

                initCondVar.append('activatedCrops_'+ str(c))
                initCondVarValue.append('activatedCrops['+str(c)+']')

        # water demand
        initCondVar.append("unmetDemandPaddy")
        initCondVarValue.append("unmetDemandPaddy")
        initCondVar.append("unmetDemandNonpaddy")
        initCondVarValue.append("unmetDemandNonpaddy")

        initCondVar.append('unmetDemand_runningSum')
        initCondVarValue.append('unmetDemand_runningSum')
        
        # Desalination
        self.var.includeDesal = False
        self.var.unlimitedDesal = False
        if 'includeDesalination' in option:
            self.var.includeDesal = checkOption('includeDesalination')
        
        if self.var.includeDesal:
            self.var.unlimitedDesal = returnBool('unlimitedDesalinationCapacity')
            if not self.var.unlimitedDesal:
                xl_settings_file_path = cbinding('Excel_settings_file')
                self.var.desalAnnualCap = self.desalinationCapacity(xl_settings_file_path)
        
        # groundwater
        if not self.var.modflow:
            initCondVar.append("storGroundwater")
            initCondVarValue.append("storGroundwater")

        # routing
        Var1 = ["channelStorage", "discharge", "riverbedExchange"]
        Var2 = ["channelStorage", "discharge", "riverbedExchange"]

        initCondVar.extend(Var1)
        initCondVarValue.extend(Var2)

        # lakes & reservoirs
        if checkOption('includeWaterBodies'):
            Var1 = ["lakeInflow", "lakeStorage","reservoirStorage","outLake","lakeOutflow"]
            Var2 = ["lakeInflow","lakeVolume","reservoirStorage","outLake","lakeOutflow"]
            initCondVar.extend(Var1)
            initCondVarValue.extend(Var2)

        # lakes & reservoirs

        if checkOption('includeWaterBodies'):
            if returnBool('useSmallLakes'):
                Var1 = ["smalllakeInflow","smalllakeStorage","smalllakeOutflow"]
                Var2 = ["smalllakeInflowOld","smalllakeVolumeM3","smalllakeOutflow"]
                initCondVar.extend(Var1)
                initCondVarValue.extend(Var2)

        if 'reservoir_transfers' in option:
            if checkOption('reservoir_transfers'):
                if 'Excel_settings_file' in binding:
                    xl_settings_file_path = cbinding('Excel_settings_file')
                    self.var.reservoir_transfers = self.reservoir_transfers(xl_settings_file_path)
        
        if 'includeWastewater' in option:
            if checkOption('includeWastewater'):
                if 'Excel_settings_file' in binding:
                    xl_settings_file_path = cbinding('Excel_settings_file')
                    self.var.wwt_def = self.wasterwater_def(xl_settings_file_path)
                    self.var.wastewater_to_reservoirs = self.wastewater_to_reservoirs(xl_settings_file_path)
                    
        
        if 'relax_irrigation_agents' in option:
            if checkOption('relax_irrigation_agents'):
                if 'irrigation_agent_SW_request_month_m3' in binding:
                    initCondVar.append("relaxSWagent")
                    initCondVarValue.append("relaxSWagent")
                if 'irrigation_agent_GW_request_month_m3' in binding:
                    initCondVar.append("relaxGWagent")
                    initCondVarValue.append("relaxGWagent")

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Load init file - a single file can be loaded - needs path and file name
        self.var.loadInit = returnBool('load_initial')
        if self.var.loadInit:
            self.var.initLoadFile = cbinding('initLoad')

        # Safe init file
        # several initial conditions can be stored in different netcdf files
        # initSave has the path and the first part of the name
        # intInit has the dates - as a single date, as several dates
        # or in certain interval e.g. 2y = every 2 years, 3m = every 3 month, 15d = every 15 days

        self.var.saveInit = returnBool('save_initial')
        self.var.initmap = {}

        if self.var.saveInit:
            self.var.saveInitFile = cbinding('initSave')
            initdates = cbinding('StepInit').split()
            datetosaveInit(initdates,dateVar['dateBegin'],dateVar['dateEnd'])

            #for d in initdates:
            #    dd = datetoInt(d, dateVar['dateBegin'])
            #    dateVar['intInit'].append(datetoInt(d, dateVar['dateBegin']))

    def dynamic(self):
        """
        Dynamic part of the initcondition module
        write initital conditions into a single netcdf file

        Note:
            Several dates can be stored in different netcdf files
        """

        if self.var.saveInit:
            if  dateVar['curr'] in dateVar['intInit']:
                saveFile = self.var.saveInitFile + "_" + "%02d%02d%02d.nc" % (dateVar['currDate'].year, dateVar['currDate'].month, dateVar['currDate'].day)
                initVar=[]
                i = 0
                for var in initCondVar:
                    variabel = "self.var."+initCondVarValue[i]
                    #print variabel
                    initVar.append(eval(variabel))
                    i += 1
                writeIniNetcdf(saveFile, initCondVar,initVar)

