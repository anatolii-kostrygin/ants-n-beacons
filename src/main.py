import sys
import math


try:
    from .reader import reader
    input = reader.read_next_line
except:
    pass


ECHO = False


EGG = 1
CRYSTAL = 2
INFINITE_DISTANCE = 100500


def debug(s: str):
    print(s, file=sys.stderr, flush=True)


def echo_input():
    s = input()
    if ECHO:
        debug(s)
    return s


class Cell:
    def __init__(
        self, _type: int, resources: int, neighbors: tuple[int, int, int, int, int, int]
    ):
        self._type = _type
        self.resources = resources
        self.neighbors = neighbors

    def is_egg(self) -> bool:
        return self._type == EGG

    def is_crystal(self) -> bool:
        return self._type == CRYSTAL


class Field:
    def __init__(self, cells: list[Cell], my_base_index: int, opp_base_index: int):
        self.cells = cells
        self.my_base_index = my_base_index
        self.opp_base_index = opp_base_index

    @property
    def size(self) -> int:
        return len(self.cells)

    def compute_expected_length(self, total_ants: int) -> int:
        total_resources = sum(c.resources for c in self.cells)
        return total_resources // total_ants


def read_initial() -> Field:
    number_of_cells = int(echo_input())  # amount of hexagonal cells in this map
    cells = []
    for _ in range(number_of_cells):
        # _type: 0 for empty, 1 for eggs, 2 for crystal
        # initial_resources: the initial amount of eggs/crystals on this cell
        # neigh_0: the index of the neighbouring cell for each direction
        (
            _type,
            initial_resources,
            neigh_0,
            neigh_1,
            neigh_2,
            neigh_3,
            neigh_4,
            neigh_5,
        ) = [int(j) for j in echo_input().split()]
        cells.append(
            Cell(
                _type=_type,
                resources=initial_resources,
                neighbors=(neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5),
            )
        )
    number_of_bases = int(echo_input())
    for i in echo_input().split():
        my_base_index = int(i)
    for i in echo_input().split():
        opp_base_index = int(i)
    return Field(
        cells=cells, my_base_index=my_base_index, opp_base_index=opp_base_index
    )


def build_distances(field: Field, base_index: int) -> list[int]:
    """A simple BFS should work."""
    distances = [INFINITE_DISTANCE for _ in range(field.size)]
    distances[base_index] = 0
    queue = [base_index]
    i = 0
    while i < len(queue):
        i_curr = queue[i]
        for i_neighbor in field.cells[i_curr].neighbors:
            if i_neighbor != -1:
                if distances[i_neighbor] == INFINITE_DISTANCE:
                    queue.append(i_neighbor)
                distances[i_neighbor] = min(
                    distances[i_neighbor], distances[i_curr] + 1
                )
        i += 1
    return distances


def time_to_harvest(distance: int, resources: int, n_ants: int) -> int:
    # debug(f"{distance=} {resources=}")
    if n_ants < distance:
        return INFINITE_DISTANCE
    return distance + math.ceil(resources / (n_ants // distance))


def find_target(
    field: Field,
    distances: list[int],
    curr_state: list[tuple[int, int, int]],
    total_my_ants: int,
    i_move: int,
    expected_length: int
) -> int:
    best_score = -1
    best_target = -1
    for i, (resources, *_) in enumerate(curr_state):
        if resources > 0:
            tth = time_to_harvest(distances[i], resources, total_my_ants)
            score = resources // tth
            debug(f"{i} -> score: {score} ({tth=})")
            if field.cells[i].is_egg():
                if i_move == 1:
                    score += 100
                score -= -i_move * 4 / expected_length
            if score > best_score:
                best_score = score
                best_target = i
    return best_target


if __name__ == "__main__":
    field = read_initial()
    distances_from_my_base = build_distances(field, base_index=field.my_base_index)
    expected_length = None
    i_move = 0
    target = None
    # game loop
    while True:
        i_move += 1
        targets = []
        dist_to_resources = {}
        curr_state = []
        total_my_ants = 0
        total_opp_ants = 0
        for i in range(field.size):
            # resources: the current amount of eggs/crystals on this cell
            # my_ants: the amount of your ants on this cell
            # opp_ants: the amount of opponent ants on this cell
            resources, my_ants, opp_ants = [int(j) for j in echo_input().split()]
            total_my_ants += my_ants
            total_opp_ants += opp_ants
            curr_state.append((resources, my_ants, opp_ants))

        if expected_length is None:
            expected_length = field.compute_expected_length(total_my_ants + total_opp_ants)
            debug(f"{expected_length = }")

        if target is None or curr_state[target][0] == 0:
            target = find_target(field, distances_from_my_base, curr_state, total_my_ants, i_move, expected_length)

        if target != -1:
            print(f"LINE {field.my_base_index} {target} {1}")
        else:
            print("WAIT")

        #     if resources > 0:
        #         dist_to_resources[i] = distances_from_my_base[i]
        #         if field.cells[i].is_crystal() and i_move >= 4:
        #             targets.append((i, resources))
        #         elif i_move <= 5 and field.cells[i].is_egg():
        #             targets.append((i, resources))
        #         elif field.cells[i].is_egg():
        #             targets.append((i, resources // 2))
        #     debug(f"{dist_to_resources = }", file=sys.stderr, flush=True)
        #
        # debug(f"{targets = }", file=sys.stderr, flush=True)
        # actions = ';'.join(f"LINE {field.my_base_index} {i} {resources}" for i, resources in targets)
        # print(actions)

        # WAIT | LINE <sourceIdx> <targetIdx> <strength> | BEACON <cellIdx> <strength> | MESSAGE <text>
        # print("WAIT")
