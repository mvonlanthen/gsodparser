# -*- coding: utf-8 -*-
'''
gsodparser.py
--------------

Collection of tools (just one so far...) to parse the Global Surface Summary 
of the Day (GSOD) dataset.

For more info on GSOD:
https://data.noaa.gov/dataset/dataset/global-surface-summary-of-the-day-gsod
ftp://ftp.ncdc.noaa.gov/pub/data/gsod/

Installation
------------
1. Copy the directory gsodparser to "/path/to/gsodparser"
2. done...

Examples
--------
# Load the module in your python script or Jupyter Notebook:
import sys
sys.path.append(r'/path/to/gsodparser')
from gsodparser import gsodparser

# Create the parser object
gp = gsodparser.GsodParser(gsodDir=r'path/to/folder/with/gsod_{year}.csv')

# load a full year into a Pandas DataFrame, without replacing the NULL value 
#  without something more sensible and without adding a DATE column with the 
#  proper python dates (raw loading).
gsodData = gp.loadYear_raw(year=2017)

# same as before, but replacing the NULLs with NaNs and adding a "DATE" columns
gsodData = gp.loadYear(year=2017)

# load the station metadata
gsodMeta = gp.loadMetadata()

# load the country list
gsodCtry = gp.loadCountryList()

# Load all: country list, metadata and one year
gsodCtry,gsodMeta,gsodData = gp.loadAll(year=2017)

# Print info about the gp object
print(gp)
 
# Add a DATE column and clean the NULL values. For some column, the NULL are 
# 9999.9 or 99.9. Those get replaced by NaNs. 
gsodData = gsodparser.addDate(gsodData)
gsodData = gsodparser.repaceNULLs(gsodData)
'''

# Load Modules
import os
import numpy as np
import pandas as pd

# Data definition according the GSOD packager. You can find this information 
# in the file "GSOD_DESC.txt"
#                'varName': [startIdx,endIdx,type,NULL]
dataDefinition = {'STN':     [0,   6,   'int',None],
                 'WBAN':     [7,   12,  'int',None],
                 'YEAR':     [14,  18,  'int',None],
                 'MO':       [18,  20,  'int',None],
                 'DA':       [20,  22,  'int',None],
                 'TEMP':     [24,  30,  'real',9999.9],
                 'TEMPcnt':  [31,  33,  'int',None],
                 'DEWP':     [35,  41,  'real',9999.9],
                 'DEWPcnt':  [42,  44,  'int',None],
                 'SLP':      [46,  52,  'real',9999.9],
                 'SLPcnt':   [53,  55,  'int',None],
                 'STP':      [57,  63,  'real',9999.9],
                 'STPcnt':   [64,  66,  'int',None],
                 'VISIB':    [68,  73,  'real',    999.9],
                 'VISIBcnt': [74,  76,  'int',     None],
                 'WDSP':     [78,  83,  'real',    999.9],
                 'WDSPcnt':  [84,  86,  'int',     None],
                 'MXSPD':    [88,  93,  'real',    999.9],
                 'GUST':     [95,  100, 'real',    999.9],
                 'MAX':      [102, 108, 'real',    9999.9],
                 'MAXflag':  [108, 109, 'starFlag',None],
                 'MIN':      [110, 116, 'real',    9999.9],
                 'MINflag':  [116, 117, 'starFlag',None],
                 'PRCP':     [118, 123, 'real',    99.99],
                 'PRCPflag': [123, 124, 'char',    None],
                 'SNDP':     [125, 130, 'real',    999.9],
                 'FRSHTT':   [132, 138, 'char',    None]}

        
# Functions
def loadMetadata(filename,sep=','):
    return pd.read_csv(filename,dtype={'USAF':'str','WBAN':'str'},sep=sep)


def loadCountryList(filename,sep=';'):
    return pd.read_csv(filename,sep=sep)  
        
        
def loadRawGsod_csv(filename,sep=';'):
    '''
    Load the raw data of "year". No processing of the NULL or of the 
    dates, just the raw data from the csv-files.
    '''
    return pd.read_csv(filename,
                       sep=sep,
                       dtype={'STN':'str',
                              'WBAN':'str',
                              'MAXflag':'str',
                              'MINflag':'str',
                              'PRCPflag':'str',
                              'FRSHTT':'str'})
    

def loadGsod_csv(filename,sep=';'):
    '''
    Load the raw data of "year", replace the NULL values (e.g. 9999.9) by 
    NaNs and add a column "DATE".
    '''
    gsodData = loadRawGsod_csv(filename,sep=sep)
    gsodData = replaceNULLs(gsodData)
    gsodData = addDate(gsodData)
    return gsodData


