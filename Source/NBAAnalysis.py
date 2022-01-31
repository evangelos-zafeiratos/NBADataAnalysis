import pandas as pd
import os

path = r'C:\Users\Vangelis\Desktop\Courses & Projects\Data Analysis Projects\NBA Datasets Analysis\Data'
os.chdir(path)

#seasonList1 = ['1996_1997']
seasonList = ['1996_1997',
              '1997_1998',
              '1998_1999',
              '1999_2000',
              '2000_2001',
              '2001_2002',
              '2002_2003',
              '2003_2004',
              '2004_2005',
              '2005_2006',
              '2006_2007',
              '2007_2008',
              '2008_2009',
              '2009_2010',
              '2010_2011',
              '2011_2012',
              '2012_2013',
              '2013_2014',
              '2014_2015',
              '2015_2016',
              '2016_2017',
              '2017_2018',
              '2018_2019',
              '2019_2020',
              '2020_2021'
              ]

def getStats(quarter):

    plus20PointsRatio = list()
    plus10PointsRatio = list()
    maxComeback = list()
    avgComeback = list()
    yearlyComeback = list()

    for season in seasonList:
        fileName = 'nbaSeason' + season + '.csv'
        # Import of the dataset and selection of only the necessary columns for our analysis.
        df = pd.read_csv(fileName, usecols = ["URL", "Quarter", "Time", "WinningTeam", "AwayTeam", "AwayScore", "HomeTeam", "HomeScore"])
        if quarter == 4:
            df = df[df['Quarter'] == '4th Q']
        # Creation of new columns to hold the score margin values after any change in the boxscore.
        df['MarginHome'] = df['HomeScore'] - df['AwayScore']
        df['MarginAway'] = df['AwayScore'] - df['HomeScore']

        # Renaming of the WinningTeam column value to binary "Home" or "Away" to help in our analysis.
        df.loc[(df.WinningTeam == df.HomeTeam), 'WinningTeam'] = 'Home'
        df.loc[(df.WinningTeam == df.AwayTeam), 'WinningTeam'] = 'Away'

        # By making use of the groupby() function, we calculate the maximum margin built by both teams during each game.
        # We extract both columns to be used to construct new DataFrame
        MarginHome = df.groupby("URL")["MarginHome"].max()
        MarginAway = df.groupby("URL")["MarginAway"].max()
        Date = df.groupby("URL")["Time"].max()
        HomeTeam = df.groupby("URL")["HomeTeam"].max()
        AwayTeam = df.groupby("URL")["AwayTeam"].max()

        NoGames = MarginHome.shape[0]

        # Implement unique function to extract list of winning teams; since it ruturns list, we apply str[0] to extract string value
        WinningTeam = df.groupby("URL")["WinningTeam"].unique().str[0]

        # Construction of a dictionary with columns to be used in the new dataframe
        frame = {'HomeTeam' : HomeTeam, 'AwayTeam' : AwayTeam, 'WinningTeam' : WinningTeam, 'MaxMarginHome': MarginHome, 'MaxMarginAway': MarginAway, 'Date' : Date}
        marginDf = pd.DataFrame(frame)

        marginDf.loc[marginDf['MaxMarginHome'] < 0, 'MaxMarginHome'] = 0
        marginDf.loc[marginDf['MaxMarginAway'] < 0, 'MaxMarginAway'] = 0

        # A new empty column is initialized to hold the value of the maximum comeback margin per game.
        marginDf["Margin"] = ""
        marginDf.loc[(marginDf.WinningTeam == 'Home'), 'Margin'] = marginDf.MaxMarginAway
        marginDf.loc[(marginDf.WinningTeam == 'Away'), 'Margin'] = marginDf.MaxMarginHome

        # Remove all games where winning team never trailed
        marginDf = marginDf[marginDf['Margin'] > 0]

        # Extact the metrics we want from the season
        plus20PointsRatio.append(round(marginDf["Margin"][marginDf["Margin"] >= 20].count()/NoGames * 100,2))
        plus10PointsRatio.append(round(marginDf["Margin"][marginDf["Margin"] >= 10].count()/NoGames * 100,2))
        maxComeback = marginDf["Margin"].max()
        avgComeback.append(round(marginDf["Margin"].mean(),2))
        homeTeam = marginDf["HomeTeam"][marginDf["Margin"] == maxComeback].values[0]
        awayTeam = marginDf["AwayTeam"][marginDf["Margin"] == maxComeback].values[0]
        date = marginDf['Date'][marginDf['Margin'] == maxComeback].values[0]
        yearRecord = (date, homeTeam, awayTeam, int(maxComeback))
        yearlyComeback.append(yearRecord)

    NbaData = { 'Comeback 10Points+' : plus10PointsRatio, 'Comeback 20Points+' : plus20PointsRatio, 'Average Comeback' : avgComeback, 'YearRecord' : yearlyComeback}
    if quarter == 4 :
        NbaSeasonQ4Df = pd.DataFrame(data = NbaData, index = seasonList)
        return NbaSeasonQ4Df
    else:
        NbaSeasonDf = pd.DataFrame(data = NbaData, index = seasonList)
        return NbaSeasonDf

Nbadf = getStats(10)
NbaQ4df = getStats(4)

with pd.ExcelWriter('NbaStats.xlsx') as writer :
    Nbadf.to_excel(writer, sheet_name = 'Full Games')
    NbaQ4df.to_excel(writer, sheet_name = '4th Quarter')
print(Nbadf)
print(NbaQ4df)
