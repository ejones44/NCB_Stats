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
        form['username'].value = login.username.value
        form['password'].value = login.password.value
        br.submit_form(form)
        print('\nLogging In\n')
    except:
        print('\nNo need to login!\n')

    return br

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def nameToBatPos(d):
    #BatPos = ['Catcher', 'First Base', 'Second Base', 'Third Base', 'Shortstop', 'Left Field', 'Center Field', 'Right Field', 'Designated Hitter']
    s = d.text.format('ascii')
    name = s[:s.find(',')]
    s = s[s.find(',')+2:]
    pID = d.find_all('a')[0]['playerid']
    team = s[:s.find('\xa0')]
    pos = s[s.find('\xa0')+1:]
    posOut = getBatPositions(pos)
    return [pID, name, team] + posOut

def getBatPositions(s):
    posOut = [None]*9
    if 'SSPD' in s:
        s = s.replace('SSPD', '')
    if '1B' in s:
        posOut[1] = 1
        s = s.replace('1B', '')
    if '2B' in s:
        posOut[2] = 1
        s = s.replace('2B', '')
    if '3B' in s:
        posOut[3] = 1
        s = s.replace('3B', '')
    if 'SS' in s:
        posOut[4] = 1
        s = s.replace('SS', '')
    if 'LF' in s:
        posOut[5] = 1
        s = s.replace('LF', '')
    if 'CF' in s:
        posOut[6] = 1
        s = s.replace('CF', '')
    if 'RF' in s:
        posOut[7] = 1
        s = s.replace('RF', '')
    if 'DH' in s:
        posOut[8] = 1
        s = s.replace('DH', '')
    if 'C' in s:
        posOut[0] = 1
        s = s.replace('C', '')
    return posOut

def splitHAB(s):
    hits = s[:s.find('/')]
    ab = s[s.find('/')+1:]
    if is_number(hits):
        hits = float(hits)
    else:
        hits = 0
    if is_number(ab):
        ab = float(ab)
    else:
        ab = 0
    return [hits, ab]

def nameToPitchPos(d):
    #['Starting Pitcher', 'Relief Pitcher']
    s = d.text.format('ascii')
    name = s[:s.find(',')]
    s = str(s[s.find(',')+2:])
    pID = d.find_all('a')[0]['playerid']
    team = s[:s.find('\xa0')]
    pos = s[s.find('\xa0')+1:]
    posOut = getPitchPositions(pos)
    return [pID, name, team] + posOut

def getPitchPositions(s):
    posOut = [None]*2
    if 'SSPD' in s:
        s = s.replace('SSPD', '')
    if 'SP' in s:
        posOut[0] = 1
        s = s.replace('SP', '')
    if 'RP' in s:
        posOut[1] = 1
        s = s.replace('RP', '')
    return posOut

def tableToBatters(table):
    Hitters = pd.DataFrame()
    rows = table.find_all('tr')
    rows = rows[2:]
    for r in rows:
        data = r.find_all('td')
        data = [data[0]] + data[8:33]+data[34:41]+[data[42]]
        row_data = []
        for i, d in enumerate(data):
            if i == 0:
                row_data = nameToBatPos(d)
            elif '/' in d.text:
                row_data += splitHAB(d.text)
            else:
                if is_number(d.text):
                    row_data.append(float(d.text))
                else:
                    row_data.append(0)
        Hitters = Hitters.append(pd.Series(row_data), ignore_index=True)
    return Hitters

def tableToPitchers(table):
    Pitchers = pd.DataFrame()
    rows = table.find_all('tr')
    rows = rows[2:]
    for r in rows:
        data = r.find_all('td')
        data = [data[0]] + data[8:39]
        row_data = []
        for i, d in enumerate(data):
            if i == 0:
                row_data = nameToPitchPos(d)
            else:
                if is_number(d.text):
                    row_data.append(float(d.text))
                else:
                    row_data.append(0)
        Pitchers = Pitchers.append(pd.Series(row_data), ignore_index=True)
    return Pitchers


