__author__ = 'Ryan'
import FBB_League
from Scrape_espn_league import *
import pandas as pd
#RYAN IS A BADDY TEST

def main():
    NCB = FBB_league('123478', '2015')
    hitters = pd.read_csv('Data/Hitters_projections.csv')
    pitchers = pd.read_csv('Data/Pitchers_projections.csv')
    teams = pd.read_csv('Data/NCB_teams.csv')
