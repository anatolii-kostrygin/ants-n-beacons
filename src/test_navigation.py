from pathlib import Path

from .main import read_initial, echo_input
from .reader import reader


reader.reset(Path("..") / "tests" / "initial_input.txt")


def test():
    print([x for x in Path(".").iterdir() if x.is_dir()])
    # with open(Path("..") / "tests" / "initial_input.txt", "r") as file:
    #     echo_input = file.readline
    #     print(echo_input())
    f = read_initial()
    # print(input())
    # print(input())
    assert 42 != 37
