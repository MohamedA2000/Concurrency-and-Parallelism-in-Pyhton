import random
import time
import requests
import hashlib
import uuid
import os.path
import threading


def disarmMines(land):
    for i in range(len(land)):
        for j in range(len(land[0])):
            if land[i][j] == 1:
                land[i][j] = 0
    return land


# Generate the map and write it to a file only once
while True:
    grid_size = random.randint(10, 10)
    num_mines = random.randint(15, 28)
    if os.path.exists("map.txt"):
        with open("map.txt") as file:
            grid_size = int(file.readline().strip().split()[0])
            land = [[0 for x in range(grid_size)] for y in range(grid_size)] # creates a 2D list of size grid x grid and fill it with zeros.
            # iterates through grid size and stores integers into 'row'
            for i in range(grid_size):
                row = list(map(int, file.readline().strip().split()))
                # stores each integer from row into the corresponding position in the land list.
                for j in range(grid_size):
                    land[i][j] = row[j]
    else:
        land = [[0 for x in range(grid_size)] for y in range(grid_size)]
        mine_positions = random.sample(range(grid_size * grid_size), num_mines)
        # iterates over the random mine positions and sets random values to 1 to indicate a mine
        for position in mine_positions:
            row = position // grid_size
            col = position % grid_size
            land[row][col] = 1
            # writes results to map.txt file, leaving a space in between each integer and new line for each row
        with open("map.txt", "w") as file:
            file.write(str(grid_size) + " " + str(grid_size) + "\n")
            for row in land:
                file.write(" ".join([str(x) for x in row]) + "\n")
    break

# Iterate through the list of data for each rover
total_time = 0
# for i in range(1):
start_time = time.time()
# recieves data from the API using get request and then parsing the response as json data,
# and then storing the data in the 'moves' variable
response = requests.get(f'https://coe892.reev.dev/lab1/rover/10')
data = response.json()
moves = data["data"]["moves"]
print(moves)

# Initialize starting position and direction for the rover
x, y = 0, 0
direction = "S"


start_time = time.time()
path_grid = [[0 for x in range(grid_size)] for y in range(grid_size)]
# initializing indicator to indicate the starting position
path_grid[0][0] = "S"


# Process the commands for the rover
# skip move was previously used as a method to ignore all other commands, but is seldomly used now
skip_move = False
for index, move in enumerate(moves):
    if skip_move:
        skip_move = False
        continue
    if move == "M":
        if direction == "N" and y > 0:
            y -= 1
        elif direction == "S" and y < grid_size - 1:
            y += 1
        elif direction == "W" and x > 0:
            x -= 1
        elif direction == "E" and x < grid_size - 1:
            x += 1
    elif move == "L":
        if direction == "N":
            direction = "W"
        elif direction == "S":
            direction = "E"
        elif direction == "W":
            direction = "S"
        elif direction == "E":
            direction = "N"
    elif move == "R":
        if direction == "N":
            direction = "E"
        elif direction == "S":
            direction = "W"
        elif direction == "W":
            direction = "N"
        elif direction == "E":
            direction = "S"
    elif move == "D":
        path_grid[y][x] = "D"
        continue

    path_grid[y][x] = "*"
    # if the rover is on a mine, and next move isn't to disarm it, B will print and the loop will break,
    # ignoring the remaining command
    if land[y][x] == 1 and index + 1 < len(moves) and moves[index + 1] != "D":
        path_grid[y][x] = "B"
        break
    # if the rover is on a mine, and the next move is to disarm, the disarmMines function is called
    if land[y][x] == 1 and index + 1 < len(moves) and moves[index + 1] == "D":
        disarm_start_time = time.time()
        disarmMines(land)
        disarm_end_time = time.time()
        print(f"The Time it took for the rover to disram all mines in parallel: {disarm_end_time - disarm_start_time}")
        break






    # disarm mine function. When the rover lands on a mine, it gets assigned a serial number,
    # which is then added to a random pin to form the temp key. the temp key is then hashed until
    #the first six digits are 0, which means the PIN is valid. print statements are available to
    #record the values as well as the time it takes to complete the brute forcing

    def disarmMine(x,y):

        start_time_hash = time.time()
        serial = uuid.uuid4().hex
        pin = random.randint(1, 99999999999)
        tempKey = str(pin) + serial
        hash = hashlib.sha256(tempKey.encode()).hexdigest()
        while (not str(hash).startswith("000000")):
            pin = random.randint(1, 99999999999)
            tempKey = str(pin) + serial
            hash = hashlib.sha256(tempKey.encode()).hexdigest()
        print("Serial Number: " + serial)
        print("Temporary Key: " + tempKey)
        print("Hash Value: " + str(hash))
        end_time_hash = time.time()
        print(f"hashing time: {end_time_hash - start_time_hash}")

        return


    # iterates through the map, looking for mines (indicated as 1's). For those cells, a thread is created
    # (thread for each mine), with the disarmMine function as the target and (x,y) as arguments. The threads
    # are then stored in a list (threads), and once they are all finished executing, they are joined together
    # using t.join()

    def disarmMines(land):
        threads = []
        for y, row in enumerate(land):
            for x, cell in enumerate(row):
                if cell == 1:
                    print("Disarming")
                    t = threading.Thread(target=disarmMine, args=(x, y))
                    t.start()
                    threads.append(t)
        for t in threads:
            t.join()

        # this part here (below) is the same implementation but done sequentially
        # for y, row in enumerate(land):
        #     for x, cell in enumerate(row):
        #         if cell == 1:
        #             print("Currently disarming")
        #             disarmMine(x, y)
        #             path_grid[y][x] = "X"

with open(f"path_11.txt", "w") as file:
    for row in path_grid:
        file.write(" ".join([str(x) for x in row]) + "\n")

rover_time = time.time() - start_time
total_time += rover_time
print(f"Rover 11 took {time.time() - start_time} seconds to disarm all the mines")

print(f"Total time taken by all rovers to run sequentially is {total_time} seconds")

