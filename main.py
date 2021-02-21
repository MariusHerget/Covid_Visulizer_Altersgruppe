import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from collections import OrderedDict
plt.style.use('seaborn')
import json
import os

def loadData(names=["Deutschland"], altersgruppen=['A80+']):
    if not os.path.isfile('full-data.csv'):
        print("### Please download the data from https://pavelmayer.de/covid/risks/data.csv")
        break
    for name in names:
        for altersgruppe in altersgruppen:
            with open('full-data.csv', newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                csv_headers = next(spamreader)
                i=[]
                idate={}
                ideaths={}
                for row in spamreader:
                    datestringrow = int(row[8])/1000
                    if name in ['Sachsen', 'Baden-Württemberg', 'Rheinland-Pfalz', 'Thüringen', 'Hamburg' , 'Niedersachsen', 'Bayern', 'Brandenburg', 'Berlin', 'Schleswig-Holstein', 'Saarland', 'Sachsen-Anhalt', 'Mecklenburg-Vorpommern', 'Nordrhein-Westfalen', 'Bremen', 'Hessen']:
                        # print(row[1], row[1].find(name) > 0)
                        if row[1] == name:
                            if row[3] == altersgruppe:
                                i.append(row)
                                if not datestringrow in idate:
                                     idate[datestringrow] = 0
                                idate[datestringrow] = idate[datestringrow] + int(row[5])

                                if not datestringrow in ideaths:
                                     ideaths[datestringrow] = 0
                                ideaths[datestringrow] = ideaths[datestringrow] + int(row[6])
                    elif name != "Deutschland":
                        if row[2].find(name) > 0:
                            # i.append(row)
                            if row[3] == altersgruppe:
                                i.append(row)
                                if not datestringrow in idate:
                                     idate[datestringrow] = 0
                                idate[datestringrow] = idate[datestringrow] + int(row[5])

                                if not datestringrow in ideaths:
                                     ideaths[datestringrow] = 0
                                ideaths[datestringrow] = ideaths[datestringrow] + int(row[6])
                    else:
                        # Gesamt
                        if row[3] == altersgruppe:
                            # i.append(row)
                            if not datestringrow in idate:
                                 idate[datestringrow] = 0
                            idate[datestringrow] = idate[datestringrow] + int(row[5])

                            if not datestringrow in ideaths:
                                 ideaths[datestringrow] = 0
                            ideaths[datestringrow] = ideaths[datestringrow] + int(row[6])
                data = {'date':idate, 'deaths': ideaths, 'raw': i}
                with open('data/data_'+name+'_'+altersgruppe+'.txt', 'w') as fobj:
                    json.dump(data, fobj)

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

def savePlot(in7, in14, in80deaths, name, color, startdate, altersgruppe, einwohneranzahl, max1=60, max2=6):
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
    # fig.fmt_xdata = mdates.DateFormatter('%d.%m.%Y')
    datexticks = [startdate]
    today = dt.datetime.today()
    while startdate < today:
        startdate = startdate + dt.timedelta(days=7)
        datexticks.append(startdate)

    date_formatter = mdates.DateFormatter('%d.%m.%Y')
    # Set the major tick formatter to use your date formatter.
    host.set_xticks(datexticks)
    host.xaxis.set_major_formatter(date_formatter)
    host.tick_params(axis="x",labelrotation=30)
    # estring = f'{600:,}'
    host.text(0,-0.285,
        'Einwohneranzahl: '+'{:,}'.format(einwohneranzahl)+' | Letzter Datenpunkt: '+list(in7.keys())[-1].strftime('%d.%m.%Y')+' | Erstellt am: '+today.strftime('%d.%m.%Y'),
        size=9, ha="left",
        transform=host.transAxes)
    # plt.show()
    fig.tight_layout()
    fig.savefig('graphs/'+name+'_'+altersgruppe+'.png', orientation='landscape')

def createPlots(names, altersgruppen, color="black", startdate=dt.datetime(2020,10,1), maxYInzidenz=60, maxYTodeszahlen=6):
    for name, einwohneranzahl in names.items():
        for altersgruppe in altersgruppen:
            i80date = {}
            i80deaths = {}
            if not os.path.isfile('data/data_'+name+'_'+altersgruppe+'.txt'):
                loadData([name], [altersgruppe])
            with open('data/data_'+name+'_'+altersgruppe+'.txt') as fobj:
                data = json.load(fobj)
                i80dateRAW = data["date"]
                i80deathsRAW = data["deaths"]
                i80RAW = data["raw"]
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
            savePlot(i7, i14, i80deathsN, name, color, startdate, altersgruppe, einwohneranzahl, maxYInzidenz, maxYTodeszahlen)


# HERE
createPlots(
    {"Deutschland": 83166711, "Bayern": 13124737, "Tirschenreuth": 72046}, ["A80+", "A60-A79", "A35-A59"], "black", dt.datetime(2020,9,1), 0, 0)
# createPlots(
#     ['Sachsen', 'Baden-Württemberg', 'Rheinland-Pfalz', 'Thüringen', 'Hamburg' , 'Niedersachsen', 'Bayern', 'Brandenburg', 'Berlin', 'Schleswig-Holstein', 'Saarland', 'Sachsen-Anhalt', 'Mecklenburg-Vorpommern', 'Nordrhein-Westfalen', 'Bremen', 'Hessen'],
#     ["A80+", "A60-A79", "A35-A59"],, "A60-A79", "A35-A59", "A15-A34", "A05-A14", "A00-A04" , "Schweinfurt": 115445, "Tirschenreuth": 72046
#     [83166711],
#     "black", dt.datetime(2020,9,1), 0, 0)
