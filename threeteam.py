from teamsPlayed import didteamsplay
import random

rankings = {}
# Contraints: no two teams can play each other more than once
firstPlace = 2
secondPlace = 1
thirdPlace = 0

def h2hThreeTeams(key, scores, dbData, scoresForPool, h2h2):
    

    print("3 teams are: " + str(key))
    scores = list(scores)
    team1 = scores[0]
    team2 = scores[1]
    team3 = scores[2]
    
    team_1vs2_winner = False
    team_1vs3_winner = False
    team_2vs3_winner = False
    gamesPlayed = []
    rankings = {}
    allGamesNonTie = 0

    team_1vs2 = didteamsplay(dbData, team1, team2)
    if team_1vs2:
        team_1vs2_winner = team_1vs2['winner_id']
        gamesPlayed.append(team_1vs2)

    team_1vs3 = didteamsplay(dbData, team1, team3)
    if team_1vs3:
        team_1vs3_winner = team_1vs3['winner_id']
        gamesPlayed.append(team_1vs3)

    team_2vs3 = didteamsplay(dbData, team2, team3)
    if team_2vs3:
        team_2vs3_winner = team_2vs3['winner_id']
        gamesPlayed.append(team_2vs3)

    teamWins = {scores[0]: 0, scores[1]: 0, scores[2]: 0}
    occuranceOfTeamPlays = {scores[0]: 0, scores[1]: 0, scores[2]: 0}
    
    rev_multidict = {}
    # occuranceOfTeamPlays = {}
    tiedGamesDict = {}
    
    #Check if a team is is in both of these 2 games played. If yes, we can narrow to case 7 or 8
    for teams in gamesPlayed:
        # xs
        if teams['winner_id'] == 0:
            allGamesNonTie += 1
            tiedGamesDict.setdefault(teams['team1_id'], 0)
            tiedGamesDict.setdefault(teams['team2_id'], 0)
            tiedGamesDict[teams['team1_id']] += 1
            tiedGamesDict[teams['team2_id']] += 1
            occuranceOfTeamPlays[teams['team1_id']] += 1
            occuranceOfTeamPlays[teams['team2_id']] += 1
            continue
        occuranceOfTeamPlays[teams['team1_id']] += 1
        occuranceOfTeamPlays[teams['team2_id']] += 1
        teamWins[teams['winner_id']] += 1
    for teamsPlayed in occuranceOfTeamPlays: #Reversing array to see who played and how many
            rev_multidict.setdefault(occuranceOfTeamPlays[teamsPlayed], set()).add(teamsPlayed)
    print("rev_multidict: " + str(rev_multidict))


    #Need to check if none of the games are tied to proceed below, if yes, go to another method

    if allGamesNonTie == 2: #Two games tied, so automatically case 13
        print("case 13: Two games tied")
        rankings[scores[0]] = secondPlace
        rankings[scores[1]] = secondPlace
        rankings[scores[2]] = secondPlace

        for team in rankings:
            if h2h2 == True:
                scoresForPool[team]['H2H2points'] = rankings[team]
            scoresForPool[team]['H2Hpoints'] = rankings[team]
        return True

    if allGamesNonTie > 0:
        print("Found a game that is tied, so going to rest of cases")
        tiedThreeWay(rankings, allGamesNonTie, occuranceOfTeamPlays, rev_multidict, tiedGamesDict, teamWins, dbData)
    
        for team in rankings:
            if h2h2 == True:
                scoresForPool[team]['H2H2points'] = rankings[team]
            scoresForPool[team]['H2Hpoints'] = rankings[team]
        return True


    ##Check if non of the games are tie
    if len(gamesPlayed) == 1:
        print("Case 5 - only 1 game played")
        rankings[scores[0]] = secondPlace
        rankings[scores[1]] = secondPlace
        rankings[scores[2]] = secondPlace

        for team in rankings:
            if h2h2 == True:
                scoresForPool[team]['H2H2points'] = rankings[team]
            scoresForPool[team]['H2Hpoints'] = rankings[team]
        return False

    if len(gamesPlayed) == 2:
        #If only 2 games were played between these 3 teams, we know
        # it must be either case: 6, 7 ,8, 
        teamplayedtwice = False

        print("2 games in between them")
    
        if rev_multidict[2]:
            #A team played twice (can only happen once, as per the contraint leading to this line)
            teamThatPlayedTwice = list(rev_multidict[2])[0]
            otherTeam1 = list(rev_multidict[1])[0]
            otherTeam2 = list(rev_multidict[1])[1]
            print("Team " + str(teamThatPlayedTwice) + " played twice")
            if teamWins.setdefault(teamThatPlayedTwice, None) == 1: 
                #If team that played twice only won once, 
                #we assume they are second place
                rankings[teamThatPlayedTwice] = secondPlace
                remainingTeam = didteamsplay(dbData, otherTeam1, otherTeam2 )
                if not remainingTeam:
                    print("Remaning teams did not play each other!")
                getWinnerVSOtherTeam1 = didteamsplay(dbData, teamThatPlayedTwice, otherTeam1 )
                getWinnerVSOtherTeam2 = didteamsplay(dbData, teamThatPlayedTwice, otherTeam2 )
                #Case 6
                    #I check if if team (2nd place) and a *random* team played, if they do, I know the loser is third place, opposite for first place
                    
                if getWinnerVSOtherTeam1:
                    if getWinnerVSOtherTeam1['winner_id'] == otherTeam1:
                        rankings[otherTeam1] = firstPlace
                        rankings[teamThatPlayedTwice] = secondPlace
                        rankings[otherTeam2] = thirdPlace
                if getWinnerVSOtherTeam2:
                    if getWinnerVSOtherTeam2['winner_id'] == otherTeam2:
                        rankings[otherTeam2] = firstPlace
                        rankings[teamThatPlayedTwice] = secondPlace
                        rankings[otherTeam1] = thirdPlace
                print(" case 6: I check if if team (2nd place) and a *random* team played, if they do, I know the loser is third place, opposite for first place")

            if teamWins.setdefault(teamThatPlayedTwice, None) == 2:
                #Case 8
                #If the team that played twice won twice, we know they are the winner 
                rankings[teamThatPlayedTwice] = firstPlace
                #The other two teams, as they did not play (b/c of contraints of 2 games played), the rest are second place
                rankings[otherTeam1] = secondPlace
                rankings[otherTeam2] = secondPlace
                print(" case 8: If the team that played twice won twice, we know they are the winner ")
                for team in rankings:
                    if h2h2 == True:
                        scoresForPool[team]['H2H2points'] = rankings[team]
                    scoresForPool[team]['H2Hpoints'] = rankings[team]
                return False

            if teamWins.setdefault(teamThatPlayedTwice, None) == 0:  
                #Case 7
                #If team that played twice lost both games (won 0) will be 3rd place
                print("case 7: If team that played twice lost both games (won 0) will be 3rd place")
                rankings[teamThatPlayedTwice] = secondPlace
                rankings[otherTeam1] = firstPlace
                rankings[otherTeam2] = firstPlace
                for team in rankings:
                    if h2h2 == True:
                        scoresForPool[team]['H2H2points'] = rankings[team]
                    scoresForPool[team]['H2Hpoints'] = rankings[team]
                return False

    if len(gamesPlayed) == 3:
        # If 3 games were played, we know it must be between: 9 or  15
        teamsThatPlayed = occuranceOfTeamPlays.copy()

        #We can do elimination. If a team won 2 games, they are winners (case 9)
        try:
            teamThatPlayedTwiceAndWonTwice = list(teamWins.keys())[list(teamWins.values()).index(2)]
            del occuranceOfTeamPlays[teamThatPlayedTwiceAndWonTwice]
            otherTeam1 = random.choice(list(occuranceOfTeamPlays))
            del occuranceOfTeamPlays[otherTeam1]
            otherTeam2 = random.choice(list(occuranceOfTeamPlays))
            del occuranceOfTeamPlays[otherTeam2]
            print("Team " + str(teamThatPlayedTwiceAndWonTwice) + " played twice")
            if teamWins.setdefault(teamThatPlayedTwiceAndWonTwice, None) == 2:
                #This has to be case 9
                print("Case 9")
                rankings[teamThatPlayedTwiceAndWonTwice] = firstPlace
                del teamsThatPlayed[teamThatPlayedTwiceAndWonTwice]
                getTeam1VSTeam2 = didteamsplay(dbData, otherTeam1, otherTeam2)
                print("getTeam1VSTeam2",getTeam1VSTeam2)
                if getTeam1VSTeam2:
                    winnerOfRemaining = getTeam1VSTeam2['winner_id']
                    rankings[winnerOfRemaining] = secondPlace
                    del teamsThatPlayed[winnerOfRemaining]
                    rankings[random.choice(list(teamsThatPlayed))] = thirdPlace

                    for team in rankings:
                        if h2h2 == True:
                            scoresForPool[team]['H2H2points'] = rankings[team]
                        scoresForPool[team]['H2Hpoints'] = rankings[team]
                    return True

        except:
            print("Case 15")
            for team in teamWins:
                rankings[team] = secondPlace
                print("Giving second place to " + str(team))
                for team in rankings:
                    if h2h2 == True:
                        scoresForPool[team]['H2H2points'] = rankings[team]
                    scoresForPool[team]['H2Hpoints'] = rankings[team]
            return False
            
            

        #case 15
        print("3 games in between them, more math :/ ")
    
    if len(rankings) == 3: #If this is true, rankings were set!

        for team in rankings:
            if h2h2 == True:
                scoresForPool[team]['H2H2points'] = rankings[team]
            scoresForPool[team]['H2Hpoints'] = rankings[team]
    for team in rankings:
        if h2h2 == True:
            scoresForPool[team]['H2H2points'] = rankings[team]
        scoresForPool[team]['H2Hpoints'] = rankings[team]
    return 0
