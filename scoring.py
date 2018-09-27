import pymysql
import operator
from threeteam import case4
from passwords import DATABASE_HOST,DATABASE_USERNAME,DATABASE_PASSWORD
import time


#Connect to MySQL Database
mydb = pymysql.connections.Connection(
  host=DATABASE_HOST,
  user=DATABASE_USERNAME,
  passwd=DATABASE_PASSWORD,

)
cur = mydb.cursor(pymysql.cursors.DictCursor)
print("\n")

# mycursor = mydb.cursor(dictionary=True)
cur.execute("use mgdb")
# mycursor.execute("Select g.game_id, score1, score2, g.tournament_id, team1_id,team2_id, sport, gender, category from sign as s" 
# + " INNER JOIN game as g on g.game_id = s.game_id" 
# + " INNER JOIN tournament as t on g.tournament_id = t.tournament_id;")


cur.execute("Select g.tournament_id, CONCAT(category,' ',gender,' ',sport) as tournament_name, p.pool, g.game_id, g.team1_id,  g.team2_id, score1, score2 from sign as s"
+ " INNER JOIN game as g on g.game_id = s.game_id "
+" INNER JOIN tournament as t on g.tournament_id = t.tournament_id"
+ " INNER JOIN pool as p on p.team_id = g.team1_id")
pool = cur.fetchall()
cur.close()
#creating dict for keeping track of all the scores
scoresForPool = {}
totalPointsForTeam = {}
goalsforTeam = {}
PDforTeams = {}

def calculateRawPoints(dataGames):
    # #Calculates raw points for the teams
    print("Pool in Calculate: " + str(pool))
    for game in dataGames:
        # print("Game: " + str(game))
        givePoints(game)
        # print(game)
    # print("All Points" + str(scoresForPool))
    

def head2head(RawPointCheck,dbData):
    repeatAmount = len(RawPointCheck)
    returnStatement = True
    # goes to teams's tied game and gets the result
    # assigns H2H Points:
    #   team won: 2 pts
    #   team lost: 0 points
    #   tied: 1 point each
    # return H2H points for each team
    print("H2H here: " + str(repeatAmount))
    if repeatAmount > 1:
        ##If there are only 2 way-ties for points
        gameH2HFound = None
        team1Score = ""
        team1Score = ""
        # print("In Repeat Amount")
        for key, scores in RawPointCheck.items():
            scores = list(scores)
            print("Repeating " + str(scores))
            gameH2HFound = None
            for game in dbData:
                team1Score = game['score1']
                team2Score = game['score2']
                if game['team1_id'] == scores[0] and game['team2_id'] == scores[1]:
                    print(" 1 - Found a game where these teams played!" + str(game['team1_id']) + " vs " + str(game['team2_id']))
                    gameH2HFound = game['game_id']
                    # returnStatement = True
                    break
                if game['team1_id'] == scores[1] and game['team2_id'] == scores[0]:   
                    print(" 2 - Found a game where these teams played!" + str(game['team1_id']) + " vs " + str(game['team2_id']))
                    gameH2HFound = game['game_id']
                    # returnStatement = True
                    break
            print("gameH2HFound " +  str(gameH2HFound))
            if gameH2HFound != None:
                print("Game found")
                if team1Score > team2Score:
                    winner = game['team1_id']
                elif team1Score < team2Score:
                    winner = game['team2_id']
                else:
                    winner = 0
                assignH2H(gameH2HFound, game['team1_id'], game['team2_id'], winner)
            else:
                print("Game not found")
                team1 = scores[0]
                team2 = scores[1]
                scoresForPool[team1]['H2Hpoints'] = 1
                scoresForPool[team2]['H2Hpoints'] = 1
                scoresForPool[team1]['TotalPoints'] += 0.1
                scoresForPool[team2]['TotalPoints'] += 0.1
                returnStatement = False
                # for tied in RawPointCheck:
                #     print("scoresForPool: 95 " +  str(scoresForPool))
                #     teams = list(RawPointCheck[tied])
                #     print("Tied is " + str(teams))
                #     # games = list(tied)
                #     print("H2H game not found " + str(teams))
                #     team1 = teams[0]
                #     team2 = teams[1]
                #     scoresForPool[team1]['H2Hpoints'] = 1
                #     scoresForPool[team2]['H2Hpoints'] = 1
                #     scoresForPool[team1]['TotalPoints'] += 0.1
                #     scoresForPool[team2]['TotalPoints'] += 0.1
                continue
        return returnStatement
        # assignH2H(gameH2HFound, game['team1_id'], game['team2_id'], 0)
                # return assignH2H(gameH2HFound, game['team1_id'], game['team2_id'], 0)

    
    # if repeatAmount[0]  == 3 or repeatAmount[1]  == 3 or repeatAmount[2]  == 3 or repeatAmount[3]  == 3 or repeatAmount[4]  == 3:
    #     #Case 4 - No one plays anyone
    #     case4()
        #Case 5
    #No repeats in score H2H
    
    return
