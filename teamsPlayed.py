def didteamsplay(dbData, team1_id, team2_id):
    # team1Score = game['score1']
    # team2Score = game['score2']
    for game in dbData:
        if game['team1_id'] == team1_id and game['team2_id'] == team2_id:
            print(" 1 - Found a game where these teams played!" + str(game['team1_id']) + " vs " + str(game['team2_id']))
            # returnStatement = True
            return game
        if game['team1_id'] == team2_id and game['team2_id'] == team1_id: 
            print(" 2 - Found a game where these teams played!" + str(game['team1_id']) + " vs " + str(game['team2_id']))
            # returnStatement = True
            return game
    return False