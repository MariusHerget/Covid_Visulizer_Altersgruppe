import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from collections import OrderedDict
plt.style.use('seaborn')
import json

def loadData(name="Deutschland", altersgruppe='A80+'):
    with open('full-data.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        csv_headers = next(spamreader)
        i=[]
        i80=[]
        i80date={}
        i80deaths={}
        for row in spamreader:
            datestringrow = int(row[8])/1000
            if name != "Deutschland":
                if row[2].find(name) > 0:
                    i.append(row)
                    if row[3] == altersgruppe:
                        i80.append(row)
                        if not datestringrow in i80date:
                             i80date[datestringrow] = 0
                        i80date[datestringrow] = i80date[datestringrow] + int(row[5])

                        if not datestringrow in i80deaths:
                             i80deaths[datestringrow] = 0
                        i80deaths[datestringrow] = i80deaths[datestringrow] + int(row[6])
            else:
                if row[3] == altersgruppe:
                    i80.append(row)
                    if not datestringrow in i80date:
                         i80date[datestringrow] = 0
                    i80date[datestringrow] = i80date[datestringrow] + int(row[5])

                    if not datestringrow in i80deaths:
                         i80deaths[datestringrow] = 0
                    i80deaths[datestringrow] = i80deaths[datestringrow] + int(row[6])

        with open('data'+name+'.txt', 'w') as fobj:
            json.dump(i80date, fobj)
        with open('data'+name+'deaths.txt', 'w') as fobj:
            json.dump(i80deaths, fobj)
        with open('data'+name+'RAW.txt', 'w') as fobj:
            json.dump(i80, fobj)

def calc7Tage(input80date, einwohneranzahl, raum=-7):
    output7Tage = {}
    for keyO, valueO in input80date.items():
        anzahlSUM = 0
        for key, value in input80date.items():
            delta = keyO - key
            if (delta > dt.timedelta(days = raum)) and (delta <= dt.timedelta(days = 0)):
                anzahlSUM = anzahlSUM + value
        output7Tage[keyO] = anzahlSUM/einwohneranzahl * 100000
    output7Tage = OrderedDict(sorted(output7Tage.items(), key=lambda t: t[0]))
    return output7Tage

def calcNormalized(input80date, einwohneranzahl, raum=-7):
    ret = {}
    for key, value in input80date.items():
        ret[key] = value/einwohneranzahl * 100000
    ret = OrderedDict(sorted(ret.items(), key=lambda t: t[0]))
    return ret

def savePlot(in7, in14, in80deaths, name, color, startdate, altersgruppe, max1=60, max2=6):
    fig, host = plt.subplots(figsize=(15,4),sharex=True)
    fig.suptitle('Corona bei Altersgruppe '+altersgruppe, fontsize=16)
    ax2 = host.twinx()
    lns = []

    host.set_ylabel("Inzidenz pro 100k")
    p11, = host.plot_date(in7.keys(),in7.values(),linestyle='solid',color =color,label=name+' 7 Tages Inzidenz', marker=",")
    lns.append(p11)

    ax2.set_ylabel("Gemeldete Tote pro 100k")
    p21, = ax2.plot_date(in80deaths.keys(),in80deaths.values(),linestyle='dashed',color =color,label=name+' Todeszahlen Normalisiert', marker=",")
    lns.append(p21)

    # p12, = host.plot_date(in14.keys(),in14.values(),linestyle="dashdot",color=color,label=name+' 14 Tages Inzidenz', marker=",")
    # lns.append(p12)

    if max1 > 0:
        host.set_ylim(0, max1)
    if max2 > 0:
        ax2.set_ylim(0, max2)

    # lns = [p11, p21, p12]
    host.legend(handles=lns, bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=2)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.fmt_xdata = mdates.DateFormatter('%d.%m.%Y')
    datexticks = [startdate]
    while startdate < dt.datetime.today():
        startdate = startdate + dt.timedelta(days=7)
        datexticks.append(startdate)

    host.set_xticks(datexticks)
    host.tick_params(axis="x",labelrotation=45)
    # plt.show()
    fig.savefig(name+'.png', orientation='landscape')

def createPlots(name, altersgruppe, einwohneranzahl, color="black", startdate=dt.datetime(2020,10,1), maxYInzidenz=60, maxYTodeszahlen=6):
    i80date = {}
    i80deaths = {}

    with open('data'+name+'.txt') as fobj:
        i80dateRAW = json.load(fobj)
    with open('data'+name+'deaths.txt') as fobj:
        i80deathsRAW = json.load(fobj)
    with open('data'+name+'RAW.txt') as fobj:
        i80RAW = json.load(fobj)
    for key, value in i80dateRAW.items():
        if dt.datetime.fromtimestamp(float(key)) > startdate:
            i80date[dt.datetime.fromtimestamp(float(key))]=value
    for key, value in i80deathsRAW.items():
        if dt.datetime.fromtimestamp(float(key)) > startdate:
            i80deaths[dt.datetime.fromtimestamp(float(key))]=value


    i80date = OrderedDict(sorted(i80date.items(), key=lambda t: t[0]))
    i80deaths = OrderedDict(sorted(i80deaths.items(), key=lambda t: t[0]))
    i80deathsN = calcNormalized(i80deaths, einwohneranzahl)
    i7 = calc7Tage(i80date, einwohneranzahl)
    i14 = calc7Tage(i80date, einwohneranzahl, -14)
    makePlot(i7, i14, i80deathsN, name, color, startdate, altersgruppe, maxYInzidenz, maxYTodeszahlen)


# HERE
loadData("Deutschland", "A80+")
createPlots("Deutschland", "A80+", 83166711, "black", dt.datetime(2020,9,1), 0, 0)