def assignH2H(game_id, team1, team2, winner):
    # print("A game has been matched for H2H:  " + str(game_id) + " The winner is " + str(winner))
    if winner == 0:
        print("Tied or not played!")
        # scoresForPool[winner]['H2Hpoints'] += 1
        return
    scoresForPool[winner]['H2Hpoints'] += 2
    scoresForPool[winner]['TotalPoints'] += 0.2

    #add tied game score
    # print("scoresForPool " + str(scoresForPool))
    return True

# def calculatePointsDiffforPD(data,team_id):
#     #Gets the data from all the games and calculates the point in favor minus the points scored on them
#     teamScorePositive = 0
#     teamScoreNegative = 0
#     for game in data:
#         if game['team1_id'] == team_id:
            
#             score = game['score1'] - game['score2']
#             teamScorePositive += score
#             print("Adding " + str(score) + " to " + str(team_id))
#             continue
#         if game['team2_id'] == team_id:
#             score = game['score2'] - game['score1']
#             teamScorePositive += score
#             print("Adding " + str(score) + " to " + str(team_id))
#             continue
#     difference = teamScorePositive - teamScoreNegative
#     goalsforTeam[team_id] = { "positive": teamScorePositive, 'negative': teamScoreNegative, 'difference': difference }
#     print("teamScorePositive for  "+str(team_id) + " is " +  str(teamScorePositive))
#     print("teamScoreNegative: " +  str(teamScoreNegative)) 
#     return difference    

def pointDifferential(data):
    #calculate total points scored for a given team minus total points scored on
    # teams = [8,10]

    # teamPD = []
    # # print("Data is " + str(data))
    # print("totalPointsForTeam " + str(scoresForPool))
    # # team = 6
    # for game in data:
    #     team1 = game['team1_id']
    #     team2 = game['team2_id']
        # print("Game is " +  str(game))
        # if 
        #     PointsScored[team1] = 


    #     PDCalculation = calculatePointsDiffforPD(data,team)
    #     print("PDCalculation: " + str(PDCalculation))
    #     teamPD.append(PDCalculation)  
    # print("TeamPD is "+ str(teamPD))
    # if teamPD[0] > teamPD[1]:
    #     print("Team1 Won PD")
    #     addPoints(teams[0], 2, 'PDPoints')
    #     addPoints(teams[0], 0.02, 'TotalPoints')
    # if teamPD[0] > teamPD[1]:
    #     print("Team2 Won PD")
    #     addPoints(teams[1], 2, 'PDPoints')
    #     addPoints(teams[1], 0.02, 'TotalPoints')
    # if teamPD[0] == teamPD[1]:
    #     print("PD had Tie")
    #     addPoints(teams[0], 1, 'PDPoints')
    #     addPoints(teams[1], 1, 'PDPoints')
    #     addPoints(teams[1], 0.01, 'TotalPoints')
    #     addPoints(teams[0], 0.01, 'TotalPoints')
    #Doesnt make sense as if it is over 9, it goes into tenths place
    # scoresForPool['PDPoints'] += PDCalculation
    return 0
