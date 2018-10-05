from __future__ import print_function
import pymysql
import operator
from threeteam import h2hThreeTeams
from teamsPlayed import didteamsplay
from passwords import DATABASE_HOST,DATABASE_USERNAME,DATABASE_PASSWORD
import time


#Main that gets called
tournament_id = 9
poolName = 'Pool A'


#creating dict for keeping track of all the scores
scoresForPool = {}
totalPointsForTeam = {}
goalsforTeam = {}
PDforTeams = {}

#Used to know what steps each team has gone up to, so we can avoid putting it in the database
teamTrackUpToStep = {}
cur = None

mydb = None

def calculateRawPoints(pool):
    # #Calculates raw points for the teams
    print("Pool in Calculate: " + str(pool))
    for game in pool:
        # print("Game: " + str(game))
        givePoints(game)
        # print(game)
    # print("All Points" + str(scoresForPool))

def H2HgamenotFound(scores,scoresForPool):
    team1 = scores[0]
    team2 = scores[1]
    scoresForPool[team1]['H2Hpoints'] = 1
    scoresForPool[team2]['H2Hpoints'] = 1
    scoresForPool[team1]['TotalPoints'] += 0.1
    scoresForPool[team2]['TotalPoints'] += 0.1
    return False

def h2hTwoTeams(key, scores, RawPointCheck, dbData, h2h2h):
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
        assignH2H(game, game['team1_id'], game['team2_id'], winner, h2h2h)
    else:
        print("Game not found")
        team1 = scores[0]
        team2 = scores[1]
        scoresForPool[team1]['H2Hpoints'] = 1
        scoresForPool[team2]['H2Hpoints'] = 1
        scoresForPool[team1]['TotalPoints'] += 0.1
        scoresForPool[team2]['TotalPoints'] += 0.1
        returnStatement = False
    return returnStatement

def head2head(RawPointCheck,dbData, h2h2h=False):
    repeatAmount = len(RawPointCheck)
    returnStatement = True
    # goes to teams's tied game and gets the result
    # assigns H2H Points:
    #   team won: 2 pts
    #   team lost: 0 points
    #   tied: 1 point each
    # return H2H points for each team
    
    print("H2H here: " + str(repeatAmount))
    if repeatAmount >= 1:
        ##If there are only 2 way-ties for points
        gameH2HFound = None
        team1Score = ""
        team1Score = ""
        # print("In Repeat Amount")
        for key, scores in RawPointCheck.items():
            if h2h2h:
                for teams in scores:
                    teamTrackUpToStep[teams] = 4
            if not h2h2h:
                for teams in scores:
                    teamTrackUpToStep[teams] = 2
            if len(scores) == 2:
                returnStatement = h2hTwoTeams(key, scores, RawPointCheck, dbData, h2h2h)
            if len(scores) == 3:
                returnStatement = h2hThreeTeams(key, scores, dbData, scoresForPool, h2h2h)

    return returnStatement
def assignH2H(game_id, team1, team2, winner, h2h2=False):

    # print("A game has been matched for H2H:  " + str(game_id) + " The winner is " + str(winner))
    if h2h2:
        print("Tied or not played!")
        scoresForPool[team1]['H2H2points'] += 1
        scoresForPool[team2]['H2H2points'] += 1
        scoresForPool[team2]['TotalPoints'] += 0.1
        scoresForPool[team2]['TotalPoints'] += 0.1
        return
        
    if winner == 0:
        print("Tied or not played!")
        scoresForPool[team1]['H2Hpoints'] += 1
        scoresForPool[team2]['H2Hpoints'] += 1
        scoresForPool[team2]['TotalPoints'] += 0.1
        scoresForPool[team2]['TotalPoints'] += 0.1
        return
    teamTrackUpToStep[team1] = 2
    teamTrackUpToStep[team2] = 2
    scoresForPool[winner]['H2Hpoints'] += 2
    scoresForPool[winner]['TotalPoints'] += 0.2

    #add tied game score
    # print("scoresForPool " + str(scoresForPool))
    return True