#No team plays each other

def tiedThreeWay(rankings, allGamesNonTie, occuranceOfTeamPlays, rev_multidict, tiedGamesDict, teamWins, dbData):
    rev_tiedGamesDict = {}
    for teamsTied in tiedGamesDict: #Reversing array to see who played and how many
            rev_tiedGamesDict.setdefault(tiedGamesDict[teamsTied], set()).add(teamsTied)
    if rev_tiedGamesDict[1]:
        case11 = True
        try:
            if not list(teamWins.keys())[list(teamWins.values()).index(2)] == None: 
                print("Case 10 executed")
                teamWonTwice = list(teamWins.keys())[list(teamWins.values()).index(2)]
                rankings[teamWonTwice] = firstPlace
                del occuranceOfTeamPlays[teamWonTwice]

                tiedteam1 = random.choice(list(occuranceOfTeamPlays.keys()))
                rankings[tiedteam1] = secondPlace
                del occuranceOfTeamPlays[tiedteam1]

                tiedteam2 = random.choice(list(occuranceOfTeamPlays.keys()))
                rankings[tiedteam2] = secondPlace
                del occuranceOfTeamPlays[tiedteam2]
                case11 = False
                return False
        except: 
            print("")
        if case11:
            try:
                if list(teamWins.values()).count(1) == 2:
                    print("Case 11, meaning a team list twice")
                    losingTeam = list(teamWins.keys())[list(teamWins.values()).index(0)]
                    rankings[losingTeam] = secondPlace
                    del occuranceOfTeamPlays[losingTeam]

                    tiedteam1 = random.choice(list(occuranceOfTeamPlays.keys()))
                    rankings[tiedteam1] = firstPlace
                    del occuranceOfTeamPlays[tiedteam1]

                    tiedteam2 = random.choice(list(occuranceOfTeamPlays.keys()))
                    rankings[tiedteam2] = firstPlace
                    del occuranceOfTeamPlays[tiedteam2]
                    return False
            except:
                print("")
            try:
                playedOnce = rev_multidict[1]
                teamWonOnce = list(teamWins.keys())[list(teamWins.values()).index(1)]
                playedOnce = list(playedOnce)
                playedOncePlayeEachOther = didteamsplay(dbData,playedOnce[0], playedOnce[1])
                if not playedOncePlayeEachOther:
                    #Can be 12 or 14
                    print("Case 12 or 14")
                    twoTeamsTied = list(rev_tiedGamesDict[1])
                    
                    
                    copyTeamsPlayed = occuranceOfTeamPlays.copy()
                    del copyTeamsPlayed[twoTeamsTied[0]]
                    del copyTeamsPlayed[twoTeamsTied[1]]
                    teamLeft = random.choice(list(copyTeamsPlayed))

                    Team1PlayedNonTie = didteamsplay(dbData,twoTeamsTied[0], teamLeft)
                    Team2PlayedNonTie = didteamsplay(dbData,twoTeamsTied[1], teamLeft)

                    if Team1PlayedNonTie:
                        winnerOfTeamAndWonOnce = Team1PlayedNonTie['winner_id']
                    if Team2PlayedNonTie:
                        winnerOfTeamAndWonOnce = Team2PlayedNonTie['winner_id']
                    
                    if winnerOfTeamAndWonOnce == twoTeamsTied[0] or winnerOfTeamAndWonOnce == twoTeamsTied[1]:
                        print("case 14")
                        print("Winner is one of the tied games")
                        rankings[winnerOfTeamAndWonOnce] = thirdPlace
                        rankings[twoTeamsTied[0]] = secondPlace
                        rankings[twoTeamsTied[1]] = secondPlace
                        return True
                    else:
                        print("case 12")
                        rankings[winnerOfTeamAndWonOnce] = firstPlace
                        rankings[twoTeamsTied[0]] = secondPlace
                        rankings[twoTeamsTied[1]] = secondPlace
                        return True
            except:
                print("")
            print("Case not found")




