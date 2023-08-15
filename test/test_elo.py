from typing import Any, Iterable, Protocol, Self

from elosports.elo import Elo


class Data(Protocol):
    season: int
    team1: str
    team2: str
    score1: int
    score2: int

    def iterrows(self) -> Iterable[tuple[Any, Self]]:
        ...


def test_elo(data_from_2000: Data) -> None:
    elo_league = Elo(k=20)

    all_teams = set(data_from_2000.team1)
    for team in all_teams:
        elo_league.add_player(team)

    current_season = 2000
    for _, game in data_from_2000.iterrows():
        if game.season > current_season:
            for key in elo_league.rating:
                elo_league.rating[key] -= (elo_league.rating[key] - 1500) * (1 / 3.0)
            current_season += 1

        if game.score1 > game.score2:
            elo_league.game_over(game.team1, game.team2, True)
        else:
            elo_league.game_over(game.team2, game.team1, False)

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

    assert elo_league.rating == expected