def pushPointstoDB(scoresForPool,mydb, cur):
    # TeamStackup to.... 
    # 1 - Raw points
    # 2 - H2H points
    # 3 - PD points
    # 4 - H2H2
    # 5 - Goals In favor
    
    # h2hPoints = None
    # pdPoints = None
    # gif = None
    # h2h2Points = None
    for teams in scoresForPool:
        data  = scoresForPool[teams]
        tieBrakerReached = teamTrackUpToStep[teams]
        if tieBrakerReached == 1:
             sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, final_points, rank) values(%d, '%s', %d, %d, %d, %d, %d,%3.10f, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'], data['TotalPnt'],data['RankNumber'])
        if tieBrakerReached == 2:
            h2hPoints = data['H2Hpoints']
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, h2h, final_points, rank) values(%d, '%s', %d, %d, %d, %d, %d, %d,%3.10f, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'],h2hPoints, data['TotalPnt'],data['RankNumber'])
        if tieBrakerReached == 3:
            h2hPoints = data['H2Hpoints']
            pdPoints = data['PDScore']
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, h2h, pd, final_points, rank) values(%d, '%s', %d, %d, %d, %d, %d, %d, %d, %3.10f, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'],h2hPoints, pdPoints, data['TotalPnt'],data['RankNumber'])
        if tieBrakerReached == 4:
            h2hPoints = data['H2Hpoints']
            pdPoints = data['PDScore']
            h2h2Points = data['H2H2points']
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, h2h, pd, h2h2, final_points, rank) values(%d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %3.10f, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'],h2hPoints, pdPoints,h2h2Points, data['TotalPnt'],data['RankNumber'])
        if tieBrakerReached == 5:
            h2hPoints = data['H2Hpoints']
            pdPoints = data['PDScore']
            h2h2Points = data['H2H2points']
            pdPoints = data['PDScore']
            gif = data['GoalsInFavour']
            sql = "REPLACE into standings (tournament_id, pool, team_id, raw_points, wins, losses, ties, h2h, pd, h2h2, final_points, rank, gif ) values(%d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %3.10f, %d, %d)" % (tournament_id, poolName, teams, data['rawPoints'], data['Wins'], data['Losses'], data['Ties'],h2hPoints, pdPoints,h2h2Points, data['TotalPnt'],data['RankNumber'], gif)
        print("teams " + str(teams) + " teamTrackUpToStep: " + str(teamTrackUpToStep[teams]))
        print(sql)
        cur.execute(sql)
    return



def initializeDictOfGames(team):
        #Initializing the dict when a team doesnt exists
        if not team in scoresForPool:
            scoresForPool[team] = { "rawPoints": 0, "H2Hpoints" : 0, 'PDPoints': 0, 'TotalPoints': 0, 'PDScore': 0, 'GoalsInFavour': 0, 'PointsScoredOn': 0, 'Wins': 0 , 'Losses': 0, 'Ties': 0, 'RankNumber': 0, 'H2H2points': 0}
        return 0


def givePoints(scoreInfo):
    #Give RawPoints based on score and place them on the dict
    score1 = scoreInfo['score1']
    score2 = scoreInfo['score2']
    team1 = scoreInfo['team1_id']
    team2 = scoreInfo['team2_id']
    #What each win/loss/tie is worth
    win = 2
    loss = 0
    tie = 1
    initializeDictOfGames(team1)
    initializeDictOfGames(team2)

    #To keep track up to where each team has gone
    teamTrackUpToStep[team1] = 1
    teamTrackUpToStep[team2] = 1
    tournament_id = scoreInfo['tournament_id']

    addPoints(team1, score1, 'GoalsInFavour')
    addPoints(team2, score2, 'GoalsInFavour')

    if score1 > score2:
        # print("Winner is score1")
        difference = scoreInfo['score1'] - scoreInfo['score2']
        addPoints(team1, difference, 'PDScore')
        addPoints(team2, (-1*difference), 'PDScore')
        addPoints(team1, 1, 'Wins')
        addPoints(team2, 1, 'Losses')
        addPoints(team1, win, 'rawPoints')
        addPoints(team2,loss, 'rawPoints')
        scoreInfo['winner_id'] = scoreInfo['team1_id']
        scoreInfo['tie'] = False
        return
    elif score1 < score2:
        # print("Winner is score2")
        difference = scoreInfo['score2'] - scoreInfo['score1']
        addPoints(team2, difference, 'PDScore')
        addPoints(team1, (-1*difference), 'PDScore')
        addPoints(team2, 1, 'Wins')
        addPoints(team1, 1, 'Losses')
        addPoints(team1, loss, 'rawPoints')
        addPoints(team2,win, 'rawPoints')
        scoreInfo['winner_id'] = scoreInfo['team2_id']
        scoreInfo['tie'] = False
        return
    else:
        # print("Tie")
        addPoints(team1, tie, 'rawPoints')
        addPoints(team2,tie, 'rawPoints')
        addPoints(team1, 1, 'Ties')
        addPoints(team2, 1, 'Ties')
        scoreInfo['winner_id'] = 0
        scoreInfo['tie'] = True
        return

def addPoints(team, addition, pointName):
    ##Generic function to add any type of points to a team
    # print("Adding " + str(addition) + " to: " + str(team))
    if pointName == "rawPoints":
        scoresForPool[team]['TotalPoints'] += addition
    scoresForPool[team][pointName] += addition
    # 

def duplicateChecker(points, keyName):
    ##It checks if the points are duplicate so it knows if it succeeded
    rev_multidict = {}
    repeatData = {}
    # repeat = False
    print("Points: " + str(points))
    #Inverts the dict to see if duplicates
    for key, value in points.items():
        # print("KeyName dup " + str(value))
        if keyName == "":
            # print("KeyName dup")
            rev_multidict.setdefault(value, set()).add(key)
        if keyName == "H2Hpoints":
            totalPointsForTeamH2H = value['rawPoints'] + (value['H2Hpoints'] * 0.1)
            value['H2HUpToNow'] = totalPointsForTeamH2H
            print("TotalPnt  is " + str(totalPointsForTeamH2H))
            rev_multidict.setdefault(value['H2HUpToNow'], set()).add(key)
        elif keyName == "rawPoints":
            rev_multidict.setdefault(value['rawPoints'], set()).add(key)
        else:
            #To keep track up to where each team has gone
            totalPointsForTeam = value['rawPoints'] + (value['H2Hpoints'] * 0.1) + (value['PDScore'] * 0.0001) + (value['H2H2points'] * 0.00001) + (value['GoalsInFavour'] * 0.0000001)
            value['TotalPnt'] = totalPointsForTeam
            print("TotalPnt  is " + str(totalPointsForTeam))
            rev_multidict.setdefault(value['TotalPnt'], set()).add(key)
    for key, values in rev_multidict.items(): 
        if len(values) > 1:
            # Tell us which teams/score repeat
            repeatData[key] = values
            for items in values:
                if keyName == "TotalPoints":
                    teamTrackUpToStep[items] = 3
                if keyName == "TotalPoints-GIF":
                    teamTrackUpToStep[items] = 4
            # print("Repeats " + str(values))
            # print("Repeats " + str(key))
            repeat = True
    print("Repeat Data: " + str(repeatData))
    return repeatData

def giveRanks(sorted_teams):
    ranks = []
    print('\n')
    for standings, scores in enumerate(sorted_teams):
        print("Final Standings: " + str(scores))
        ranks.append(scores[0])
    # print("ranks: " + str(ranks))
    print('\n')
    return ranks

def rankBasedOn(mydb, cur):
    ##Puts the teams in order of ranks and places it on the database (not yet implemented)
    for team in scoresForPool:
        # if scoresForPool[team]['H2Hpoints'] >
        totalPointsForTeam[team] = scoresForPool[team]['rawPoints'] + (scoresForPool[team]['H2Hpoints'] * 0.1) + (scoresForPool[team]['PDScore'] * 0.0001 +  (scoresForPool[team]['H2H2points']) * 0.00001 + (scoresForPool[team]['GoalsInFavour'] * 0.0000001))
        scoresForPool[team]['TotalPnt'] = totalPointsForTeam[team]
    print("totalPointsForTeam: " + str(totalPointsForTeam))
    sorted_teams = sorted(totalPointsForTeam.items(), key=lambda kv: kv[1], reverse=True)
    for stand, teams in enumerate(sorted_teams):
        teams = teams[0]
        scoresForPool[teams]['RankNumber'] = (stand +1)
    rankedTeams = giveRanks(sorted_teams)
    pushPointstoDB(scoresForPool, mydb, cur)
    return rankedTeams
    
def MySQLCursorDictToDict(pool):
    dataDict = []
    for game in pool:
        dataDict.append(game)
    return dataDict

def calculateStandings(pool, mydb, cur): 
    #Big Overall Method
    dbData = MySQLCursorDictToDict(pool)
    calculateRawPoints(pool)   
    
    # print("dbData: " + str(dbData))
    # print("Pool: " + pool)
    RawPointCheck = duplicateChecker(scoresForPool, "rawPoints")
    if len(RawPointCheck) > 0:
        print(" --------------- Duplicate found, going to H2H  ---------------" + str(RawPointCheck))
        
        H2H = head2head(RawPointCheck, dbData)

        #If teams are still tied, allow PD to go into DB
        H2HDuplicate = duplicateChecker(scoresForPool, 'H2Hpoints')
        for team in H2HDuplicate:
            for teams_ID in H2HDuplicate[team]:
                teamTrackUpToStep[teams_ID] = 3
        if H2H:
            #Must check if duplicate
            print("Worked out H2H!")
            rankBasedOn(mydb, cur)
            return True
        else:
            print("--------------- Duplicate still found, going to PD  ---------------")
            RawPointCheckH2H2 =  duplicateChecker(scoresForPool, 'TotalPoints')
            if not RawPointCheckH2H2:
                
                print("--------------- No more duplicates, ending  ---------------")
                rankBasedOn(mydb, cur)
                return True

            print("--------------- Still duplicates, going to H2H2  ---------------")
            H2H2 = head2head(RawPointCheckH2H2, dbData, True)
            
            if H2H2:
                print("--------------- H2H2 worked out  ---------------")
                rankBasedOn(mydb, cur)
                return True
            print("--------------- Still duplicates, going to GoalsInFavor  ---------------")
            RawPointCheckGIF =  duplicateChecker(scoresForPool, 'TotalPoints-GIF')

            print("--------------- Giving up, cant compute ---------------")
            rankBasedOn(mydb, cur)
            
            return False
  
    else:
        rankBasedOn(mydb, cur)
        print("No duplicates! Ending")



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

def lambda_handler(event="", context=""):
    
    #Connect to MySQL Database
    mydb = pymysql.connections.Connection(
      host=DATABASE_HOST,
      user=DATABASE_USERNAME,
      passwd=DATABASE_PASSWORD,
      autocommit=True
    
    )
    cur = mydb.cursor(pymysql.cursors.DictCursor)
    print("\n")
    tournament_id = 9
    poolName = 'Pool A'
    # poolName = ""
    cur.execute("use mgdb")
    # mycursor = mydb.cursor(dictionary=True)
    if poolName in ['Pool A', 'Pool B', 'Pool C']:
        #print(pool)
        cur.execute("Select g.tournament_id, CONCAT(category,' ',gender,' ',sport) as tournament_name, p.pool, g.game_id, g.team1_id,  g.team2_id, score1, score2 from sign as s"
        + " INNER JOIN game as g on g.game_id = s.game_id "
        +" INNER JOIN tournament as t on g.tournament_id = t.tournament_id"
        + " LEFT JOIN pool as p on p.team_id = g.team1_id"
        + " WHERE g.tournament_id = " + str(tournament_id) + " and p.pool = '" + poolName + "'")
    else:
        #print(pool)
        cur.execute("Select g.tournament_id, CONCAT(category,' ',gender,' ',sport) as tournament_name, p.pool, g.game_id, g.team1_id,  g.team2_id, score1, score2 from sign as s"
        + " INNER JOIN game as g on g.game_id = s.game_id "
        +" INNER JOIN tournament as t on g.tournament_id = t.tournament_id"
        + " LEFT JOIN pool as p on p.team_id = g.team1_id"
        #+ " WHERE g.tournament_id = " + str(tournament_id) + " and p.pool IS NULL")
        + " WHERE p.pool IS NULL")

    
    
    pool = cur.fetchall()
    
    #creating dict for keeping track of all the scores
    scoresForPool = {}
    totalPointsForTeam = {}
    goalsforTeam = {}
    PDforTeams = {}
    
    #Used to know what steps each team has gone up to, so we can avoid putting it in the database
    teamTrackUpToStep = {}
    calculateStandings(pool, mydb, cur)
    cur.close()
    # for record in event['Records']:
    #    x = []
    #    print("test")
    #    payload=record["body"]
    #    [x.strip() for x in payload.split(',')]
    #    print("Payload" + str(payload))
    #    start = time.time()
       
    #    cur.close()
    #    end = time.time()
# print("Time to run " + str(end - start))


if __name__ == "__main__":
    lambda_handler()


# TeamStackup to.... 
# 1 - Raw points
# 2 - H2H points
# 3 - PD points
# 4 - H2H2
# 5 - Goals In favor