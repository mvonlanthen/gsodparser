# -*- coding: utf-8 -*-
'''
Prepare gsod dataset
'''
#%% import modules
import os
import shutil
import tarfile
import gzip

#%% parameters
gsodDir = r'C:\Users\marcel\Downloads\gsod' #folder used as output by the script "download_gsod_dataset.py"

#%% Function and file format
# location (first and last character) for each entries in op-file. In the op-file, 
# each column is always located at the same position. Hence reading the data is 
# only about counting
#     key: [start char, end char, dat type, missing val]  (real=python float,char=python string)
opFile_datLoc = {'STN': [0, 6, 'int',None],
                 'WBAN': [7, 12, 'int',None],
                 'YEAR': [14, 18, 'int',None],
                 'MO': [18, 20, 'int',None],
                 'DA':[20,22,'int',None],
                 'TEMP': [24, 30, 'real',9999.9],
                 'TEMPcnt': [31, 33, 'int',None],
                 'DEWP': [35, 41, 'real',9999.9],
                 'DEWPcnt': [42, 44, 'int',None],
                 'SLP': [46, 52, 'real',9999.9],
                 'SLPcnt': [53, 55, 'int',None],
                 'STP': [57, 63, 'real',9999.9],
                 'STPcnt': [64, 66, 'int',None],
                 'VISIB': [68, 73, 'real',999.9],
                 'VISIBcnt': [74, 76, 'int',None],
                 'WDSP': [78, 83, 'real',999.9],
                 'WDSPcnt': [84, 86, 'int',None],
                 'MXSPD': [88, 93, 'real',999.9],
                 'GUST': [95, 100, 'real',999.9],
                 'MAX': [102, 108, 'real',9999.9],
                 'MAXflag': [108, 109, 'starFlag',None],
                 'MIN': [110, 116, 'real',9999.9],
                 'MINflag': [116, 117, 'starFlag',None],
                 'PRCP': [118, 123, 'real',99.99],
                 'PRCPflag': [123, 124, 'char',None],
                 'SNDP': [125, 130, 'real',999.9],
                 'FRSHTT': [132, 138, 'char',None]}

# column order. Be carful, len(colOrder) MUST be equal to 
# len(list(opFile_datLoc.keys()))!
colOrder = ['STN','WBAN','YEAR','MO','DA','TEMP','TEMPcnt','DEWP','DEWPcnt',
            'SLP','SLPcnt','STP','STPcnt','VISIB','VISIBcnt','WDSP','WDSPcnt',
            'MXSPD','GUST','MAX','MAXflag','MIN','MINflag','PRCP','PRCPflag','SNDP','FRSHTT']



def processTarYear(gsodDir,tarYearFile,colOrder,opFile_datLoc):
    # unpack the tar. Packed in the tar, a LOT of op-files, a wierd csv, but 
    # without separation...
    tarSource = os.path.join(gsodDir,tarYearFile)
    print('processing tarfile "{}"'.format(tarSource))
    tarTarget = os.path.join(gsodDir,tarYearFile[:-4])
    csvOutPath = os.path.join(gsodDir,tarYearFile[:-4]+'.csv')
    if os.path.isfile(csvOutPath):
        print('Output csv "{}" already exist. Skip this tar'.format(csvOutPath))
        return 0
    tar = tarfile.open(tarSource,'r')
    tar.extractall(tarTarget)
    tar.close()
    
    # read and process each op-file and appends its content in the csv-file
    with open(csvOutPath,'w') as fo:
        # write header
        fo.write(';'.join(colOrder)+'\n')
        gcFiles = os.listdir(tarTarget)
        for gcFile in gcFiles:
            # let's assume there is only gc-files in the a tar (should be true). 
            # This will save us the costly "if" check...
            lines = None
            with gzip.open(os.path.join(tarTarget,gcFile), mode='r') as gc:
                lines = gc.read().splitlines()
            lines.pop(0)     #remove header line
            for line in lines:
                opLine = list()
                for k in colOrder:
                    v = opFile_datLoc[k]
                    dat = line[v[0]:v[1]]
                    if type(dat)==str:
                        opLine.append(dat.strip())
                    elif type(dat)==bytes:
                        opLine.append(dat.decode('utf-8').strip())
                    else:
                        raise TypeError('Error: data format not recognized!')
                fo.write(';'.join(opLine)+'\n')
    shutil.rmtree(tarTarget)
    print('done processing tarfile "{}"'.format(tarSource))
    return 0


#%% list all files  finishing by .tar and starting by gsod_ in gsodDir
gsodFiles = list()
gsodPath = list()
for file in os.listdir(gsodDir):
    if file.endswith('.tar') and file.startswith('gsod_'):
        gsodFiles.append(file)
        gsodPath.append(os.path.join(gsodDir,file))
        
  
#%% process all the tar-file
# this for loop could be done in parallel with a map_async function. 
# Nevertheless, the processing is mainly I/O operations, therefore the 
# bottleneck is the data storage. I don't think there will be a important 
# gain with parallelisation
for gsodFile in gsodFiles:
    status = processTarYear(gsodDir,gsodFile,colOrder,opFile_datLoc) 


