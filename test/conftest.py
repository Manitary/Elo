from typing import Generator

import pandas as pd
import pytest


@pytest.fixture
def data_from_2000() -> Generator[pd.DataFrame, None, None]:
    df = pd.read_csv("test/nfl_elo.csv")
    yield df[(df["season"] > 1999)]
