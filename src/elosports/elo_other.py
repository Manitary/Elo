from collections import defaultdict
from operator import itemgetter

import pandas as pd
from sklearn.metrics import confusion_matrix


def k_factor(margin_of_victory: float, elo_diff: float) -> tuple[float, float]:
    init_k = 20
    if margin_of_victory > 0:
        multiplier = (margin_of_victory + 3) ** (0.8) / (7.5 + 0.006 * (elo_diff))
    else:
        multiplier = (-margin_of_victory + 3) ** (0.8) / (7.5 + 0.006 * (-elo_diff))
    return init_k * multiplier, init_k * multiplier


def s_value(home_score: float, away_score: float) -> tuple[float, float]:
    if home_score > away_score:
        return 1, 0
    if home_score < away_score:
        return 0, 1
    return 0.5, 0.5


def elo_update(
    home_score: float,
    away_score: float,
    home_rating: float,
    away_rating: float,
    home_advantage: float = 100.0,
) -> tuple[float, float]:
    home_rating += home_advantage
    elo_home = elo_prediction(home_rating, away_rating)
    elo_away = 1 - elo_home
    elo_diff = home_rating - away_rating
    mov = home_score - away_score

    s_home, s_away = s_value(home_score, away_score)
    if s_home > 0:
        k_home, k_away = k_factor(mov, elo_diff)
    else:
        k_home, k_away = k_factor(mov, elo_diff)

    return k_home * (s_home - elo_home), k_away * (s_away - elo_away)


def elo_prediction(home_rating: float, away_rating: float) -> float:
    return 1.0 / (1 + 10 ** ((away_rating - home_rating) / (400.0)))


def score_prediction(home_rating: float, away_rating: float) -> float:
    return (home_rating - away_rating) / 28.0


class EloSimulation:
    def __init__(
        self,
        games,
        update_function,
        label_dict,
        end_of_season_correction,
        prediction_function=None,
    ) -> None:
        self.update_function = update_function
        self.games = games
        self.ratings = {}
        self.prediction_function = prediction_function
        self.predictions = []
        self.curr_season = defaultdict(lambda: self.games[0][1][label_dict["year_id"]])
        self.end_of_season_correction = end_of_season_correction

    def train(self):
        for game in self.games:
            new_year = game[label_dict["year_id"]]
            label_i = game[label_dict["fran_id"]]
            label_j = game[label_dict["opp_fran"]]

            if self.ratings.get(label_i, False) == False:
                self.ratings[label_i] = elo_lookup(
                    label_i, game[label_dict["gameorder"]]
                )

            if self.ratings.get(label_j, False) == False:
                self.ratings[label_j] = elo_lookup(
                    label_j, game[label_dict["gameorder"]]
                )

            if self.curr_season[label_i] != new_year:
                self.curr_season[label_i] = new_year
                self.ratings[label_i] = self.ratings[label_i] * 0.6 + 1505.0 * 0.4
            elif self.curr_season[label_j] != new_year:
                self.curr_season[label_j] = new_year
                self.ratings[label_j] = self.ratings[label_j] * 0.6 + 1505.0 * 0.4
            self.predictions.append(
                elo_prediction(self.ratings[label_i] + 100, self.ratings[label_j])
            )
            # todo change below to just use event
            update = self.update_function(
                game[label_dict["pts"]],
                game[label_dict["opp_pts"]],
                self.ratings[label_i],
                self.ratings[label_j],
            )
            self.ratings[label_i] += update[0]
            self.ratings[label_j] += update[1]

    def power_rankings(self):
        power_rankings = sorted(self.ratings.items(), key=itemgetter(1), reverse=True)
        power = []
        for i, x in enumerate(power_rankings):
            power.append((i + 1, x))
        return power


label_dict = {
    "year_id": "year_id",
    "fran_id": "fran_id",
    "opp_fran": "opp_fran",
    "game_order": "game_order",
    "pts": "pts",
    "opp_pts": "opp_pts",
}
full_df = pd.read_csv("../../elo-simulations/nbaallelo.csv")
games = full_df[
    full_df["game_location"] == "H"
]  # remove duplicated rows work with our elo implementation
games["SEASON"] = games["year_id"].apply(lambda x: "%s-%s" % (x - 1, x))

STARTING_LOC = 0


def elo_lookup(fran_id, gameorder):
    return full_df[
        (full_df["fran_id"] == fran_id) & (full_df["game_order"] >= gameorder)
    ]["elo_i"].iloc[0]


m = EloSimulation(
    games=list(games[games["game_order"] > STARTING_LOC].iterrows()),
    update_function=elo_update,
    prediction_function=elo_prediction,
    label_dict=label_dict,
    end_of_season_correction=1,
)

m.train()
m.power_rankings()
games["prediction"] = m.predictions
games["predictedWinner"] = games["prediction"].apply(lambda x: 1 if x >= 0.5 else 0)
games["winner"] = games.apply(lambda x: x["pts"] >= x["opp_pts"], axis=1)


conf_matrix = confusion_matrix(games["winner"], games["predictedWinner"])

top = float(conf_matrix[0][0] + conf_matrix[1][1])
botton = top + float(conf_matrix[0][1] + conf_matrix[1][0])

print(top / botton * 100)