def pushPointstoDB():
    for teams in scoresForPool:
        print("Teams: " + str(teams))
    sql = "UPDATE customers SET address = 'Canyon 123' WHERE address = 'Valley 345'"
    sql = "UPDATE `standings` SET h2h = 3, pd = 4, h2h2 = 0, final_rank = 1  WHERE tournament_id = 9 AND team_id = 10 "
    # mycursor.execute(sql)
    # mydb.commit()


def initializeDictOfGames(team):
        #Initializing the dict when a team doesnt exists
        if not team in scoresForPool:
            scoresForPool[team] = { "rawPoints": 0, "H2Hpoints" : 0, 'PDPoints': 0, 'TotalPoints': 0, 'PDScore': 0, 'PointsScoredOn': 0 }
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

    if score1 > score2:
        # print("Winner is score1")
        difference = scoreInfo['score1'] - scoreInfo['score2']
        addPoints(team1, difference, 'PDScore')
        addPoints(team2, (-1*difference), 'PDScore')
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
        addPoints(team1, loss, 'rawPoints')
        addPoints(team2,win, 'rawPoints')
        scoreInfo['winner_id'] = scoreInfo['team2_id']
        scoreInfo['tie'] = False
        return
    else:
        # print("Tie")
        addPoints(team1, tie, 'rawPoints')
        addPoints(team2,tie, 'rawPoints')
        scoreInfo['winner_id'] = 0
        scoreInfo['tie'] = True
        return

def addPoints(team, addition, pointName):
    ##Generic function to add any type of points to a team
    print("Adding " + str(addition) + " to: " + str(team))
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
        if keyName == "":
            rev_multidict.setdefault(value, set()).add(key)
        else:
            rev_multidict.setdefault(value[keyName], set()).add(key)
    for key, values in rev_multidict.items(): 
        if len(values) > 1:
            # Tell us which teams/score repeat
            repeatData[key] = values
            # print("Repeats " + str(values))
            # print("Repeats " + str(key))
            repeat = True
    print("Repeat Data: " + str(repeatData))
    return repeatData

def giveRanks(sorted_teams):
    ranks = []
    print('\n')
    for scores in sorted_teams:
        print("Final Standings: " + str(scores))
        ranks.append(scores[0])
    # print("ranks: " + str(ranks))
    print('\n')
    return ranks

def rankBasedOn():
    ##Puts the teams in order of ranks and places it on the database (not yet implemented)
    for team in scoresForPool:
        # if scoresForPool[team]['H2Hpoints'] >
        totalPointsForTeam[team] = scoresForPool[team]['rawPoints'] + (scoresForPool[team]['H2Hpoints'] * 0.1) + (scoresForPool[team]['PDScore'] * 0.001)
    print("totalPointsForTeam: " + str(totalPointsForTeam))
    sorted_teams = sorted(totalPointsForTeam.items(), key=lambda kv: kv[1], reverse=True)
    rankedTeams = giveRanks(sorted_teams)
    return rankedTeams
    
def MySQLCursorDictToDict(pool):
    dataDict = []
    for game in pool:
        dataDict.append(game)
    return dataDict

def calculateStandings(pool): 
    #Big Overall Method
    dbData = MySQLCursorDictToDict(pool)
    calculateRawPoints(pool)   
    
    # print("dbData: " + str(dbData))
    # print("Pool: " + pool)
    RawPointCheck = duplicateChecker(scoresForPool, "rawPoints")
    if len(RawPointCheck) > 0:
        print(" --------------- Duplicate found, going to H2H  ---------------" + str(RawPointCheck))
        
        H2H = head2head(RawPointCheck, dbData)
        if H2H:
            #Must check if duplicate
            print("Worked out H2H!")
            rankBasedOn()
            return
        else:
            print("--------------- Duplicate still found, going to PD  ---------------")
            duplicateChecker(scoresForPool, 'TotalPoints')
            rankBasedOn()
            return
  
    else:
        rankBasedOn()
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


#Main that gets called
start = time.time()

calculateStandings(pool)

end = time.time()
# print("Time to run " + str(end - start))