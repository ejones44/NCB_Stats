__author__ = 'Ryan'
import pandas as pd


class FBB_Team:
    def __init__(self, leagueID, year, teamId):
        self.leagueID = leagueID
        self.year = year
        self.teamId = teamId
        self.batters = pd.DataFrame()
        self.pitchers = pd.DataFrame()
