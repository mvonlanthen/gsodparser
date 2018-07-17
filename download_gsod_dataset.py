# -*- coding: utf-8 -*-
'''
Download the Global Surface Summary of the Day (GSOD) dataset. Check the 
following links for more data:

https://data.noaa.gov/dataset/dataset/global-surface-summary-of-the-day-gsod
ftp://ftp.ncdc.noaa.gov/pub/data/gsod/
'''
# import modules
import os
import ftplib      

# parameters
ftpAddress = r'ftp.ncdc.noaa.gov'
ftpDir  = r'/pub/data/gsod'
outputDir = r'C:\Users\marcel\Downloads\gsod'
startYear = 1901
endYear = 2018

# try to connect to the server      
print('Starting connection to NOAA database')
try:
    ftp = ftplib.FTP(ftpAddress) 
    ftp.login()
    print('Connect successful')
except:
    raise ConnectionError('Can not connect to "{}"'.format(ftpAddress))

# loop through all the folders and download ONLY the gsod_*year*.tar! It 
# contains all the other little files in the year folder
errorYears = list()
for year in range(startYear,endYear+1):
    ftpDirYear = ftpDir+r'/'+str(year)
    ftpFile = r'gsod_{}.tar'.format(year)
    ftpPath = ftpDirYear+r'/'+ftpFile
    localPath = os.path.join(outputDir,ftpFile)
    # if localPath already exist, skip. It means it has already been 
    # downloaded, for example during a previous run
    if os.path.isfile(localPath):
        print('Target file "{}" already exist. Skip'.format(localPath))
        continue
    print('Downloading "{}"'.format(ftpPath))
    try: 
        file = open(localPath,'wb')
        ftp.cwd(ftpDirYear)
        ftp.retrbinary('RETR {}'.format(ftpFile),file.write)
        file.close()
        print('Successful download of "{}"'.format(ftpPath))
    except:
        file.close()
        os.remove(localPath)
        errorYears.append(year)
        print('Error: fail to download "{}"'.format(ftpPath))
    finally:
        file.close()
        
# all done...
with open(os.path.join(outputDir,'errorYears.txt'),'w') as f:
    f.write(str(errorYears))
print('All files downloaded')
print('Closing connection')
ftp.close()