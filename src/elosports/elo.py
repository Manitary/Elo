from typing import Hashable


class Elo:
    def __init__(self, k: int, g: int = 1, home_field: int = 100) -> None:
        self._rating: dict[Hashable, float] = {}
        self._k = k
        self._g = g
        self._home_field = home_field

    def add_player(self, name: Hashable, rating: float = 1500) -> None:
        self._rating[name] = rating

    def game_over(self, winner: Hashable, loser: Hashable, winner_home: bool) -> None:
        if winner_home:
            result = self.expect_result(
                self._rating[winner] + self._home_field, self._rating[loser]
            )
        else:
            result = self.expect_result(
                self._rating[winner], self._rating[loser] + self._home_field
            )

        self._rating[winner] += self._k * self._g * (1 - result)
        self._rating[loser] += self._k * self._g * (result - 1)

    def expect_result(self, p1: float, p2: float) -> float:
        exp = (p2 - p1) / 400.0
        return 1 / ((10.0 ** (exp)) + 1)

    @property
    def rating(self) -> dict[Hashable, float]:
        return self._rating

    # Backward compatibility
    # pylint: disable=invalid-name
    def addPlayer(self, name: Hashable, rating: float = 1500) -> None:
        return self.add_player(name, rating)

    def gameOver(self, winner: Hashable, loser: Hashable, winnerHome: bool) -> None:
        return self.game_over(winner, loser, winnerHome)

    def expectResult(self, p1: float, p2: float) -> float:
        return self.expect_result(p1, p2)

    @property
    def ratingDict(self) -> dict[Hashable, float]:
        return self._rating
