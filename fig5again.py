import pandas as pd
import matplotlib.pyplot as plot

df = pd.read_csv("2022_PM25.csv.org", sep=';',header=9,engine='python');
#global replace: U+03BC is the unicode hex value of the character Greek Small Letter Mu.
df['Eenheid']='ug/m3'

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

#https://stackoverflow.com/questions/16459217/in-pandas-how-can-i-get-a-dataframe-as-the-output-while-i-sum-the-dataframe
a = df.mean()
mean = list(a)
values = list(a.index)
Series_Dict = {"station":values, "jaargemiddelde":mean}
df_mean = pd.DataFrame(Series_Dict)
print(df_mean)

#haal de dag uit kolom Begindatumtijd
new = df[" Begindatumtijd"].str.split(" ", n = 1, expand = True)
df["dag"]= new[0]
df['dag'] = pd.to_datetime(df.dag, format='%Y%m%d')
df = df.set_index(['dag'])

del(df["Component"]) 
del(df["Bep.periode"]) 
del(df["Eenheid"])
del(df[" Begindatumtijd"])
del(df["Einddatumtijd"])


df_resampled = df.resample('d').mean()
print(df_resampled)

#als meer dan hardgecodeerde limiet van 25, dan noemen we het overschrijdingsdag 
#bij een overschrijdingsdag noteren we een 1 
#bij een niet overschrijdingsdag noteren we een 0
for col in df_resampled.columns:
    df_resampled[col]=df_resampled[col].apply(lambda x: 1 if x > 25 else 0)

print(df_resampled)

a = df_resampled.sum()
sum = list(a)
values = list(a.index)
Series_Dict = {"station":values, "aantalteveel":sum}
df_teveel = pd.DataFrame(Series_Dict)
print(df_teveel)

df_all = pd.merge(df_mean, df_teveel, on='station', how='inner')
print(df_all)

#https://stackoverflow.com/questions/14432557/scatter-plot-with-different-text-at-each-data-point
import plotly.express as px
title_text='2022 NL stations PM2.5 limiet 25ug/m3 '
fig = px.scatter(df_all, x="jaargemiddelde", y="aantalteveel", text="station", log_x=True, size_max=100, color="jaargemiddelde")
fig.update_traces(textposition='top center')
fig.update_layout(title_text=title_text, title_x=0.5)
fig.show()


fig, ax = plot.subplots()
from scipy.optimize import curve_fit
import numpy as np


def func(x, a, b):
    return a * x  + b



x=df_all['jaargemiddelde']
y=df_all['aantalteveel']

popt, pcov = curve_fit(func, x, y)
perr = np.sqrt(np.diag(pcov))

print("fit parameter 1-sigma error")
print()
textstr = "fit op ax+b, met +/- "+'$\sigma$' +"\n\n"
for i in range(len(popt)):
    print(i,str(popt[i])+" +- "+str(perr[i]))
    if (i==0):
        textstr=textstr+"a="+str(round(popt[i],4))+"  +/-  " +str(round(perr[i],4))
        a=popt[i]
    if (i==1):
        textstr=textstr+"\nb="+str(round(popt[i],4))+"  +/-  " +str(round(perr[i],4))
        b=popt[i]

fit = func(x, *popt)

mse= np.sum( (y-fit)**2)
mse = mse / (len(fit)-2)
mse = np.sqrt(mse)
textstr=textstr+ "\n\nnrpoints=" + str(len(fit))
textstr=textstr+" \nmse="+str(round(mse,1))

corr_matrix = np.corrcoef(y, fit)
corr = corr_matrix[0,1]
R_sq = corr**2
textstr=textstr+" \nR$^2$="+str(round(R_sq,2))
print(textstr)


ax.scatter(df_all.jaargemiddelde, df_all.aantalteveel,zorder=1,alpha = 0.45, s=200,c='b')
ax.plot(x, fit, "r", lw=2, label="LeastSquares fit")

plot.title(title_text)
ax.set(xlabel='jaargemiddelde pm25 $\mu gram/m^3$ ', ylabel='aantal daggemiddelde overschrijdingen' )
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
# place a text box in upper left in axes coords
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)


plot.show()

