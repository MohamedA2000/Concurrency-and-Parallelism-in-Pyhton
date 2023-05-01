import random
import time
import requests
import threading
import os.path


#GOOD COPY
# Generate the map and write it to a file only once
grid_size = random.randint(3, 9)
num_mines = random.randint(13, 22)
land = [[0 for x in range(grid_size)] for y in range(grid_size)]
mine_positions = random.sample(range(grid_size * grid_size), num_mines)
# iterates over the random mine positions and sets random values to 1 to indicate a mine
for position in mine_positions:
    row = position // grid_size
    col = position % grid_size
    land[row][col] = 1
    #WHEN THIS IS UNCOMMENTED, IF A MAP.TXT FILE ALREADY EXISTS IT WILL NOT OVERWRITE IT.
    # IF IT IS COMMENTED OUT, IT WILL CREATE A NEW MAP FILE EVEERYTIME
#if not os.path.exists("map.txt"):
    # writes results to map.txt file, leaving a space in between each integer and new line for each row
    with open("map.txt", "w") as file:
        file.write(str(grid_size) + " " + str(grid_size) + "\n")
        for row in land:
            file.write(" ".join([str(x) for x in row]) + "\n")

# Define a function for processing each rover in a separate thread
file_lock = threading.Lock()


def process_rover(i):
    #tracking time for rover
    total_time = 0
    start_time = time.time()
    # recieves data from the API using get request and then parsing the response as json data,
    # and then storing the data in the 'moves' variable
    response = requests.get(f'https://coe892.reev.dev/lab1/rover/{i}')
    data = response.json()
    moves = data["data"]["moves"]
    # print(f"Rover {i} moves: {moves}")

    # Initialize starting position and direction for the rover
    x, y = 0, 0
    direction = "S"
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
            # used state variables to assign a direction and adjust the grid location based on moves command
        if move == "M":
            if direction == "N" and y > 0:
                y -= 1
            elif direction == "S" and y < grid_size - 1:
                y += 1
            elif direction == "W" and x > 0:
                x -= 1
            elif direction == "E" and x < grid_size - 1:
                x += 1
                # changes direction based on move
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
        # ignoring the remaining commands
        if land[y][x] == 1 and index + 1 < len(moves) and moves[index + 1] != "D":
            path_grid[y][x] = "B"
            break


    # Write the path grid to a file
    with file_lock:
        with open(f"path_{i}.txt", "w") as file:
            for row in path_grid:
                file.write(" ".join([str(x) for x in row]) + "\n")

    rover_time = time.time() - start_time
    total_time += rover_time
    # print(f"Rover {i} took {time.time() - start_time} seconds to complete")

    # print(f"Total time taken by all rovers is {total_time} seconds")

if __name__ == "__main__":
    #threading lock used to synchronize access to resoucres for all threads (in theory)
    lock = threading.Lock()
    # execution time for sequential is calculated
    start_time_sequential = time.time()
    for i in range(1,11):
        process_rover(i)
    end_time_sequential = time.time()
    print(f"Time taken to run sequentially: {end_time_sequential - start_time_sequential}")


start_time = time.time()
# Create the lock
# file_lock = threading.Lock()


#recording time for thread execution
start_time_threads = time.time()
threads = []
#creates 10 threads, runs process rover function for each rover,
#stores the threads in a list. the threads are then executed and then joined together in a loop
# iterating through all the threads when done, and then joined together using t.join()
for i in range(1,11):
    t = threading.Thread(target=process_rover, args=(i,))
    threads.append(t)
    t.start()
for t in threads:
    t.join()
end_time_threads = time.time()
#prints execution time with threads, and then the difference between parallel and sequential
print(f"Time taken to run with threads: {end_time_threads - start_time_threads}")

print(f"The differene: {(end_time_sequential - start_time_sequential)- (end_time_threads - start_time_threads)}")


