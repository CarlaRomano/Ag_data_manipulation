# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 08:50:29 2022

@author: romanc
"""


import os
import pandas as pd
from glob import glob
import numpy as np
# Function to read and process the text file
def process_comp_file(file_path):
    columns_to_keep = [0, 1, 2, 3,5,7, 14, 22, 23, 79, 107, 108]
    column_labels = [
        "Comp % - Low Value",
        "Comp % - Representative Value",
        "Comp % - High Value",
        "Component Name",
        "Major Component",
        "Local phase",
        "Runoff Class",
        "Hydric Rating",
        "Drainage Class",
        "Hydrologic Group",
        "mukey",
        "cokey",
    ]

    # Read the text file into a DataFrame
    comp_df = pd.read_csv(file_path, sep="|", header=None, usecols=columns_to_keep)

    # Rename columns
    comp_df.columns = column_labels
    comp_df['Area_Symbol']=subfolder[-5:]

    return comp_df

def process_chor_file(file_path):
    columns_to_keep = [6, 9, 12, 60, 63, 66, 82, 114, 135,169,170]
    column_labels = [
        "Top Depth - Representative Value",
        "Bottom Depth - Representative Value",
        "Thickness - Representative Value",
        "Total Clay - Representative Value",
        "CaCO3 Clay - Representative Value",
        "OM - Representative Value",
        "Ksat - Representative Value",
        "CaCO3 - Representative Value",
        "pH H2O - Representative Value",
        "cokey",
        "chorizon"
    ]

    # Read the text file into a DataFrame
    chor_df = pd.read_csv(file_path, sep="|", header=None, usecols=columns_to_keep)   
    # Rename columns
    chor_df.columns = column_labels
    # chor_df['Area_Symbol']=subfolder[-5:]

    return chor_df
##Folder where SSURGO data has been downloaded
root_folder = "M:/SW_SAMPLING/15_years_sampling/2008-2022/GIS/SSURGO/ssurgo-downloads"  # Replace with the actual root folder path
# os.chdir(root_folder)
part_folders = glob(os.path.join(root_folder, "Part*"))
comp_dfs = []
chor_dfs = []
# Find all folders starting with "Part"
for part_folder in part_folders:
    # Find subfolders within each "Part" folder
    subfolders = glob(os.path.join(part_folder, "WI*"))
    for subfolder in subfolders:
        tabular_folder = os.path.join(subfolder, "tabular")
        # print (subfolder)
        # Check if the "tabular" folder exists
        if os.path.exists(tabular_folder):
            # Find only text files named "comp" in the "tabular" folder
            text_files = glob(os.path.join(tabular_folder, "comp.txt"))
            for text_file in text_files:
                # Process the text file
                comp_data = process_comp_file(text_file)
                # Append to the list of comp DataFrames
                comp_dfs.append(comp_data)
                
            # Find only text files named "chor" in the "tabular" folder
            text_files2 = glob(os.path.join(tabular_folder, "chorizon.txt"))

            for text_file2 in text_files2:
                # Process the text file
                chor_data = process_chor_file(text_file2)
                chor_dfs.append(chor_data)
# Combine all comp DataFrames into a single DataFrame
combined_comp_df = pd.concat(comp_dfs, ignore_index=True)
# Remove duplicate rows
combined_comp_df = combined_comp_df.drop_duplicates()
# Combine all comp DataFrames into a single DataFrame
combined_chor_df = pd.concat(chor_dfs, ignore_index=True)
# Remove duplicate rows
combined_chor_df = combined_chor_df.drop_duplicates()


##Folder where file containing SSURGO mukey joined to my shapefiles is stored
file_folder = 'M:/Neonicotinoids/GW_REVIEW'
os.chdir(file_folder)
df=pd.read_excel('Buffer_SSURGO.xls')
df = df.dropna(how='all')
df_co=pd.merge(df,combined_comp_df,how='left',on='mukey')
df_co_nan=df_co[pd.isnull(df_co['cokey'])]   
# df_co['cokey'] = pd.to_numeric(df_co['cokey'], errors='coerce').astype('Int64')
df_all=pd.merge(df_co,combined_chor_df,on='cokey',how='left')
df_water=df_all[df_all['Component Name'].str.contains('Water')]
df_all=df_all[df_all['Component Name']!='Water']
df_nan=df_all[pd.isnull(df_all['chorizon'])]    
df_nan = df_nan.drop_duplicates(subset=['mukey','cokey'])
df_all2 = df_all.dropna(subset=['Top Depth - Representative Value'])
df_all2['Thickness']=df_all2['Bottom Depth - Representative Value']-df_all2['Top Depth - Representative Value']


##HYDRAULIC CONDUCTIVITY (um/s): WEIGHTED AVERAGES BASED ON THE THICKNESS OF EACH HORIZON
filtered_rows = df_all2[df_all2['Ksat - Representative Value'].notna()]
weighted_ksat0 = (filtered_rows['Ksat - Representative Value'] * filtered_rows['Thickness']).groupby([filtered_rows['mukey'], filtered_rows['WUWN'], filtered_rows['cokey']]).sum() / filtered_rows.groupby(['mukey', 'WUWN','cokey'])['Thickness'].sum()
weighted_ksat0=weighted_ksat0.reset_index()
cokey_det=filtered_rows[['WUWN','cokey','Comp % - Representative Value','mukey']]
cokey_det=cokey_det.drop_duplicates()
weighted_ksat1 = pd.merge(weighted_ksat0, cokey_det, on=['mukey', 'WUWN','cokey'], how='left')
weighted_ksat1.rename(columns={0: 'Ksat-W_Av-thickness'}, inplace=True)
##HYDRAULIC CONDUCTIVITY: WEIGHTED AVERAGES BASED ON THE REPRESENTATIVE VALUE OF THE COMPONENT PERCENTAGE 
weighted_ksat = (weighted_ksat1['Ksat-W_Av-thickness'] * weighted_ksat1['Comp % - Representative Value']).groupby([weighted_ksat1['mukey'], weighted_ksat1['WUWN']]).sum() / weighted_ksat1.groupby(['mukey', 'WUWN'])['Comp % - Representative Value'].sum()

##SAME FOR CLAY CONTENT AND ORGANIC MATTER (IN PERCENTAGE)
filtered_rows = filtered_rows[filtered_rows['Total Clay - Representative Value'].notna()]
weighted_clay0 = (filtered_rows['Total Clay - Representative Value'] * filtered_rows['Thickness']).groupby([filtered_rows['mukey'], filtered_rows['WUWN'], filtered_rows['cokey']]).sum() / filtered_rows.groupby(['mukey', 'WUWN','cokey'])['Thickness'].sum()
weighted_clay0=weighted_clay0.reset_index()
cokey_det=filtered_rows[['WUWN','cokey','Comp % - Representative Value','mukey']]
cokey_det=cokey_det.drop_duplicates()
weighted_clay1 = pd.merge(weighted_clay0, cokey_det, on=['mukey', 'WUWN','cokey'], how='left')
weighted_clay1.rename(columns={0: 'Clay-W_Av-thickness'}, inplace=True)
weighted_clay = (weighted_clay1['Clay-W_Av-thickness'] * weighted_clay1['Comp % - Representative Value']).groupby([weighted_clay1['mukey'], weighted_clay1['WUWN']]).sum() / weighted_clay1.groupby(['mukey', 'WUWN'])['Comp % - Representative Value'].sum()
filtered_rows = filtered_rows[filtered_rows['OM - Representative Value'].notna()]
weighted_OM0 = (filtered_rows['OM - Representative Value'] * filtered_rows['Thickness']).groupby([filtered_rows['mukey'], filtered_rows['WUWN'], filtered_rows['cokey']]).sum() / filtered_rows.groupby(['mukey', 'WUWN','cokey'])['Thickness'].sum()
weighted_OM0=weighted_OM0.reset_index()
cokey_det=filtered_rows[['WUWN','cokey','Comp % - Representative Value','mukey']]
cokey_det=cokey_det.drop_duplicates()
weighted_OM1 = pd.merge(weighted_OM0, cokey_det, on=['mukey', 'WUWN','cokey'], how='left')
weighted_OM1.rename(columns={0: 'OM-W_Av-thickness'}, inplace=True)
weighted_OM = (weighted_OM1['OM-W_Av-thickness'] * weighted_OM1['Comp % - Representative Value']).groupby([weighted_OM1['mukey'], weighted_OM1['WUWN']]).sum() / weighted_OM1.groupby(['mukey', 'WUWN'])['Comp % - Representative Value'].sum()

##SAVE FINAL FILE
summary = df_all2[['FID', 'mukey', 'WUWN']].drop_duplicates()
summary['ksat_weight_av'] = summary.set_index(['mukey', 'WUWN']).index.map(weighted_ksat.get)
summary['clay_weight_av'] = summary.set_index(['mukey', 'WUWN']).index.map(weighted_clay.get)
summary['OM_weight_av'] = summary.set_index(['mukey', 'WUWN']).index.map(weighted_OM.get)
soil_acres=df_all.drop_duplicates(subset=['WUWN', 'mukey', 'Soil_acres'])
soil_acres=soil_acres[['FID','Soil_acres']]
summary2=pd.merge(summary,soil_acres, on='FID', how='left')
summary2.to_csv(r'SSURGO_CALCS.csv', index = False)
