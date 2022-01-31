import requests
import csv
import re
from bs4 import BeautifulSoup

# Function to extract all game URLs for a specific NBA year and store them in a list
def extractGameURLs(year):
    URLs_list = list()
    domain_URL = "https://www.basketball-reference.com/leagues/NBA_"
    year_URL = domain_URL + str(year) + "_games-"
    months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june' ,'july']#'august', 'september']
    #months = ['october-2019', 'november', 'december', 'january', 'february', 'march', 'july', 'august', 'september', 'october-2020']
    #months = ['february', 'march', 'april', 'may', 'june']
    for month in months:
        URL = year_URL + month + ".html"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        schedule_div = soup.find(id="schedule")
        schedule_str = str(schedule_div)
        # We are looking to match the string "201410280SAS" that is used in creating the NBA boxscores URL
        regex = '\d{9}\w{3}'
        match = re.findall(regex,schedule_str)
        for item in (set(match)):
            URLs_list.append(item)
        URLs_list.sort()
    return URLs_list

# Function to create the CSV file and write the header
def writeCsvHeader(fileName):
    with open(fileName, 'w', encoding='UTF-8', newline="") as f:
        header = ['URL','GameType','Location','Date','Time','WinningTeam','AwayTeam','HomeTeam','Quarter',
        'TimeLeft','GamePlay','AwayPlay','AwayScore','HomePlay','HomeScore']
        writer = csv.writer(f)
        writer.writerow(header)
        return f

# Function to write to the CSV file row by row, as this is processed by the playByPlay() function
def writeCsv(filename,itemList):
    with open(filename, 'a', encoding='UTF-8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(itemList)

# Function which reads the game URL, makes the request to the website Server, retrieves basic information about the game and then calls playByPlay function.
def pbpRead(pbp_URL):
    httpString = 'https://www.basketball-reference.com/boxscores/pbp/'
    finalURL = httpString + pbp_URL + '.html'
    page = requests.get(finalURL)
    soup = BeautifulSoup(page.content,"html.parser")
    a = soup.find_all(re.compile("game_summaries"))
    URL = finalURL[-31:]
    homeTeam, awayTeam = teamNames(soup)
    gameType = gameTypeDecider(soup)
    date, time, location = locationGameTime(soup)
    winningTeam = findWinner(soup,homeTeam, awayTeam)
    fixedList = [URL,gameType,location,date,time,winningTeam,awayTeam,homeTeam]
    playByPlay(soup,fixedList)

# This function looks into a particular div that holds the values of the Home & Away team.
def teamNames(soup):
    item = soup.find_all('a',itemprop='name')
    awayTeam = item[0].string
    homeTeam = item[1].string
    return homeTeam, awayTeam

# This function searches for a specific string 'game_summaries playoffs compressed' which exists only in playoff games
# It returns 'playoff' or 'regular' value which is assigned back to gameType variable
def gameTypeDecider(soup):
    page_text = str(soup)
    if(re.findall('game_summaries playoffs compressed',page_text)):
        return 'playoff'
    else:
        return 'regular'

# This function searches for the div with the class='scorebox_meta' and after iterating inside its items, should
# extract the values for date, time & location of the match, which are returned to the main function.
def locationGameTime(soup):
    scoreDiv = soup.find(class_='scorebox_meta')
    tempList = list()
    for child in scoreDiv.children:
        tempDiv = child.string
        if (tempDiv!= '\n') and (tempDiv!= None):
            tempList.append(tempDiv)
    if len(tempList) == 2: # This condition covers all seasons after 2001 where the Time & Location information were introduced
        date = tempList[0].split(',',1)[0]
        time = tempList[0].split(',',1)[1].lstrip()
        location = tempList[1].replace(',','')
    elif len(tempList) == 1: # This condition covers all seasons prior to 2001
        date = date = tempList[0]
        time = ''
        location = ''
    return date, time, location

# This function returns the name of the Winning Team.
def findWinner(soup, team1, team2):
    awayScore = int(soup.find_all(class_='score')[0].string)
    homeScore = int(soup.find_all(class_='score')[1].string)
    if homeScore > awayScore :
        return team1
    else:
        return team2

# This function reads the main play-by-play table and retrieves the information that we intend to copy to our CSV.
def playByPlay(soup,itemList):
    table = soup.find('table', id="pbp")
    rows = table.find_all('tr')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 0:
            if re.findall('id=\"q',str(row)):
                qString = row.find('th')
                quarter = qString.string #to add to the list
                # Initialize all other values to empty strings
                timeLeft = ''
                gamePlay = ''
                awayPlay = ''
                awayScore = ''
                awayScoreChange = ''
                homePlay = ''
                homeScore = ''
                homeScoreChange = ''
            else:
                continue
        elif len(columns) == 1:
            continue
        elif len(columns) == 2:
            timeLeft = columns[0].string
            gamePlay = columns[1].get_text()
            awayPlay = ''
            awayScore = ''
            awayScoreChange = ''
            homePlay = ''
            homeScore = ''
            homeScoreChange = ''
        else:
            timeLeft = columns[0].string
            awayPlay = columns[1].get_text() if re.findall('\w+',columns[1].get_text()) else ''
            awayScore = columns[3].string.split('-')[0] if re.findall('\w+',columns[3].string) else ''
            homeScore = columns[3].string.split('-')[1] if re.findall('\w+',columns[3].string) else ''
            homePlay = columns[5].get_text() if re.findall('\w+',columns[5].get_text()) else ''
            gamePlay = ''

        finalList = itemList + [quarter, timeLeft, gamePlay, awayPlay, awayScore, homePlay, homeScore]
        writeCsv(fileName, finalList)

#year = int(input("Which NBA season would you like to extract: "))
for year in range(2021,2023):
    fileName = 'nbaSeason' + str(year-1) + '_' + str(year) + '.csv'
    gameList = extractGameURLs(year)
    writeCsvHeader(fileName)
    for game in gameList:
        pbpRead(game)
        print('Now printing game:',game)
    print('All games saved in the file were printed successfully!')


# 1996 - 1997 play-by-play is introduced
# Replace def locationGameTime(soup)
# 2000 - 2001 introduces Location & GameTime. Prior to that only information displayed is Date
# ---- SEASONS MISSING -----
# 2010 - 2011 DONE!
# 2011 - 2012 DONE!
# 2019 - 2020 (COVID)
# 2020 - 2021 (post-COVID)
# 2021 - 2022
# 1996 - 1997
# 1997 - 1998
# 1998 - 1999
# 1999 - 2000
