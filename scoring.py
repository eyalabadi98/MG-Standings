import mysql.connector
import operator
from passwords import DATABASE_HOST,DATABASE_USERNAME,DATABASE_PASSWORD

#Connect to MySQL Database
mydb = mysql.connector.connect(
  host=DATABASE_HOST,
  user=DATABASE_USERNAME,
  passwd=DATABASE_PASSWORD,

)

print("\n")


mycursor = mydb.cursor(dictionary=True)
mycursor.execute("use mgdb")
# mycursor.execute("Select g.game_id, score1, score2, g.tournament_id, team1_id,team2_id, sport, gender, category from sign as s" 
# + " INNER JOIN game as g on g.game_id = s.game_id" 
# + " INNER JOIN tournament as t on g.tournament_id = t.tournament_id;")


mycursor.execute("Select g.tournament_id, CONCAT(category,' ',gender,' ',sport) as tournament_name, p.pool, g.game_id, g.team1_id,  g.team2_id, score1, score2 from sign as s"
+ " INNER JOIN game as g on g.game_id = s.game_id "
+" INNER JOIN tournament as t on g.tournament_id = t.tournament_id"
+ " INNER JOIN pool as p on p.team_id = g.team1_id")
pool = mycursor.fetchall()


# for item in pool:
#     print("Item: " + str(item))


#creating dict for keeping track of all the scores
scoresForPool = {
    
}

def calculateRawPoints(dataGames):
    # #Calculates raw points for the teams
    # print("Pool in Calculate: " + str(pool))
    for game in dataGames:
        # print("Game: " + str(game))
        givePoints(game)
        # print(game)
    # print("All Points" + str(scoresForPool))
    

def head2head(RawPointCheck,dbData):
    #Nothing yet
    # goes to teams's tied game and gets the result
    # assigns H2H Points:
    #   team won: 2 pts
    #   team lost: 0 points
    #   tied: 1 point each
    # return H2H points for each team
    gameH2HFound = None
    team1Score = ""
    team1Score = ""
    for key, scores in RawPointCheck.items():
        scores = list(scores)
        print("Repeating " + str(key))
        for game in dbData:
            team1Score = game['score1']
            team2Score = game['score2']
            # print("Each Game" + str(game))
            if game['team1_id'] == scores[0] and game['team2_id'] == scores[1]:
                # print(" 1 - Found a game where these teams played!")
                gameH2HFound = game['game_id']
                break
            if game['team1_id'] == scores[1] and game['team2_id'] == scores[0]:   
                # print(" 2 - Found a game where these teams played!")
                gameH2HFound = game['game_id']
                break

        if not gameH2HFound == None:
            if team1Score > team2Score:
                winner = game['team1_id']
            elif team1Score < team2Score:
                winner = game['team2_id']
            else:
                winner = 0
            return assignH2H(gameH2HFound, game['team1_id'], game['team2_id'], winner)
            
def assignH2H(game_id, team1, team2, winner):
    print("A game has been matched for H2H:  " + str(game_id) + " The winner is " + str(winner))
    if winner == "0":
        return
    scoresForPool[winner]['H2Hpoints'] += 2
    print("scoresForPool " + str(scoresForPool))
    return True




def initializeDictOfGames(team):
        #Initializing the dict when a team doesnt exists
        if not team in scoresForPool:
            scoresForPool[team] = { "rawPoints": 0, "H2Hpoints" : 0, 'P2PPoints': 0, }
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
        addPoints(team1, win)
        addPoints(team2,loss)
        scoreInfo['winner_id'] = scoreInfo['team1_id']
        scoreInfo['tie'] = False
        return
    elif score1 < score2:
        # print("Winner is score2")
        addPoints(team1, loss)
        addPoints(team2,win)
        scoreInfo['winner_id'] = scoreInfo['team2_id']
        scoreInfo['tie'] = False
        return
    else:
        # print("Tie")
        addPoints(team1, tie)
        addPoints(team2,tie)
        scoreInfo['winner_id'] = 0
        scoreInfo['tie'] = True
        return

def addPoints(team, addition):
    ##Generic function to add any type of points to a team
    # print("Adding " + str(addition) + " to: " + str(team))
    scoresForPool[team]['rawPoints'] += addition

def duplicateChecker(points, keyName):
    ##It checks if the points are duplicate so it knows if it succeeded
    rev_multidict = {}
    repeatData = {}
    repeat = False
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
    totalPointsForTeam = {}
    for team in scoresForPool:
        totalPointsForTeam[team] = scoresForPool[team]['rawPoints'] * 1 +  scoresForPool[team]['H2Hpoints'] * 0.1 + scoresForPool[team]['P2PPoints'] * 0.01
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
        print(" --------------- Duplicate found, going to H2H  ---------------")
        H2H = head2head(RawPointCheck, dbData)
        if H2H:
            "Worked out H2H!"
            rankBasedOn()
            return
        else:
            print("--------------- Duplicate still found, going to PD  ---------------")
            return
        # rankBasedOn(scoresForPool,"rawPoints")
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



calculateStandings(pool)

# givePoints(scoreInfo)
# print("Score " + str(scoreInfo))
# sortedTeams = rankBasedOn(points)

# if not sortedTeams:
#     print("Scores are equal!")
    #assign points based on H2H
# # print("Sorted Teams: " + sortedTeams)