def scrapePlayerProjections(leagueID, year):
    br = loginToESPN(leagueID, year)
    Hitters = pd.DataFrame()
    HitPos = ['Catcher', 'First Base', 'Second Base', 'Third Base', 'Shortstop', 'Left Field', 'Center Field', 'Right Field', 'Designated Hitter']
    Pitchers = pd.DataFrame()
    PitchPos = ['Starting Pitcher', 'Relief Pitcher']
    thead = []
    index = 0
    #get batter values
    br.open('http://games.espn.go.com/flb/freeagency?leagueId='+str(leagueID)+'&teamId=1&seasonId='+str(year)+'&context=freeagency&view=stats&version=projections&startIndex=0&avail=-1&startIndex='+str(index))
    table = br.find_all('table', class_='playerTableTable tableBody')[0]
    rows = table.find_all('tr')

    #get the column headers
    header = rows[1]
    data = header.find_all('td')
    data = [data[0]] + data[8:33]+data[34:41]+[data[42]]
    for d in data:
        txt = d.text.replace('\xa0', '')
        thead.append(txt.format('ascii'))
    thead[0] = 'PlayerID'
    if 'H/AB' in thead:
        ind = thead.index('H/AB')
        thead[ind] = 'AB'   #AB stored in ind+1
        thead.insert(ind, 'H')  #H stored in ind
    thead.insert(1, 'Team')
    thead.insert(1, 'Name')
    thead = thead[0:3]+HitPos+thead[3:]
    #get player projections
    while index < 250:
        br.open('http://games.espn.go.com/flb/freeagency?leagueId='+str(leagueID)+'&teamId=1&seasonId='+str(year)+'&context=freeagency&view=stats&version=projections&avail=-1&startIndex='+str(index))
        table = br.find_all('table', class_='playerTableTable tableBody')[0]
        Hitters = Hitters.append(tableToBatters(table))
        index += 50
    Hitters.columns = thead
    index = 0


    #get Pitchers
    br.open('http://games.espn.go.com/flb/freeagency?leagueId='+str(leagueID)+'&teamId=1&seasonId='+str(year)+'&context=freeagency&view=stats&version=projections&avail=-1&slotCategoryGroup=2&startIndex='+str(index))
    table = br.find_all('table', class_='playerTableTable tableBody')[0]
    rows = table.find_all('tr')

    #get the column headers
    thead = []
    header = rows[1]
    data = header.find_all('td')
    data = [data[0]] + data[8:39]
    for d in data:
        txt = d.text.replace('\xa0', '')
        thead.append(txt.format('ascii'))
    thead[0] = 'PlayerID'
    thead.insert(1, 'Team')
    thead.insert(1, 'Name')
    thead = thead[0:3]+PitchPos+thead[3:]
    #get player projections
    while index < 250:
        br.open('http://games.espn.go.com/flb/freeagency?leagueId='+str(leagueID)+'&teamId=1&seasonId='+str(year)+'&context=freeagency&view=stats&version=projections&avail=-1&slotCategoryGroup=2&startIndex='+str(index))
        table = br.find_all('table', class_='playerTableTable tableBody')[0]
        Pitchers = Pitchers.append(tableToPitchers(table))
        index += 50
    Pitchers.columns = thead

    print(Pitchers)

    Hitters.to_csv('Hitters_projections.csv')
    Pitchers.to_csv('Pitchers_projections.csv')


def scrapeTeamPlayers(leagueID, year):
    pass

def scrapeMatchups():
    pass


def scrapeLeagueSchedule():
    pass


def scrapeMatchupPlayers():
    pass


# returns data frame containing
# [teamID, teamName, shortName, wins, losses, draws]
def scrapeLeagueTeams(leagueID, year):
    br = loginToESPN(leagueID, year)

    # dataframe will have the following columns:
    #[teamID, teamName, wins, losses, draws]
    teams = pd.DataFrame()

    br.open('http://games.espn.go.com/flb/standings?leagueId=' + str(leagueID) + '&seasonId=' + str(year))
    tables = br.find_all('table', class_='tableBody')
    tables = tables[:-1]
    for t in tables:
        print('\nTABLE\n')
        row = t.find_all('tr')[2:]
        for r in row:
            data = r.find_all('td')
            name = data[0]
            name_row = teamNameToRow(name)
            wins = float(data[1].text)
            losses = float(data[2].text)
            draw = float(data[3].text)
            out = name_row + [wins, losses, draw]
            teams = teams.append(pd.Series(out), ignore_index=True)
    print(teams)
    teams.columns = ['teamId', 'Name', 'W', 'L', 'T']
    return teams


def teamNameToRow(name):
    link = name.find_all('a')[0]['href']
    ID = link.split('&')[1]
    teamID = int(ID[ID.find('=') + 1:])
    teamName = name.text

    return [teamID, teamName]


def scrapeTeamStats(leagueID, year):
    br = loginToESPN(leagueID, year)

    # dataframe will have the following columns:
    #[teamID, teamName, wins, losses, draws]
    teamStats = pd.DataFrame()

    br.open('http://games.espn.go.com/flb/standings?leagueId=' + str(leagueID) + '&seasonId=' + str(year))
    tables = br.find_all('table', class_='tableBody')
    table = tables[-1]
    rows = table.find_all('tr')
    head = rows[2].find_all('td')
    header = [h.text for h in head]
    while '' in header:
        header.remove('')
    header.insert(0, 'Name')
    header.insert(0, 'teamID')
    stats = rows[3:]

    for r in stats:
        data_row = []
        data = r.find_all('td')
        name = teamNameToRow(data[1])
        data = data[2:-2]
        for d in data:
            if is_number(d.text):
                data_row.append(float(d.text))
        out = name + data_row
        print(out)
        teamStats = teamStats.append(pd.Series(out), ignore_index=True)

    teamStats.columns = header
    print(teamStats)
    return teamStats


teamStats = scrapeTeamStats('123478', '2015')
teamStats.to_csv('Team_Season_Stats.csv')