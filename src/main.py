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
        self, _type: int, resources: int, neighbors: tuple[int, int, int, int, int, int], my_ants: int, opp_ants: int
    ):
        self._type = _type
        self.resources = resources
        self.neighbors = neighbors
        self.my_ants = my_ants
        self.opp_ants = opp_ants

    def is_egg(self) -> bool:
        return self._type == EGG

    def is_crystal(self) -> bool:
        return self._type == CRYSTAL


class Field:
    def __init__(self, cells: list[Cell], my_base_index: int, opp_base_index: int):
        self.cells = cells
        self.my_base_index = my_base_index
        self.opp_base_index = opp_base_index

        self.distances = [self._build_distances_from(i) for i in range(self.size)]
        self.total_my_ants = 0
        self.total_opp_ants = 0

    @property
    def size(self) -> int:
        return len(self.cells)

    def compute_expected_length(self, total_ants: int) -> int:
        total_resources = sum(c.resources for c in self.cells)
        return total_resources // total_ants

    def _build_distances_from(self, base_index: int) -> list[int]:
        """A simple BFS should work."""
        distances = [INFINITE_DISTANCE for _ in range(self.size)]
        distances[base_index] = 0
        queue = [base_index]
        i = 0
        while i < len(queue):
            i_curr = queue[i]
            for i_neighbor in self.cells[i_curr].neighbors:
                if i_neighbor != -1:
                    if distances[i_neighbor] == INFINITE_DISTANCE:
                        queue.append(i_neighbor)
                    distances[i_neighbor] = min(
                        distances[i_neighbor], distances[i_curr] + 1
                    )
            i += 1
        return distances

    def cell_is_mine(self, i_cell) -> bool:
        return self.distances[i_cell][self.my_base_index] < self.distances[i_cell][self.opp_base_index]

    def cell_is_neutral(self, i_cell) -> bool:
        return self.distances[i_cell][self.my_base_index] == self.distances[i_cell][self.opp_base_index]

    def apply_update(self, upd: list[tuple[int, int, int]]):
        self.total_my_ants = 0
        self.total_opp_ants = 0
        for (resources, my_ants, opp_ants), cell in zip(upd, self.cells):
            cell.resources = resources
            cell.my_ants = my_ants
            cell.opp_ants = opp_ants
            self.total_my_ants += my_ants
            self.total_opp_ants += opp_ants


def read_initial() -> Field:
    number_of_cells = int(echo_input())
    cells = []
    for _ in range(number_of_cells):
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
                my_ants=0,
                opp_ants=0
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


def evaluate_target(field: Field, i_cell: int) -> tuple[int, float]:
    """ Max is better. First element is negative and is a priority (-1 == top-priority). 2nd is a "geometric" score. """
    cell = field.cells[i_cell]
    my_dist = field.distances[i_cell][field.my_base_index]
    dist_ratio = my_dist / field.distances[i_cell][field.opp_base_index]

    if cell.is_egg() and dist_ratio <= 0.66:
        return -1, -my_dist
    if cell.is_crystal() and 0.34 <= dist_ratio <= 1:
        return -2, time_to_harvest(my_dist, cell.resources, field.total_my_ants)
    if cell.is_egg() and dist_ratio <= 1.3:
        return -3, my_dist
    elif cell.is_crystal() and dist_ratio > 1:
        return -4, -my_dist
    elif cell.is_crystal() and dist_ratio < 0.34:
        return -5, 0
    return -7, 0  # lower priority for any other case


if __name__ == "__main__":
    field = read_initial()
    distances_from_my_base = field.distances[field.my_base_index]
    expected_length = None
    i_move = 0
    target = None
    my_cells = set()
    for i, cell in enumerate(field.cells):
        if cell.resources > 0 and field.cell_is_mine(i):
            debug(f"Cell {i} is mine")
            my_cells.add(i)

    # game loop
    while True:
        i_move += 1
        dist_to_resources = {}
        curr_state = []
        total_my_ants = 0
        total_opp_ants = 0
        upd = []
        for i in range(field.size):
            resources, my_ants, opp_ants = [int(j) for j in echo_input().split()]
            upd.append((resources, my_ants, opp_ants))
        field.apply_update(upd)

        #     total_my_ants += my_ants
        #     total_opp_ants += opp_ants
        #     curr_state.append((resources, my_ants, opp_ants))
        #
        # if expected_length is None:
        #     expected_length = field.compute_expected_length(total_my_ants + total_opp_ants)
        #     debug(f"{expected_length = }")
        #
        # if target is None or curr_state[target][0] == 0:
        #     target = find_target(field, distances_from_my_base, curr_state, total_my_ants, i_move, expected_length)
        #
        # if target != -1:
        #     print(f"LINE {field.my_base_index} {target} {1}")
        # else:
        #     print("WAIT")

        raw_targets = []
        for i, cell in enumerate(field.cells):
            if cell.resources > 0:
                score = evaluate_target(field, i)
                raw_targets.append((score, i))
        targets = []
        total_dist = 0
        for score, i_cell in sorted(raw_targets, reverse=True):
            distance_to_target = field.distances[i_cell][field.my_base_index]
            if total_dist + distance_to_target <= field.total_my_ants:
                targets.append((i_cell, 100))
                total_dist += distance_to_target
            # if cell.resources > 0 and i in my_cells:
            #     if field.cells[i].is_crystal() and i_move >= 4:
            #         targets.append((i, cell.resources))
            #     elif i_move <= 5 and field.cells[i].is_egg():
            #         targets.append((i, cell.resources))
            #     elif field.cells[i].is_egg():
            #         targets.append((i, cell.resources // 2))

        debug(f"{targets =}")
        if targets:
            actions = ';'.join(f"LINE {field.my_base_index} {i} {resources}" for i, resources in targets)
        else:
            actions = "WAIT"
        print(actions)
