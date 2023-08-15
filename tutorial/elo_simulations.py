import pandas as pd
import datetime
from elosports.elo import Elo

df = pd.read_csv("tutorial/nfl_elo.csv")
from2000 = df[(df["season"] > 1999)]
allTeams = set(from2000.team1.tolist())
eloLeague = Elo(k=20)

for team in allTeams:
    eloLeague.add_player(team)

currSeason = 2000
for game in from2000.iterrows():
    if game[1].season > currSeason:
        for key in eloLeague.rating.keys():
            eloLeague.rating[key] = eloLeague.rating[key] - (
                (eloLeague.rating[key] - 1500) * (1 / 3.0)
            )
        currSeason += 1

    if game[1].score1 > game[1].score2:
        eloLeague.game_over(game[1].team1, game[1].team2, True)
    else:
        eloLeague.game_over(game[1].team2, game[1].team1, 0)

expected = {
    "CLE": 1293.272678922271,
    "MIA": 1473.5556751810827,
    "SEA": 1550.203276467007,
    "LAC": 1490.2033076023486,
    "CHI": 1402.2094642282343,
    "PHI": 1601.9037319329573,
    "ARI": 1512.8812035074834,
    "NO": 1546.0878625024213,
    "PIT": 1604.234295044287,
    "KC": 1553.1312415504078,
    "CIN": 1482.639964298762,
    "CAR": 1554.6460851836562,
    "DET": 1519.1270502322766,
    "OAK": 1482.726134902254,
    "DAL": 1543.8482611792383,
    "LAR": 1501.8929694192843,
    "TB": 1448.2308676918867,
    "JAX": 1485.0278898852441,
    "SF": 1432.4506249961305,
    "DEN": 1480.120745652597,
    "HOU": 1433.1943390211604,
    "TEN": 1498.7369458530468,
    "WSH": 1483.7140067281027,
    "MIN": 1585.6534411377163,
    "NYG": 1430.6776258116151,
    "GB": 1512.2362952505803,
    "IND": 1431.6889473226995,
    "NE": 1657.9431100469733,
    "NYJ": 1431.2762743441174,
    "ATL": 1567.8375500311038,
    "BAL": 1502.8561644069798,
    "BUF": 1505.7919696660754,
}

print(eloLeague.rating == expected)
