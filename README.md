# gsodparser
A collection of tools to download, repack and load into Pandas the NOAA Global 
Surface Summary of the Day (GSOD) weather dataset.

Be careful, this package is still in alpha version! All the functions and 
classes work, but there is some manual work to do to prepare the data and set 
paths in the python scripts.

For more info on GSOD:
https://data.noaa.gov/dataset/dataset/global-surface-summary-of-the-day-gsod
ftp://ftp.ncdc.noaa.gov/pub/data/gsod/

## Installation
1. clone or download the git repository: https://github.com/mvonlanthen/gsodparser
2. If not already done, download and repack the GSOD dataset into csv with the 
   following python scripts:
   * download_gsod_dataset.py
   * repack_gsod_dataset.py

## Examples
* Load the module in your python script or Jupyter Notebook:
```python
import sys
sys.path.append(r'/path/to/gsodparser')
import gsodparser as gp
```

### work without the parser object with functions
* Load the station metadata
dfMeta = gp.loadMetadata(filename,sep=',')

* Load country list
```python
dfCtry = gp.loadCountryList(filename)
```

* Load a year of data
```python
dfData = gp.loadGsod_csv(filename,sep=';')
```

### work with the parser object
* Create the parser object
gp = gsodparser.GsodParser(gsodDir=r'path/to/folder/with/gsod_{year}.csv')

* load a full year into a Pandas DataFrame, without replacing the NULL value 
  without something more sensible and without adding a DATE column with the 
  proper python dates (raw loading).
```python
gsodData = gp.loadYear_raw(year=2017)
```

* Same as before, but replacing the NULLs with NaNs and adding a "DATE" columns
```python
gsodData = gp.loadYear(year=2017)
```

* load the station metadata
```python
gsodMeta = gp.loadMetadata()
```

* load the country list
```python
gsodCtry = gp.loadCountryList()
```

* Load all: country list, metadata and one year
```python
gsodCtry,gsodMeta,gsodData = gp.loadAll(year=2017)
```
* Print info about the gp object
```python
print(gp)
```
* Add a DATE column and clean the NULL values. For some column, the NULL are
  9999.9 or 99.9. Those get replaced by NaNs.
```python
gsodData = gsodparser.addDate(gsodData)
gsodData = gsodparser.repaceNULLs(gsodData)
```