def replaceNULLs(gsodData):
    for col in gsodData.columns:
        if col in ['STN','WBAN','MAXflag','MINflag','PRCPflag','FRSHTT']:
            continue  # skip the strings. An empty string is valid
        if col in dataDefinition.keys():
            # change the NULL=9999.9 to np.nan
            if col in ['TEMP','DEWP','SLP','STP','MAX','MIN']: 
                bidx = gsodData[col]>9999.8  #handle rounding
                gsodData.loc[bidx,col] = np.nan
            # change the NULL=999.9 to np.nan
            if col in ['VISIB','WDSP','MXSPD','GUST','SNDP']: 
                bidx = gsodData[col]>999.8  #handle rounding
                gsodData.loc[bidx,col] = np.nan
            # change the NULL=99.9 to np.nan
            if col in ['PRCP']: 
                bidx = gsodData[col]>99.8  #handle rounding
                gsodData.loc[bidx,col] = np.nan
    return gsodData


def addDate(gsodData):
    df = pd.DataFrame({'year':gsodData['YEAR'],'month':gsodData['MO'],'day':gsodData['DA']})
    df = pd.to_datetime(df).rename('DATE')
    return pd.concat([df,gsodData], axis=1)


def saveDataToCsv(gsodData,filename,sep=';',cleanColumns=True):
    '''
    Save a Pandas Dataframe with GSOD data (not the metadata or the country 
    list!) to a CSV, while cleaning the extra-columns which are not in the 
    original GSOD dataset.
    '''
    colToDrop = list()
    for col in gsodData.columns:
        if col not in list(dataDefinition.keys()):
            colToDrop.append(col)
    gsodData.drop(colToDrop,axis=1).to_csv(filename,sep=sep,index=False)


# Calss Definition
class GsodParser(object):
    '''
    A "praser" to read the GSOD csv-files after they have been downloaded with 
    "download_gsod_dataset.py" and repacked with "repack_gsod_dataset.py".
    '''
    # constructors
    def __init__(self,gsodDir,fileType='csv',filenameFormat=r'gsod_{year}'):
        '''
        Constructor
        
        Arguments
        ---------
        gsodDir: string
            location of the dataset, which is composed of csv-files, such as 
            "gsod_2017.csv" or "isd-history.csv" (the metadata).
        '''
        # set class variables
        self.gsodDir = None
        if os.path.isdir(gsodDir):
            self.gsodDir = gsodDir
        else:
            raise IOError('gsodDir "{}" does not exist'.format(gsodDir))
        self.fileType = fileType
        self.filenameFormat = filenameFormat
        
        # set derived variables
        self.metaFilename = 'isd-history.'+self.fileType
        if os.path.isfile(os.path.join(self.gsodDir,self.metaFilename))==False:
            raise IOError(
                'Metadata file "{}" not present in "{}"'.format(self.metaFilename,self.gsodDir)
            )
        self.countryFilename = r'country-list.'+self.fileType
        if os.path.isfile(os.path.join(self.gsodDir,self.countryFilename))==False:
            raise IOError(
                'Country file "{}" not present in "{}"'.format(self.countryFilename,self.gsodDir)
            )
        
      
    # class methods 
    def loadMetadata(self):
        filePath = os.path.join(self.gsodDir,self.metaFilename)
        return loadMetadata(filePath)

        
    def loadCountryList(self):
        filePath = os.path.join(self.gsodDir,self.countryFilename)
        return loadCountryList(filePath,sep=';')

        
        
    def loadYear_raw(self,year,sep=';'):
        '''
        Load the raw data of "year". No processing of the NULL or of the 
        dates, just the raw data from the csv-files.
        '''
        filename = self.filenameFormat.format(year=year)+'.'+self.fileType
        filePath = os.path.join(self.gsodDir,filename)
        return loadRawGsod_csv(filePath,sep=sep)
    
    
    def loadYear(self,year,sep=';'):
        '''
        Load the raw data of "year", replace the NULL values (e.g. 9999.9) by 
        NaNs and add a column "DATE".
        '''
        gsodData = self.loadYear_raw(year,sep=sep)
        gsodData = replaceNULLs(gsodData)
        gsodData = addDate(gsodData)
        return gsodData
    
    
    def loadAll(self,year,sep=';'):
        '''
        Load the country list, the station metadata and one year (cleaned). 
        For more info, see methods:
            * loadCountryList
            * loadMetadata
            * loadYear
        '''
        gsodCtry = self.loadCountryList()
        gsodMeta = self.loadMetadata()
        gsodData = self.loadYear(year,sep=sep)
        return gsodCtry,gsodMeta,gsodData
    
    # getters
    def get_availableDataFile(self):
        idx = self.filenameFormat.find('{year}')
        fStart = self.filenameFormat[:idx]
        fEnd = self.filenameFormat[idx+6:]+'.'+self.fileType
        files = list()
        for file in os.listdir(self.gsodDir):
            if os.path.isfile(files):
                if file.startswith(fStart) and file.endswith(fEnd):
                    files.append(file)
        return files

    
    # special functions
    def __str__(self):
        objStr =  'Object variables\n'
        objStr += '----------------\n'
        objStr += 'gsod directory: {}\n'.format(self.gsodDir)
        objStr += 'gsod file format: {}\n'.format(self.fileType)
        objStr += 'gsod metadata file: {}\n'.format(self.metaFilename)
        return objStr             