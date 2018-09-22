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
pool = mycursor

#creating dict for keeping track of all the scores
scoresForPool = {
    
}




def calculateRawPoints(pool):
    #Calculates raw points for the teams
    for game in pool:
        # print("Game: " + str(game))
        givePoints(game)
        # print(game)
    # print("All Points" + str(scoresForPool))
    

def head2head(teamsInPool):
    #Nothing yet
    for teams in teamsInPool:
        print(teams)


def initializeDictOfGames(team):
        #Initializing the dict when a team doesnt exists
        if not team in scoresForPool:
            scoresForPool[team] = { "rawPoints": 0 }
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
        #print("Winner is score1")
        addPoints(team1, win)
        addPoints(team2,loss)
        scoreInfo['winner_id'] = scoreInfo['team1_id']
        scoreInfo['tie'] = False
        return
    elif score1 < score2:
        #print("Winner is score2")
        addPoints(team1, loss)
        addPoints(team2,win)
        scoreInfo['winner_id'] = scoreInfo['team2_id']
        scoreInfo['tie'] = False
        return
    else:
        #print("Tie")
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

    repeat = False
    #Inverts the dict to see if duplicates
    for key, value in points.items():
        rev_multidict.setdefault(value[keyName], set()).add(key)
    for key, values in rev_multidict.items(): 
        if len(values) > 1:
            # Tell us which teams/score repeat
            print("Repeats " + str(values))
            print("Repeats " + str(key))
            repeat = True
    return repeat


def rankBasedOn(points,keyName):
    ##Puts the teams in order of ranks and places it on the database (not yet implemented)
    sorted_teams = sorted(points.items(), key=lambda kv: kv[1], reverse=True)
    #looks at the entire points and see if there are two+ of the same
    if duplicateChecker(points, ""):
        #print("Duplicates found!")
        return False
    else:
        print("Sorted Teams: " + str(sorted_teams))
        return sorted_teams
    


def calculateStandings(): 
    #Big Overall Method
    calculateRawPoints(pool)
    if duplicateChecker(scoresForPool, "rawPoints"):
        rankBasedOn(scoresForPool,"")



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


# givePoints(scoreInfo)
# print("Score " + str(scoreInfo))
# sortedTeams = rankBasedOn(points)

# if not sortedTeams:
#     print("Scores are equal!")
#     #assign points based on H2H
# # print("Sorted Teams: " + sortedTeams)