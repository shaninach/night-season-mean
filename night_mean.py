# instructions: 
# first run with first green section """ """, 
# then unable it and keep changing the dates and running. 
# in the end plot using the second green section in bottom part 

# add  sigma cliiping!!!
# add std bars to final plot!!!

# code to analyze and plot a night measurements from cyclope 
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib as mp 
import os
import pandas as pd
import datetime as dt
import math
from scipy import stats as st

############################## fill in ######################################
path = r"D:\Master\fig_sum"
os.chdir(path)
datafile = 'Seeing_Data.txt'
site = 'Neot_Smadar'
start = pd.to_datetime('2020-08-18 20:00:00')
end = pd.to_datetime('2020-08-21 05:00:00') 


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
    r0 = []
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

def splicing (df,start,end):
    """ input: datafile = .txt file of seeing data ("Seeing_Data.txt"), 
    start, end = date and time of first and last measuremnts wanted, in form dd-mm-yy HH:MM:SS'
    site = observation site. no spaces
        output: spliced table of cyclope data, of the night between start_time and end_time"""
    
    for i in list(range(0,len(df))):
        if df.time.iloc[i].hour == 0:            # fix date for hour 00:-- and 01:--
            df.time.iloc[i] += dt.timedelta(days=1)
        elif df.time.iloc[i].hour == 1:
            df.time.iloc[i] += dt.timedelta(days=1)

    mask1 = (df['time'] > start) & (df['time'] <= end) 
    df = df.loc[mask1]
    return df

def fig(rel,start,end):
    datestr = str(start.day) + '.' + str(start.month) + '.' + str(start.year)
    datestr2 = str(end.day) + '.' + str(end.month) + '.' + str(end.year)
    tit = site+ ' ' + datestr + '-' + datestr2
    Y = rel.seeing
    multi = 3 # multiplication of sigma 
    clipsee,low,high = st.sigmaclip(rel.seeing,multi,multi) # sigma clipping - 
    per = 100 - len(clipsee)/len(Y)*100 # must be positioned befor the loops that changes rel
    maxs = max(clipsee)
    mins = min(clipsee)
    medians = np.median(clipsee)
    N = len(clipsee)
    means = np.mean(clipsee)
    
    for n in list(range(len(clipsee))):   # clip rel datframe by the sigma clipping results
        while clipsee[n] != rel.seeing[n]:
            rel = rel.drop(rel.index[n])   
        
    if len(rel.seeing) != len(clipsee):     # this is to make sure any excess values are cropped 
        rel = rel.drop(rel.index[len(clipsee):])
  
    fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]})
    fig.suptitle(tit, fontsize=9)
    #scatter plot: 
    X = mp.dates.date2num(rel.time)
    xformatter = mp.dates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_formatter(xformatter)
    ax1.scatter(X,clipsee, c= 'olive', marker = '.', s = 2.5)
    ax1.set_ylabel('Seeing (arcsec)', fontsize = 9)
    ax1.set_xlabel('Time', fontsize =9)
    plt.sca(ax1)
    plt.yticks(np.arange(math.floor(min(clipsee)), math.ceil(max(clipsee))+1, step = 1), fontsize = 8)
    plt.xticks(fontsize = 8)

    textstr = r"max%.1f, min%.1f, median%.1f, mean%.1f, N%.0f, clipped%.0fs, %.0f%%" % (maxs,mins,medians,means,N,multi,per)
    props = dict(boxstyle='round', facecolor='white', alpha=0)
    ax1.text(0.132,0.14, textstr, fontsize=7.5, transform=plt.gcf().transFigure, bbox=props)
    
    #hist:
    ax2.hist(Y, bins = 5, color = 'olive', ec = 'darkolivegreen')
    ax2.set_ylabel('N measurements', fontsize = 9)
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()
    ax2.set_xlabel('Seeing (arcsec)', fontsize =9)
    plt.sca(ax2)
    plt.xticks(np.arange(math.floor(min(Y)), max(Y)+1, step = 2),fontsize = 8)
    plt.yticks(fontsize = 8)
    figname = 'fig '+site+'_'+datestr+'.pdf'    
    fig.tight_layout
    plt.savefig(figname) 
    return fig 


################################# main ###################################

df = data(datafile)
rel = splicing(df.copy(),start,end)
rel = rel.set_index(rel.time)

av_5 = rel.resample('5T').mean()
start = av_5.resample('10T').mean().dropna()
av[str(start)[0:10]] = av.resample('30T').mean().dropna()
av['time'] = av.index
av['time'] = av.time.dt.time


# table = pd.DataFrame({str(start)[0:10]+'seeing': av.seeing})
# table = table.reset_index()
# table[str(start)[0:10]+'time'] = av.time
# table[str(start)[0:10]+' see'] = av.seeing

# table = table.append(av.seeing)

#frames = []
#table = pd.concat(frames)

for df:    
st = df['time'][0]
 mask1 = (df['time'] > st) & (df['time'] <= end) 
    df = df.loc[mask1]
    return df

# present date
print(df.time[0].dt.date)
# date after 1 day
print(st+pd.to_timedelta(1,unit='D'))

pd.date_range(start='24/4/2020', end='24/5/2020', freq='D')



new = rel.groupby(rel['time'], axis = 1).all()


df_mean = df.set_index(df.time)
df_mean = df_mean.drop('time',1)
df_mean = df_mean.resample('5T').mean()
df_mean = df_mean.resample('10T').mean().dropna()
df_mean = df_mean.resample('30T').mean().dropna()
av['time'] = av.index
av['time'] = av.time.dt.time

"""
if len(av.seeing) == 17:
    table[str(start)[0:10]+'seeing'] = list(av.seeing)

tab = table.drop('time',1)
tab['mean'] = tab.mean(axis = 1)
tab['std'] = tab.std(axis=1)

fig, ax = plt.subplots(1, 1)
X = mp.dates.date2num(table.time)
Y = tab['mean']
std = list(tab['std'])
xformatter = mp.dates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(xformatter)
ax.errorbar(X,Y, yerr=std, ecolor = 'olive', capsize = 3.0, elinewidth = 1.0, marker = 'o', linewidth = 0.0)
plt.yticks(np.arange(math.floor(min(Y))-1, math.ceil(max(Y))+2, step = 1), fontsize = 8)


"""
