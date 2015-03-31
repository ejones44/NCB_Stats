__author__ = 'Ryan'
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
import pickle
from robobrowser import RoboBrowser
from espn_login import *


espn_header = {'1/0': 'H/AB', '1/0': 'H/AB', }

def loginToESPN(leagueID, year):
    link = 'http://games.espn.go.com/flb/leagueoffice?leagueId='+str(leagueID)+'&seasonId='+str(year)
    br = RoboBrowser(history=True)
    br.open(link)
    try:
        form = br.get_form(action="https://r.espn.go.com/espn/memberservices/pc/login")
        form['username'].value = login.username
        form['password'].value = login.password
        br.submit_form(form)
    except:
        print('\nNo need to login!\n')

    return br

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def nameToPos(name, positions):
    #returns  ['PlayerID', 'Name', 'Team', 'C', '1B',  ]
    posOut = [None]*len(positions)
    pID = None
    team = None
    return [pID, name, team] + posOut

def getPositions(leagueID, year):
    pass

def scrapePlayerProjections(leagueID, year):
    br = loginToESPN(leagueID, year)
    Hitters = pd.DataFrame()
    Pitchers = pd.DataFrame()
    thead = []
    #get batter values
    br.open('http://games.espn.go.com/flb/freeagency?leagueId='+str(leagueID)+'&teamId=1&seasonId='+str(year)+'&context=freeagency&view=stats&version=projections&startIndex=0&avail=-1')
    table = br.find_all('table', class_='playerTableTable tableBody')[0]
    rows = table.find_all('tr')

    #get the column headers
    header = rows[1]
    data = header.find_all('td')
    data = data[0] + data[8:33]+data[34:41]+[data[42]]
    for d in data:
        print(d.text)
        txt = d.text.replace('\xa0', '')
        thead.append(txt.format('ascii'))
    thead.insert(0, 'PlayerID')
    if 'H/AB' in thead:
        ind = thead.index('H/AB')
        thead[ind] = 'AB'   #AB stored in ind+1
        thead.insert(ind, 'H')  #H stored in ind

    #get player projections
    rows = rows[2:]
    for r in rows:
        data = r.find_all('td')
        data = data[0] + data[8:33]+data[34:41]+[data[42]]
        row_data = []
        for i, d in enumerate(data):
            if i == 0:
                row_data = nameToPos(d)




def scrapeTeamPlayers():
    pass

def scrapeMatchups():
    pass

def scrapeMatchupPlayers():
    pass


#NCB ID = '12345678'
#Data League = '158970'
scrapePlayerProjections('158970','2015')