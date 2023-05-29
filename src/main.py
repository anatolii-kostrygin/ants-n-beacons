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


class PathNode:
    def __init__(self, id: int, i_next: int, i_sources: list[int]):
        self.id = id
        self.i_next = i_next
        self.i_sources = i_sources


class Field:
    def __init__(self, cells: list[Cell], my_base_index: int, opp_base_index: int):
        self.cells = cells
        self.my_base_index = my_base_index
        self.opp_base_index = opp_base_index

        self.distances = {i: self.build_distances_from((i,)) for i in range(self.size)}
        self.total_my_ants = 0
        self.total_opp_ants = 0

    @property
    def size(self) -> int:
        return len(self.cells)

    @property
    def total_crystals(self) -> int:
        return sum(c.resources for c in self.cells if c.is_crystal())

    @property
    def total_ants(self) -> int:
        return self.total_my_ants + self.total_opp_ants

    def compute_expected_length(self, total_ants: int) -> int:
        total_resources = sum(c.resources for c in self.cells)
        return total_resources // total_ants

    def build_distances_from(self, from_indexes: tuple[int]) -> list[int]:
        """Also a BFS, but starting from a set"""
        distances = [INFINITE_DISTANCE for _ in range(self.size)]
        for i in from_indexes:
            distances[i] = 0
        queue = [i for i in from_indexes]
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

    def build_path(self, i_sources: tuple[int], i_target: int, i_other_targets: list[int]) -> list[PathNode]:
        if i_sources not in self.distances:
            self.distances[i_sources] = self.build_distances_from(i_sources)
        dists = self.distances[i_sources]

        curr_distance = dists[i_target]
        i_curr_cell = i_target
        path = [PathNode(id=i_target, i_next=-1, i_sources=[i_target])]
        while curr_distance > 0:
            i_next_cells = [n for n in self.cells[i_curr_cell].neighbors if
                            n != -1 and dists[n] < curr_distance]
            i_curr_cell = find_best_next_cell(self, i_next_cells, i_other_targets)
            path[-1].i_next = i_curr_cell
            path.append(PathNode(id=i_curr_cell, i_next=-1, i_sources=[i_target]))
            curr_distance -= 1
        return path


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

    if cell.is_egg() and field.total_ants >= field.total_crystals:
        return -7, 0

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


def find_best_next_cell(field: Field, i_next_cells: list[int], i_targets: list[int]):
    if not i_targets:
        return i_next_cells[0]
    return min(i_next_cells, key=lambda i_cell: min(field.distances[i_cell][i_target] for i_target in i_targets))


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
                if score[0] != -7:
                    raw_targets.append((score, i))
        targets = []
        total_dist = 0
        sorted_raw_targets = sorted(raw_targets, reverse=True)
        for score, i_cell in sorted_raw_targets:
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
            path = {field.my_base_index: PathNode(field.my_base_index, i_next=-1, i_sources=[])}
            path_indexes = (field.my_base_index, )
            for _, i_target in sorted_raw_targets:
                i_other_targets = [it for _, it in sorted_raw_targets[1:]]
                path_segment = field.build_path(path_indexes, i_target, i_other_targets)
                for node in path_segment[:-1]:
                    if node.id in path_indexes:
                        raise ValueError(f"Found node {node.id} that is already on the path {path_indexes}")
                    path[node.id] = node
                i_next = path_segment[-1].id  # should be one of the targets
                while i_next != -1:
                    path[i_next].i_sources.append(i_target)
                    i_next = path[i_next].i_next
            actions = ";".join(f"BEACON {node.id} {100}" for node in path.values())
        else:
            actions = "WAIT"
        print(actions)
