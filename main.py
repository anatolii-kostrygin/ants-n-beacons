import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

EGG = 1
CRYSTAL = 2

number_of_cells = int(input())  # amount of hexagonal cells in this map
cells = {}
for i in range(number_of_cells):
    # _type: 0 for empty, 1 for eggs, 2 for crystal
    # initial_resources: the initial amount of eggs/crystals on this cell
    # neigh_0: the index of the neighbouring cell for each direction
    _type, initial_resources, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    cells[i] = _type
number_of_bases = int(input())
for i in input().split():
    my_base_index = int(i)
for i in input().split():
    opp_base_index = int(i)

i_move = 0
# game loop
while True:
    i_move += 1
    targets = []
    for i in range(number_of_cells):
        # resources: the current amount of eggs/crystals on this cell
        # my_ants: the amount of your ants on this cell
        # opp_ants: the amount of opponent ants on this cell
        resources, my_ants, opp_ants = [int(j) for j in input().split()]

        if resources > 0:
            if cells[i] == CRYSTAL and i_move >= 4:
                targets.append((i, resources))
            elif i_move <= 5 and cells[i] == EGG:
                targets.append((i, resources))
            elif cells[i] == EGG:
                targets.append((i, resources // 2))

    print(f"{targets =}", file=sys.stderr, flush=True)
    actions = ';'.join(f"LINE {my_base_index} {i} {resources}" for i, resources in targets)
    print(actions)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # WAIT | LINE <sourceIdx> <targetIdx> <strength> | BEACON <cellIdx> <strength> | MESSAGE <text>
    # print("WAIT")
