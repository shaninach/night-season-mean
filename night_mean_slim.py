
# this code analyzes and plots a mean of certain night measurements from the seeing monitor
# need to define the seeing measurements file (datafile), and the wanted start and end date (start,end) 

import numpy as np
import matplotlib.pyplot as plt 
import matplotlib as mp 
import os
import pandas as pd
import datetime as dt
import math 

############################## fill in ######################################
path = r"D:\Master\fig_sum"
os.chdir(path)
datafile = 'Seeing_Data.txt'
site = 'Neot_Smadar'
start = pd.to_datetime('2021-03-16 19:30:00', format = '%Y-%m-%d %H:%M:%S')
end = pd.to_datetime('2021-05-11 05:00:00',format = '%Y-%m-%d %H:%M:%S') 

############################## functions ####################################

def data(datafile):
    file = open(datafile, "r")
    data = []
    for line in file:               # converts the data .txt file to a list of lists 
        file = open(datafile, "r")
        stripped_line = line. strip()
        line_list = stripped_line. split()
        data.append(line_list)
        file.close() 
    
    Date = []
    LST = []
    Seeing = []
    row = 0
    while row < len(data):             # extract values of Date, Hour (LST) and seeing from data - to new lists each.
        Date.append(data[row][0])
        LST.append(data[row][4])
        Seeing.append(float(data[row][10]))
        row += 1
    d = {'Date': Date, 'LST': LST, 'seeing': Seeing}
    df = pd.DataFrame(data =d)
    time = pd.to_datetime(df['Date'] + ' ' + df['LST'],format = '%d/%m/%Y %H:%M:%S')
    df = pd.DataFrame({'time': time, 'seeing': df.seeing})
    return df 

def table(daf,first,last):
    """ daf = table with seeing values per date and hour with Date column,
    first = index of wanted date to begin with, 
    last = index of wanted date to finish with"""
    t = {}
    for date in daf.groupby(daf['date']).mean().index[first:last]:   # for date in lists of observation dates
        mask = (daf['time'] >= pd.to_datetime([str(date) + ' '+ '18:00'],format = '%Y-%m-%d %H:%M')[0]) & (df['time'] <= pd.to_datetime([str(date+pd.to_timedelta(1,unit='D')) + ' '+ '06:00'],format = '%Y-%m-%d %H:%M')[0]) 
        t[date] = daf.loc[mask].rename(columns= {'seeing': str(date)})
        t[date] = t[date].set_index(pd.to_datetime(t[date].time))
        t[date] = t[date].resample('5T').median().dropna()
        t[date] = t[date].resample('10T').median().dropna()
        t[date] = t[date].resample('20T').median().dropna()
        t[date] = t[date].resample('30T').median().dropna()
        t[date]['time'] = pd.to_datetime(t[date].index)
        t[date] = t[date].set_index(t[date].time.dt.time)
        t[date] = t[date].drop('time',1)

    tkeys = list(t.keys())
    tab = t[tkeys[0]]
    for key in tkeys[1:]:
        tab = pd.merge(tab, t[key], on='time', how='outer')

    tab = tab.reset_index()
    tab = tab.sort_values('time')
    tab = tab.reset_index(drop= True)
    
    # sorting the hours properly (to begin with 18:00 and finish with 05:30)
    first_hour = tab[tab['time'] >= dt.time(18,0)].index[0]
    new = pd.concat([tab.iloc[first_hour:],tab.iloc[:first_hour]])
    
    new = new.reset_index(drop=True)
    new['mean'] = new.mean(axis=1)
    new['std'] = new.std(axis=1)
    midnight = new[new['time'] == dt.time(0,0)].index[0]
    

    new = new.assign(fake = new.index) # add new column, with indices of new. 
    for i in list(range(len(new))):    # replace each value with a fake date and real time - where from midnight the date would be +1 
        if i <= midnight-1:
            new['fake'] = new['fake'].replace(i,pd.to_datetime('2000-10-01' + ' ' +str(new.time[i])) )
        else:
            new['fake'] = new['fake'].replace(i,pd.to_datetime('2000-10-02' + ' ' +str(new.time[i])) )
    
    return new

################################# main ######################################

df = data(datafile)
df['time'] = pd.to_datetime(df.time)
daf = df.copy()
daf['date'] = daf.time.dt.date

[starti, finishi] = [0,len(daf.groupby(daf['date']).mean().index)-1]  # for all the data 
#[starti, finishi] = [15,40] # for specific range of dates

new = table(daf,starti,finishi).dropna(1,how='all')
[start, finish] = [pd.to_datetime(new.columns[1]), pd.to_datetime(new.columns[len(new.columns)-4])] # give the dates chosen 


#scatter plot - median:
fig, ax = plt.subplots()
X = mp.dates.date2num(new['fake'])
Y = list(new['mean'])
xformatter = mp.dates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(xformatter)
ax.xaxis.set_major_locator(mp.dates.HourLocator(interval = 2))
plt.errorbar(X,Y, fmt='og',markersize = 4,yerr= new['std'], elinewidth=1, ecolor = 'olive', capsize = 3.0)
plt.yticks(np.arange(math.floor(min(Y))-1, math.ceil(max(Y))+3, step = 1), fontsize = 10)
plt.title('median of ' + str(len(new.columns)) + ' nights between '+start.strftime("%d/%m/%y")+' and '+finish.strftime('%d/%m/%y'))
plt.ylabel('seeing (arcsec)', fontsize = 12)
plt.xlabel('time of measurement',fontsize = 12)
figname = 'new median night.pdf'    
fig.tight_layout
plt.savefig(figname) 


# scatter plot - seasonality median:   
minv = new.min()
minv = minv.drop(['mean','std','fake','time'])
minv.index = pd.to_datetime(minv.index)
minv = minv.astype(float)
minvmean = minv.groupby(by=minv.index.month).mean()
minvstd = minv.groupby(by=minv.index.month).std()
minvmean.index = minvmean.index.astype(str)

fig, ax = plt.subplots()
plt.figure(figsize=(5,3)) 
X = minvmean.index
Y = list(minvmean)
plt.errorbar(X,Y, fmt='og',markersize = 4,yerr= list(minvstd), elinewidth=1, ecolor = 'olive', capsize = 3.0)
plt.yticks(np.arange(math.floor(min(Y))-1, math.ceil(max(Y))+4, step = 1), fontsize = 10)
ttl = 'minimum of ' + str(len(new.columns)) + ' nights between '+start.strftime("%d/%m/%y")+' and '+finish.strftime('%d/%m/%y')
plt.title(ttl,pad=20)
plt.ylabel('seeing (arcsec)', fontsize = 12)
plt.xlabel('month', fontsize = 12)

figname = 'new seasonality.pdf'  
#fig.tight_layout()
plt.savefig(figname, bbox_inches = "tight") 

    