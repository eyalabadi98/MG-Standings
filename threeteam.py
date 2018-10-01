from teamsPlayed import didteamsplay
import random
def h2hThreeTeams(key, scores, dbData, scoresForPool):
    # Contraints: no two teams can play each other more than once
    firstPlace = 2
    secondPlace = 1
    thirdPlace = 0

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
    allGamesNonTie = True

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
    print("2 games in between them")
    #Check if a team is is in both of these 2 games played. If yes, we can narrow to case 7 or 8
    for teams in gamesPlayed:
        # xs
        occuranceOfTeamPlays[teams['team1_id']] += 1
        occuranceOfTeamPlays[teams['team2_id']] += 1
        teamWins[teams['winner_id']] += 1
    #Case6
    for teamsPlayed in occuranceOfTeamPlays: #Reversing array to see who played and how many
            rev_multidict.setdefault(occuranceOfTeamPlays[teamsPlayed], set()).add(teamsPlayed)
    print("rev_multidict: " + str(rev_multidict))



    ##Check if non of the games are tie
    if len(gamesPlayed) == 2:
        #If only 2 games were played between these 3 teams, we know
        # it must be either case: 6, 7 ,8, 
        teamplayedtwice = False

        
    
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
                getWinnerVSOtherTeam = didteamsplay(dbData, teamThatPlayedTwice, otherTeam1 )
                if getWinnerVSOtherTeam:
                    #Case 6
                    #I check if if team (2nd place) and a *random* team played, if they do, I know the loser is third place, opposite for first place
                    # rankings[teamThatPlayedTwice] = thirdPlace
                    if getWinnerVSOtherTeam['winner_id'] == otherTeam2:
                        rankings[otherTeam1] = thirdPlace
                        rankings[otherTeam2] = firstPlace
                    else:
                        rankings[otherTeam1] = firstPlace
                        rankings[otherTeam2] = thirdPlace
                    print(" case 6: I check if if team (2nd place) and a *random* team played, if they do, I know the loser is third place, opposite for first place")

            if teamWins.setdefault(teamThatPlayedTwice, None) == 2:
                #Case 8
                #If the team that played twice won twice, we know they are the winner 
                rankings[teamThatPlayedTwice] = firstPlace
                #The other two teams, as they did not play (b/c of contraints of 2 games played), the rest are second place
                rankings[otherTeam1] = secondPlace
                rankings[otherTeam2] = secondPlace
                print(" case 8: If the team that played twice won twice, we know they are the winner ")

            if teamWins.setdefault(teamThatPlayedTwice, None) == 0:  
                #Case 7
                #If team that played twice lost both games (won 0) will be 3rd place
                print("case 7: If team that played twice lost both games (won 0) will be 3rd place")
                rankings[teamThatPlayedTwice] = secondPlace
                rankings[otherTeam1] = firstPlace
                rankings[otherTeam2] = firstPlace

    if len(gamesPlayed) == 3:
        # If 3 games were played, we know it must be between: 9 or  15
        teamsThatPlayed = occuranceOfTeamPlays.copy()

        #We can do elimination. If a team won 2 games, they are winners (case 9)
        teamThatPlayedTwiceAndWonTwice = list(teamWins.keys())[list(teamWins.values()).index(2)]
        del occuranceOfTeamPlays[teamThatPlayedTwiceAndWonTwice]
        otherTeam1 = random.choice(occuranceOfTeamPlays.keys())
        del occuranceOfTeamPlays[otherTeam1]
        otherTeam2 = random.choice(occuranceOfTeamPlays.keys())
        del occuranceOfTeamPlays[otherTeam2]
        print("Team " + str(teamThatPlayedTwiceAndWonTwice) + " played twice")
        if teamWins.setdefault(teamThatPlayedTwiceAndWonTwice, None) == 2:
            #This has to be case 9
            print("Case 9")
            rankings[teamThatPlayedTwiceAndWonTwice] = firstPlace
            del teamsThatPlayed[teamThatPlayedTwiceAndWonTwice]
            getTeam1VSTeam2 = didteamsplay(dbData, otherTeam1, otherTeam2)
            if getTeam1VSTeam2:
                winnerOfRemaining = getTeam1VSTeam2['winner_id']
                rankings[winnerOfRemaining] = secondPlace
                del teamsThatPlayed[winnerOfRemaining]
                rankings[random.choice(teamsThatPlayed.keys())] = thirdPlace

        #case 15
        print("3 games in between them, more math :/ ")
    
    if len(rankings) == 3: #If this is true, rankings were set!
        for team in rankings:
            scoresForPool[team]['H2Hpoints'] += rankings[team]
    return 0
#No team plays each other
