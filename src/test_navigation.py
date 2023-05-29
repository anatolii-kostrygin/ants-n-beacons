from pathlib import Path

from .main import read_initial, echo_input
from .reader import reader
from time import time


def test_read_initial_field():
    reader.reset(Path("..") / "tests" / "initial_input.txt")
    t0 = time()
    field = read_initial()
    print(f"Done in {time() - t0:.3f} seconds")

    for i in range(field.size):
        assert field.distances[i][i] == 0
