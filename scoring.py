from __future__ import print_function
import pymysql
import operator
from threeteam import h2hThreeTeams
from teamsPlayed import didteamsplay
from passwords import DATABASE_HOST,DATABASE_USERNAME,DATABASE_PASSWORD
import time


#Main that gets called
tournament_id = 0
poolName = ""

#creating dict for keeping track of all the scores
allPointsByTeamDict = {}
totalPointsByTeamDict = {}

#Used to know what steps each team has gone up to, so we can avoid putting it in the database
stepReachedByTeamDict = {}
cur = None

#Used to remember if those teams played 
UntiedLast = []
mydb = None

def calculateRawPoints(games):
    # #Calculates raw points for the teams
    print("Games in Consideration: ")
    for game in games:
        print(game)
        givePoints(game)

def H2HgamenotFound(scores,allPointsByTeamDict):
    team1 = scores[0]
    team2 = scores[1]
    allPointsByTeamDict[team1]['H2Hpoints'] = 1
    allPointsByTeamDict[team2]['H2Hpoints'] = 1
    allPointsByTeamDict[team1]['TotalPoints'] += 0.1
    allPointsByTeamDict[team2]['TotalPoints'] += 0.1
    return False

def h2hTwoTeams(key, scores, RawPointDuplicateCheck, dbData, h2h2):
    #Helper function for h2htwoteams, where it checks if they played each other
    scores = list(scores)
    print("Repeating " + str(scores))
    returnStatement = True
    gameH2HFound = None
    gameH2HFound = didteamsplay(dbData,scores[0], scores[1])
    print("gameH2HFound " +  str(gameH2HFound))
    if gameH2HFound != False:
        game = gameH2HFound
        team1Score = game['score1']
        team2Score = game['score2']
        print("Game found")
        if team1Score > team2Score:
            winner = game['team1_id']
        elif team1Score < team2Score:
            winner = game['team2_id']
        else:
            winner = 0
        assignH2H(game, game['team1_id'], game['team2_id'], winner, h2h2)
    else:
        print("Game not found")
        team1 = scores[0]
        team2 = scores[1]
        allPointsByTeamDict[team1]['H2Hpoints'] = 1
        allPointsByTeamDict[team2]['H2Hpoints'] = 1
        allPointsByTeamDict[team1]['TotalPoints'] += 0.1
        allPointsByTeamDict[team2]['TotalPoints'] += 0.1
        returnStatement = False
    return returnStatement

def head2head(RawPointDuplicateCheck,dbData, h2h2=False):
    numberOfTies = len(RawPointDuplicateCheck)
    returnStatement = True
    # goes to teams's tied game and gets the result
    # assigns H2H Points:
    #   team won: 2 pts
    #   team lost: 0 points
    #   tied: 1 point each
    # return H2H points for each team
    
    print("H2H here: " + str(numberOfTies))
    if numberOfTies >= 1:
        ##If there are only 2 way-ties for points
        for key, teams in RawPointDuplicateCheck.items():
            if h2h2:
                for team in teams:
                    stepReachedByTeamDict[team] = 4
            if not h2h2:
                for team in teams:
                    stepReachedByTeamDict[team] = 2
            if len(teams) == 2:
                #If there are 2 teams tied, go to h2htwoteams
                returnStatement = h2hTwoTeams(key, teams, RawPointDuplicateCheck, dbData, h2h2)
            if len(teams) == 3:
                 #If there are 3 teams tied, go to h2hthreeteams
                returnStatement = h2hThreeTeams(key, teams, dbData, allPointsByTeamDict, h2h2)
            if len(teams) >3:
                for team in teams:
                    addPoints(team, 1, 'H2Hpoints')
    else:
        print("SOMETHING DANGEROUS AND BAD HAPPENED. WE SHOULD NEVER HAVE TRIGGERED H2H!")
    return returnStatement
