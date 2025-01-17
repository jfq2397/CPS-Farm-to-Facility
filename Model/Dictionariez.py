# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 11:31:26 2021

@author: gareyes3
"""
import math
import pandas as pd
import numpy as np
import SCInputz
import Inputz
import MainModel3z
import ScenCondz


Column_Names_Outs = ["Step_CFU_Acc",
                    "Step_CFU_Rej",
                    "Step_CFU_PerR",
                    "Step_Wei_Acc",
                    "Step_Wei_Rej",
                    "Step_Wei_PerR",
                    ]


Column_Names_Progression = ["Contam Event Before PHS",
                            "Bef Pre-Harvest Samp",
                            "Aft Pre-Harvest Samp",
                            "Contam Event After PHS",
                            "Bef Harvest Samp",
                            "Aft Harvest Samp",
                            "Bef Receiving Samp",
                            "After Receiving Samp",
                            "Bef Shredding",
                            "Bef Conveyor Belt",
                            "Bef Washing",
                            "Bef Shaker Table",
                            "Bef Centrifuge",
                            "Aft Value Addition",
                            "Bef Final Prod S",
                            "Final Product Facility"
                            ]

Column_Per_Contaminated = ["PropCont_CE_B_PHS",
                            "PropCont_B_PHS",
                            "PropCont_A_PHS",
                            "PropCont_CE_A_PHS",
                            "PropCont_B_HS",
                            "PropCont_A_PHS",
                            "PropCont_B_RS",
                            "PropCont_A_RS",
                            "PropCont_B_Shredding",
                            "PropCont_B_CBelt",
                            "PropCont_B_Washing",
                            "PropCont_B_ST",
                            "PropCont_B_Cent",
                            "PropCont_A_VA",
                            "PropCont_B_FPS",
                            "PropCont_A_FP",
                            "TotalCont_A_FP",
    ]






def Output_DF_Creation(Column_Names, Niterations):
    Outputs_Df =pd.DataFrame(np.NaN, index= range(Niterations), columns =Column_Names)
    return Outputs_Df



def Output_Collection_Prog(df, outputDF, Step_Column,i):
    #df= main model df
    #outputDF = contprogdataframe
    #Step_column = column for the step we are at
    Total_CFU = sum(df.CFU)
    outputDF.at[i,Step_Column] = Total_CFU
    return outputDF

def Pop_Output_Colection(df, outputDF, Step_Column, i):
    Pop  = df[df.CFU>0]
    TotalPop = len(Pop)
    Total_whole = len(df.CFU)
    Pop_Final = TotalPop /Total_whole
    outputDF.at[i,Step_Column] =  Pop_Final
    return outputDF

#df.CFU=np.random.uniform(0,1,2000)
#df.CFU[1] = 0

def Output_Collection_Final(df, outputDF, Step, Cont_Before, Weight_Before, i, Niterations):
    #Contaminations
    Cont_Acc = sum(df.CFU)
    Cont_Rej = Cont_Before-Cont_Acc
    if Cont_Acc == 0:
        Cont_PerR = 1
    else:
        Cont_PerR = Cont_Rej/(Cont_Acc+Cont_Rej) #Percentage Rejected by Finished product sampling
    #Weight
    Wei_Acc = sum(df.Weight)
    Wei_Rej = Weight_Before-Wei_Acc
    Wei_PerR =  Wei_Rej/(Wei_Rej+Wei_Acc)
    
    outputDF.at[i,"Step_CFU_Acc"] = Cont_Acc
    outputDF.at[i,"Step_CFU_Rej"] = Cont_Rej
    outputDF.at[i,"Step_CFU_PerR"] = Cont_PerR
    outputDF.at[i,"Step_Wei_Acc"] = Wei_Acc
    outputDF.at[i,"Step_Wei_Rej"] = Wei_Rej
    outputDF.at[i,"Step_Wei_PerR"] = Wei_PerR
    if i == Niterations -1:
        outputDF.columns = outputDF.columns.str.replace("Step", Step) #Updating Head of Columns Change column end iteration.
    
    return outputDF

#%%
#Sens Analysis


##Creation of Random Variables. 

#Contamination Determination Inputs
Total_grams= SCInputz.Field_Weight*454


CFU_10000g = Total_grams/10000 #-4 log
CFU_1000g = Total_grams/1000  #-3 log
CFU_100g = Total_grams/100 #-2 log
CFU_10g = Total_grams/10  #-1 log
CFU_g =  Total_grams #0 log
CFU_0_1g = Total_grams*10 #1 log


CFU_0_01g = Total_grams*100 #2log

#Contamination List
Contamination_List = [CFU_10000g,CFU_1000g,CFU_100g,CFU_10g,CFU_g,CFU_0_1g]
#Clustering List
Clustering_List =[100,1000,10000,100000]
NoClusters_List = [1,2,3,4]
SampleSize_List = [60,120,240,600,1200]
NoSamples_List = [1,2,3,4,5,6,7,8,9,10]
NoGrabs_List = [1,60,120,240,300,600,1200]



Sensitivity_Analysis_Dic = [
                            #Field Setup Factors
                            "InitialCont" ,
                            "ClusteringPer",
                            "ClusterSize",
                            "Time_CE_H",
                            "Total_CE_H_Dieoff",
                            #Sampling Type: 
                            "PH4d",
                            "PH4h",
                            "PHInt",
                            "HTrad",
                            "RTrad",
                            "FPTrad",
                            
                            '''
                            #Sampling Factors
                            "SampleSize",
                            "SamplesPSublot",
                            "NumberGrabs",
                            '''
                            #Harvest
                            "Harvest Wash Red",
                            #Pre-coolin
                            "Time_H_PC",
                            "Temp_H_PC",
                            "Time Precooling",
                            "Temp Precooling",
                            "Pre_cooling",
                            #Receiving
                            "Time_Storage_R",
                            "Temp_Storage_R",
                            #Processing Factor
                            "PreWashYN",
                            "WashingYN",
                            "TotalCFUFP"
    ]
    

def Func_LoadInputs (OutputDF,i,df, TotalDieoff):
    #Setup Factors
    #Initial Contamination Factors
    OutputDF.at[i, "InitialCont"] =  SCInputz.PSHazard_lvl #InitialContmination
    OutputDF.at[i, "ClusteringPer"] =  SCInputz.PSNo_Cont_Clusters #Cluestering Level
    OutputDF.at[i, "ClusterSize"] =   SCInputz.PSCluster_Size #InitialContmination
    OutputDF.at[i, "Time_CE_H"] =  Inputz.Time_CE_H #Time between contamination event and harvest
    OutputDF.at[i, "Total_CE_H_Dieoff"] = TotalDieoff  #TotalDieoff between contamination event and harvest. 
    
    #Sampling Selection
    OutputDF.loc[i, "PH4d"] = ScenCondz.PHS_4d #InitialContmination
    OutputDF.loc[i, "PH4h"] = ScenCondz.PHS_4h #Cluestering Level
    OutputDF.loc[i, "PHInt"] =  ScenCondz.PHS_Int #InitialContmination
    OutputDF.loc[i, "HTrad"] =  ScenCondz.H_Sampling #Time between contamination event and harvest
    OutputDF.loc[i, "RTrad"] =  ScenCondz.R_Sampling #Time between contamination event and harvest
    OutputDF.loc[i, "FPTrad"] =  ScenCondz.FP_Sampling #Time between contamination event and harvest
    
    '''
    #Sampling Factors
    OutputDF.at[i, "SampleSize"] = SCInputz.sample_size_PH #Sample Size at Pe-Harvest
    OutputDF.at[i, "SamplesPSublot"] = SCInputz.n_samples_slot_PH #Number of Samples per sublot
    OutputDF.at[i, "NumberGrabs"] =  SCInputz.No_Grabs_PH #Number of Grabs at PreHarvest.
    '''
    #Harvests
    OutputDF.at[i, "Harvest Wash Red"] =  Inputz.Harvest_Cspray_red #Number of Grabs at PreHarvest.
    #Pre-cooling
    OutputDF.at[i, "Time_H_PC"] =  Inputz.Time_H_PreCooling #Time beetween harvest and pre-cooling
    OutputDF.at[i, "Temp_H_PC"] =  Inputz.Temperature_H_PreCooling #Time beetween harvest and pre-cooling
    OutputDF.at[i, "Time Precooling"] =  Inputz.Time_PreCooling #Pre-cooling process length time
    OutputDF.at[i, "Temp Precooling"] =  Inputz.Temperature_PreCooling #Pre-cooling process temperature
    OutputDF.loc[i, "Pre_cooling"] =  SCInputz.Pre_CoolingYN #Number of Grabs at PreHarvest.
    #Receiving
    OutputDF.at[i, "Time_Storage_R"] =  Inputz.Time_Storage_R #Time storage at receiving
    OutputDF.at[i, "Temp_Storage_R"] =  Inputz.Temperature_Storage_R #temperature of receiving storage.
    #Procesing Factord
    OutputDF.loc[i, "PreWashYN"] =  SCInputz.C_Spray_HYN #Washing Yes or Not
    OutputDF.loc[i, "WashingYN"] =  SCInputz.Washing_YN #Washing Yes or Not
    OutputDF.loc[i, "TotalCFUFP"] =  df["CFU"].sum()
    
    return   OutputDF

    








































'''
df_prog = Output_DF_Creation(Column_Names =Column_Names_Progression, Niterations =20)
df_outs = Output_DF_Creation(Column_Names =Column_Names_Outs, Niterations =20)


df_prog = Output_Collection_Prog(df = df,
                                outputDF = df_prog,
                                Step_Column = "Bef Pre-Harvest Samp", 
                                i =11 )


ContBEf = 10000
weightBEf = 100000
df_outs = Output_Collection_Final(df = df, 
                                outputDF = df_outs, 
                                Step = "PH", 
                                Cont_Before = 10000, 
                                Weight_Before =1000000, 
                                i = 10, 
                                Niterations = 20)

'''