def assignH2H(game_id, team1, team2, winner, h2h2=False):
    #This is a helper function for H2H, it gives them points to both teams for H2H
    if h2h2:
        print("Tied or not played!")
        allPointsByTeamDict[team1]['H2H2points'] += 1
        scoresForPool[team2]['H2H2points'] += 1
        allPointsByTeamDict[team2]['TotalPoints'] += 0.1
        allPointsByTeamDict[team2]['TotalPoints'] += 0.1
        return
        
    if winner == 0:
        print("Tied or not played!")
        allPointsByTeamDict[team1]['H2Hpoints'] += 1
        allPointsByTeamDict[team2]['H2Hpoints'] += 1
        allPointsByTeamDict[team2]['TotalPoints'] += 0.1
        allPointsByTeamDict[team2]['TotalPoints'] += 0.1
        return
    stepReachedByTeamDict[team1] = 2
    stepReachedByTeamDict[team2] = 2
    allPointsByTeamDict[winner]['H2Hpoints'] += 2
    allPointsByTeamDict[winner]['TotalPoints'] += 0.2

    #add tied game score
    return True
def teamOverrides(allPointsByTeamDict, teamOverrides, cur):
    print("Manual Qualification")
def pushPointstoDB(allPointsByTeamDict,mydb, cur, tournament_id, poolName):
    # TeamStackup to.... 
    # 1 - Raw points
    # 2 - H2H points
    # 3 - PD points
    # 4 - H2H2
    # 5 - Goals In favor
    

    ##Method to override scores by table
    if poolName:
        sqlOverride = "SELECT * FROM mgdb.manualstanding where tournament_id = " + str(tournament_id) + " AND pool ='" + str(poolName) + "'; "
        print("sql " + sqlOverride)
        cur.execute(sqlOverride)
    if not poolName:
        sqlOverride = "SELECT * FROM mgdb.manualstanding where tournament_id = " + str(tournament_id) + " AND pool is NULL"
        print("sql " + sqlOverride)
        cur.execute(sqlOverride)
    teamStandingsOverride = cur.fetchall()
    teamOverrides = {}
    for teams in teamStandingsOverride:
        teamOverrides[teams['team_id']] = teams

    for teams in allPointsByTeamDict:
        data  = allPointsByTeamDict[teams]
        tieBrakerReached = stepReachedByTeamDict[teams]
        #This is where it checks how for they got and gives null for the ones they didnt reach :)
        if tieBrakerReached == 1:
            print("Reached Tie Braker 1 ")
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, final_points, rank, qualify) values(%d, '%s', %d, %d, %d, %d, %d,%3.10f, %d, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'], data['TotalPnt'],data['RankNumber'], data['qualify'])
        if tieBrakerReached == 2:
            print("Reached Tie Braker 2 - H2H2points ")
            h2hPoints = data['H2Hpoints']
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, h2h, final_points, rank, qualify) values(%d, '%s', %d, %d, %d, %d, %d, %d,%3.10f, %d, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'],h2hPoints, data['TotalPnt'],data['RankNumber'], data['qualify'])
        if tieBrakerReached == 3:
            print("Reached Tie Braker 3 - H2H and PDScore ")
            h2hPoints = data['H2Hpoints']
            pdPoints = data['PDScore']
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, h2h, pd, final_points, rank, qualify) values(%d, '%s', %d, %d, %d, %d, %d, %d, %d, %3.10f, %d, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'],h2hPoints, pdPoints, data['TotalPnt'],data['RankNumber'], data['qualify'])
        if tieBrakerReached == 4:
            print("Reached Tie Braker 4 - H2H and PDScore and H2H2points")
            h2hPoints = data['H2Hpoints']
            pdPoints = data['PDScore']
            h2h2Points = data['H2H2points']
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, h2h, pd, h2h2, final_points, rank, qualify) values(%d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %3.10f, %d, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'],h2hPoints, pdPoints,h2h2Points, data['TotalPnt'],data['RankNumber'], data['qualify'])
        if tieBrakerReached == 5:
            print("Reached Tie Braker 5 - H2H,PDScore, H2H2 and Goals in favor ")
            h2hPoints = data['H2Hpoints']
            pdPoints = data['PDScore']
            h2h2Points = data['H2H2points']
            pdPoints = data['PDScore']
            gif = data['GoalsInFavor']
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, h2h, pd, h2h2, final_points, rank, gif, qualify ) values(%d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %3.10f, %d, %d, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'],h2hPoints, pdPoints,h2h2Points, data['TotalPnt'],data['RankNumber'], gif, data['qualify'])
        print(sql)
        cur.execute(sql)
        try:
            #Tries to fetch and override them
            if teamOverrides[teams]['manualqual'] == 1:
                print("Team Override Executing -> Force to 1")
                qualifySQl = "UPDATE mgdb.standings  SET qualify = %d, rank = %d WHERE tournament_id = %d AND pool = '%s' AND team_id = %d " % (1,-1,tournament_id, poolName, teams)
                print(qualifySQl)
                cur.execute(qualifySQl)
                print("Team has been manually qualified: " + str(teams))
                continue
            if teamOverrides[teams]['manualqual'] == 0:
                print("Team Override Executing -> Force to 0")
                qualifySQl = "UPDATE mgdb.standings  SET qualify = %d, rank = %d  WHERE tournament_id = %d AND pool = '%s' AND team_id = %d " % (0,-2,tournament_id, poolName, teams)
                print(qualifySQl)
                cur.execute(qualifySQl)
                print("Team has not manually qualified: " + str(teams))
                continue
            if teamOverrides[teams]['manualqual'] == -1:
                print("Team Override Executing -> Force to -1")
                qualifySQl = "UPDATE mgdb.standings  SET qualify = %d, rank = %d  WHERE tournament_id = %d AND pool = '%s' AND team_id = %d " % (-1,-3,tournament_id, poolName, teams)
                print(qualifySQl)
                cur.execute(qualifySQl)
                print("Team has not manually qualified undefined: " + str(teams))
                continue
        except:
            print("Team not found")
    cur.close()
    return



def initializeAllPointsByTeamDict(team):
        #Initializing the dict when a team doesnt exists
        if not team in allPointsByTeamDict:
            allPointsByTeamDict[team] = { "rawPoints": 0, "H2Hpoints" : 0, 'PDPoints': 0, 'TotalPoints': 0, 'PDScore': 0, 'GoalsInFavor': 0, 'PointsScoredOn': 0, 'Wins': 0 , 'Losses': 0, 'Ties': 0, 'RankNumber': 0, 'H2H2points': 0}
        return 0


def givePoints(game):
    #Give RawPoints based on score and place them on the dict
    score1 = game['score1']
    score2 = game['score2']
    team1 = game['team1_id']
    team2 = game['team2_id']
    #What each win/loss/tie is worth
    win = 2
    loss = 0
    tie = 1
    initializeAllPointsByTeamDict(team1)
    initializeAllPointsByTeamDict(team2)

    #To keep track up to where each team has gone. I can assume both teams at least got 1
    stepReachedByTeamDict[team1] = 1
    stepReachedByTeamDict[team2] = 1
    tournament_id = game['tournament_id']

    addPoints(team1, score1, 'GoalsInFavor')
    addPoints(team2, score2, 'GoalsInFavor')
    
    #Self explenatory, checks who wons and gives them points
    if score1 > score2:
        addPoints(team1, 1, 'Wins')
        addPoints(team2, 1, 'Losses')
        addPoints(team1, win, 'rawPoints')
        addPoints(team2,loss, 'rawPoints')
        game['winner_id'] = game['team1_id']
        game['tie'] = False
    elif score1 < score2:
        addPoints(team2, 1, 'Wins')
        addPoints(team1, 1, 'Losses')
        addPoints(team1, loss, 'rawPoints')
        addPoints(team2,win, 'rawPoints')
        game['winner_id'] = game['team2_id']
        game['tie'] = False
    else:
        print("Tie")
        addPoints(team1, tie, 'rawPoints')
        addPoints(team2,tie, 'rawPoints')
        addPoints(team1, 1, 'Ties')
        addPoints(team2, 1, 'Ties')
        game['winner_id'] = 0
        game['tie'] = True
    
    #RACHMANUS
    print("Rachmanus Max for this game is", game['rachmanus'])
    rachmanusMax = game['rachmanus']
    if score1 >= score2:
        Team1PD = min(rachmanusMax,game['score1'] - game['score2'])
        Team2PD = -1*Team1PD
        addPoints(team1, Team1PD, 'PDScore')
        addPoints(team2, Team2PD, 'PDScore')

    else:
        Team2PD = min(rachmanusMax,game['score2'] - game['score1'])
        Team1PD = -1*Team2PD
        addPoints(team1, Team1PD, 'PDScore')
        addPoints(team2, Team2PD, 'PDScore')
        
        
    print("Point Differentials (Including Rachmanus): " + str(Team1PD) + " | " + str(Team2PD))

def addPoints(team, addition, pointName):
    ##Generic function to add any type of points to a team
    if pointName == "rawPoints":
        allPointsByTeamDict[team]['TotalPoints'] += addition
    allPointsByTeamDict[team][pointName] += addition


def duplicateChecker(allPointsByTeamDict, keyName):
    ##It checks if the points are duplicate so it knows if it succeeded
    rev_multidict = {}
    teamsByRepeatedPointDict = {}
    global untiedLast
    #print("Points: " + str(allPointsByTeamDict))
    #Inverts the dict to see if duplicates
    print("Running Duplicate Checker for: " + keyName)
    for team, allPointsDict in allPointsByTeamDict.items():
        print("Checking team: " + str(team))
        if keyName == "":
            # The below tells the program how to calculate if there is still a tie == a duplicate., hence the name
            rev_multidict.setdefault(allPointsDict, set()).add(team)
        elif keyName == "H2Hpoints":
            totalPointsByTeamDictH2H = allPointsDict['rawPoints'] + (allPointsDict['H2Hpoints'] * 0.1)
            allPointsDict['H2HUpToNow'] = totalPointsByTeamDictH2H
            print("TotalPnt  is " + str(totalPointsByTeamDictH2H))
            rev_multidict.setdefault(allPointsDict['H2HUpToNow'], set()).add(team)
        elif keyName == "PDScore":
            totalPointsByTeamDictPD = allPointsDict['rawPoints'] + (allPointsDict['H2Hpoints'] * 0.1) + (allPointsDict['PDScore'] * 0.0001)
            allPointsDict['ValuePDScore'] = totalPointsByTeamDictPD
            rev_multidict.setdefault(allPointsDict['ValuePDScore'], set()).add(team)
            print("Went into PDScore!" + str(totalPointsByTeamDictPD))
        elif keyName == "rawPoints":
            rev_multidict.setdefault(allPointsDict['rawPoints'], set()).add(team)
        elif keyName == 'H2H2Score':
            totalPointsByTeamDictH2H2 = allPointsDict['rawPoints'] + (allPointsDict['H2Hpoints'] * 0.1) + (allPointsDict['PDScore'] * 0.0001) + (allPointsDict['H2H2points'] * 0.00001)
            allPointsDict['ValueH2H2Score'] = totalPointsByTeamDictH2H2
            rev_multidict.setdefault(allPointsDict['ValueH2H2Score'], set()).add(team)
            print("totalPointsByTeamDictH2H2 is " + str(totalPointsByTeamDictH2H2))
        elif keyName == 'TotalPoints-GIF':
            totalPointsByTeamDictGIF = allPointsDict['rawPoints'] + (allPointsDict['H2Hpoints'] * 0.1) + (allPointsDict['PDScore'] * 0.0001) + (allPointsDict['H2H2points'] * 0.00001) + (allPointsDict['GoalsInFavor'] * 0.0000001)
            allPointsDict['ValueGIFScore'] = totalPointsByTeamDictGIF
            rev_multidict.setdefault(allPointsDict['ValueGIFScore'], set()).add(team)
            print("Went into TotalPoints-GIF", str(totalPointsByTeamDictGIF))
            
            for keyLast, valueLast in untiedLast:
                if len(valueLast) > 1:
                    for itemsLast in valueLast:
                        stepReachedByTeamDict[itemsLast] = 5
                        print("UntiedLast " + str(itemsLast))
        else: #NEVER GOING TO GET TRIGGERED"
            #To keep track up to where each team has gone
            print("Going into else, Key: " + str(keyName))
            totalPointsByTeamDict = allPointsDict['rawPoints'] + (allPointsDict['H2Hpoints'] * 0.1) + (allPointsDict['PDScore'] * 0.0001) + (allPointsDict['H2H2points'] * 0.00001) + (allPointsDict['GoalsInFavor'] * 0.0000001)
            allPointsDict['TotalPnt'] = totalPointsByTeamDict
            print("TotalPnt  is " + str(totalPointsByTeamDict))
            rev_multidict.setdefault(allPointsDict['TotalPnt'], set()).add(team)
            ##rev_multidict inverts the object and uses keys as values and vice-versa
    for key, values in rev_multidict.items(): 
        print("Teams with",keyName,"=",str(key) + ":",values)
        if len(values) > 1:
            # Tell us which teams/score repeat
            untiedLast = rev_multidict.items()
            teamsByRepeatedPointDict[key] = values
            for items in values:
                ##This tells the program up to where each team reached so we cant null the values that dont affect it
                if keyName == "TotalPoints":
                    stepReachedByTeamDict[items] = 3
                if keyName == "TotalPoints-GIF":
                    stepReachedByTeamDict[items] = 5
                    print("Setting TotalPoints-GIF")
                if keyName == "PDScore":
                    stepReachedByTeamDict[items] = 3
                if keyName == "H2H2Score":
                    stepReachedByTeamDict[items] = 4
                    
            # print("Repeats " + str(values))
            # print("Repeats " + str(key))
            repeat = True
    print("teamsByRepeatedPointDict: " + str(teamsByRepeatedPointDict))
    return teamsByRepeatedPointDict

def giveRanks(sorted_teams, qualitifactionAmount, cur, totalNumberOfGamesPlayedAlready, stillTie, tournament_id ):
    ranks = []
    print('\n')
    cur.execute("select count(*) from game where tournament_id =" + str(tournament_id) + ";")
    totalNumberOfGames = cur.fetchone()
    totalNumberOfGames = totalNumberOfGames['count(*)']
    print("TotalNumberofGames is " + str(totalNumberOfGames))
    for standings, scores in enumerate(sorted_teams):
        allPointsByTeamDict[scores[0]]['qualify'] = 0
        print("ScoresforPool for team rank " + str(allPointsByTeamDict[scores[0]]))
        if stillTie:
            #I made this so that if it cant untie them give them all -1, but I removed it due to today's discussion
            print("Assigned -1 to all teams as all the games have not been reached")
            allPointsByTeamDict[scores[0]]['qualify'] = -1
            ranks.append(scores[0])
            continue
        print("TotalNumberOfGamesPlyed is " + str(totalNumberOfGamesPlayedAlready) )
        print("TotalNumberofGames "+  str(totalNumberOfGames))
        if totalNumberOfGamesPlayedAlready < totalNumberOfGames:
            print("All teams have not played, qualifying to 0")
            allPointsByTeamDict[scores[0]]['qualify'] = -1
            ranks.append(scores[0])
            continue
        

        if allPointsByTeamDict[scores[0]]['RankNumber'] <= qualitifactionAmount:
            allPointsByTeamDict[scores[0]]['qualify'] = 1
            continue
        
        # if standings < qualitifactionAmount:
        #     print("Standings is less than qualification amount")
        #     allPointsByTeamDict[scores[0]]['qualify'] = 1
        #Comprare for each individual team their rank (1,2,3) if my rank is less than or equal to the number of qualifyNeeded (QualificationAmount)
        print("Final Standings: " + str(allPointsByTeamDict[scores[0]]))
        
    # print("ranks: " + str(ranks))
    print('\n')
    return ranks

def rankBasedOn(mydb, cur, games, stillTie, tournament_id, poolName):
    ##Puts the teams in order of ranks and places it on the database (not yet implemented)

    cur.execute("SELECT qual_number FROM mgdb.tournament where tournament_id = " + str(tournament_id))

    qualitifactionAmount = cur.fetchone()
    qualitifactionAmount = qualitifactionAmount['qual_number']
    #See how many teams need to qualify to play
    
    for qual,team in enumerate(allPointsByTeamDict):
        # allPointsByTeamDict[team]['qualify'] = 0
        totalPointsByTeamDict[team] = allPointsByTeamDict[team]['rawPoints'] + (allPointsByTeamDict[team]['H2Hpoints'] * 0.1) + (allPointsByTeamDict[team]['PDScore'] * 0.0001 +  (allPointsByTeamDict[team]['H2H2points']) * 0.00001 + (allPointsByTeamDict[team]['GoalsInFavor'] * 0.0000001))
        allPointsByTeamDict[team]['TotalPnt'] = totalPointsByTeamDict[team]
    print("totalPointsByTeamDict: " + str(totalPointsByTeamDict))
    sorted_teams = sorted(totalPointsByTeamDict.items(), key=lambda kv: kv[1], reverse=True)
    for stand, teams in enumerate(sorted_teams):
        #For every sorted team, give them a rank in orderd (from sorted_team), and add + 1 to make it 1,2,3,4...
        teams = teams[0]
        allPointsByTeamDict[teams]['RankNumber'] = (stand +1)
    totalNumberOfGamesPlayedAlready = len(games)
    rankedTeams = giveRanks(sorted_teams, qualitifactionAmount, cur, totalNumberOfGamesPlayedAlready, stillTie, tournament_id)
    pushPointstoDB(allPointsByTeamDict, mydb, cur,tournament_id, poolName )
    return rankedTeams
    
def MySQLCursorDictToDict(games):
    #Some helper function, idk if I even used it
    dataDict = []
    for game in games:
        dataDict.append(game)
    return dataDict

def calculateStandings(games, mydb, cur, tournament_id, poolName): 
    #Big Overall Method
    dbData = MySQLCursorDictToDict(games)
    calculateRawPoints(games)
    RawPointDuplicateCheck = duplicateChecker(allPointsByTeamDict, "rawPoints")
    if len(RawPointDuplicateCheck) > 0:
        print(" --------------- Duplicate found, going to H2H  ---------------" + str(RawPointDuplicateCheck))
        
        H2H = head2head(RawPointDuplicateCheck, dbData)

        #If teams are still tied, allow PD to go into DB
        H2HDuplicate = duplicateChecker(allPointsByTeamDict, 'H2Hpoints')
        for team in H2HDuplicate:
            for teams_ID in H2HDuplicate[team]:
                stepReachedByTeamDict[teams_ID] = 3
        if not H2HDuplicate:
            #Must check if duplicate
            print("Worked out H2H!")
            rankBasedOn(mydb, cur, games, False, tournament_id, poolName)
            return True
        else:
            print("--------------- Duplicate still found, going to PD  ---------------")
            RawPointDuplicateCheckH2H2 =  duplicateChecker(allPointsByTeamDict, 'PDScore')
            #duplicateChecker(allPointsByTeamDict, 'TotalPoints')
            if not RawPointDuplicateCheckH2H2:
                
                print("--------------- No more duplicates, ending  ---------------")
                rankBasedOn(mydb, cur, games, False, tournament_id, poolName)
                return True

            print("--------------- Still duplicates, going to H2H2  ---------------")
            H2H2 = head2head(RawPointDuplicateCheckH2H2, dbData, True)
            RawPointDuplicateCheckH2H2Last =  duplicateChecker(allPointsByTeamDict, 'H2H2Score')
            if not RawPointDuplicateCheckH2H2Last:
                print("--------------- H2H2 worked out  ---------------")
                rankBasedOn(mydb, cur, games,False, tournament_id, poolName)
                return True
            print("--------------- Still duplicates, going to GoalsInFavor  ---------------")
            RawPointDuplicateCheckGIF =  duplicateChecker(allPointsByTeamDict, 'TotalPoints-GIF')
            
            if not RawPointDuplicateCheckGIF:
                print("--------------- GIF worked out  ---------------")
                rankBasedOn(mydb, cur, games,False, tournament_id, poolName)
                return True
            print("--------------- Giving up, cant compute ---------------")
            rankBasedOn(mydb, cur, games, False,tournament_id, poolName)
            
            return False
  
    else:
        print("No duplicates! Ending")
        rankBasedOn(mydb, cur, games, False, tournament_id, poolName)
        return True



###### Structure
# Whenever a score is submitted through the app:
# Post score to sign table
# Post set score to Volleyball table (if volleyball or newcomb game)
# Send Eyal tournament_id and pool for this game
# Recalculate standings for the entire pool (or tournament if there are no pools).
# SQL Statement that gets all the scores for that tournament/(pool)
# Call standings Function --> Dictionary of Team:Point pair:
# Calculates points based on win and loses
# if here are no duplicates, it calls rank
# If there are duplicates, it calls H2H -> add 1/10 to pointsTotal
# If H2H does not return duplicates, call rank 
# If H2H returns duplicates, calls PD -> add 1/100 to pointsTotal
# If PD returns no duplicates, call rank
# If PD returns duplicates, H2H again
# Rank function(pointsTotal):
# Assigns rank based on points
#  check duplicates just in case
# updates the standings table for this tournament
# H2H:
# goes to teams's tied game and gets the result
# assigns H2H Points:
# team won: 2 pts
# team lost: 0 points
# tied: 1 point each
# return H2H points for each team

def lambda_handler(tournament_id, poolName):
    
    #Connect to MySQL Database
    mydb = pymysql.connections.Connection(
      host=DATABASE_HOST,
      user=DATABASE_USERNAME,
      passwd=DATABASE_PASSWORD,
      autocommit=True
    
    )
    cur = mydb.cursor(pymysql.cursors.DictCursor)
    print("\n")
    #Gets all the games from the DB
    cur.execute("use mgdb")
    print("TournamentID is: " + str(tournament_id))
    if poolName in ['Pool A', 'Pool B', 'Pool C', 'Pool 0']:
        print("Pool is:",poolName)
        print("Starting to Calculate Standings")
        #returns the games played in the tournament/pool specified in the function called. Inludes rachmanus max and forfeit scores for each game
        cur.execute("Select distinct g.game_id, g.tournament_id, CONCAT(category,' ',gender,' ',t.sport) as tournament_name, p.pool, g.game_id, g.team1_id,  g.team2_id, score1, score2, rachmanus_max_pd as rachmanus, forfeit_score as forfeit from mgdb.sign as s  INNER JOIN mgdb.game as g on g.game_id = s.game_id   INNER JOIN mgdb.tournament as t on g.tournament_id = t.tournament_id  LEFT JOIN mgdb.pool as p on p.team_id = g.team1_id JOIN mgdb.sport as sp on t.sport=sp.sport  WHERE g.tournament_id = " + str(tournament_id) + " and p.pool = '" + poolName + "' AND t.tournament_id=p.tournament_id")
    else:
        print("Pool not recognized")
        #Not using this in 2018
        cur.execute("Select distinct g.game_id, g.tournament_id, CONCAT(category,' ',gender,' ',t.sport) as tournament_name, p.pool, g.game_id, g.team1_id,  g.team2_id, score1, score2, rachmanus_max_pd as rachmanus, forfeit_score as forfeit from mgdb.sign as s  INNER JOIN mgdb.game as g on g.game_id = s.game_id   INNER JOIN mgdb.tournament as t on g.tournament_id = t.tournament_id  LEFT JOIN mgdb.pool as p on p.team_id = g.team1_id JOIN mgdb.sport as sp on t.sport=sp.sport WHERE p.pool IS NULL AND t.tournament_id=p.tournament_id")
    
    global untiedLast
    untiedLast = []
    games = cur.fetchall()
    
    if len(games) == 0:
        print("There are no games for this tournament/pool combination")
        return False
    
    #creating dict for keeping track of all the scores
    global allPointsByTeamDict,totalPointsByTeamDict,stepReachedByTeamDict
    allPointsByTeamDict = {}
    totalPointsByTeamDict = {}
    
    #Used to know what steps each team has gone up to, so we can avoid putting it in the database
    stepReachedByTeamDict = {}
    calculateStandings(games, mydb, cur, tournament_id, poolName)
    cur.close()


if __name__ == "__main__":
    lambda_handler(81, "Pool 0")

def start(event, context):
    print("event is " + str(event))
    x = []
     #Delete values
    tournament_id = 0
    poolName = ""
    print("test")
    #payload=record["body"]
    payload = event['team']
    x = [x.strip() for x in payload.split(',')]
    print("Payload" + str(x))
    # x = [16, 'Pool A']
    start = time.time()

   

    #creating dict for keeping track of all the scores
    allPointsByTeamDict = {}
    totalPointsByTeamDict = {}

    #Used to know what steps each team has gone up to, so we can avoid putting it in the database
    stepReachedByTeamDict = {}
    cur = None

    mydb = None

    tournamentNumber = x[0]
    tournament_id = int(tournamentNumber)

    poolName = x[1]
    lambda_handler(tournament_id, poolName)
    
    end = time.time()
    print("Time: " + str(end-start))
    return True


# TeamStackup to.... 
# 1 - Raw points
# 2 - H2H points
# 3 - PD points
# 4 - H2H2
# 5 - Goals In favor
