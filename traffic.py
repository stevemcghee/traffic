import time
import os
import random
from enum import Enum

VERSION = "1.0"

# ANSI escape codes for colors
def get_color(color_code):
    return os.popen(f'tput setaf {color_code}').read()

class Color:
    GREEN = get_color(2)
    RED = get_color(1)
    YELLOW = get_color(3)
    RESET = os.popen('tput sgr0').read()

class Light(Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

UNLIT_BULB = "⚪"
LIGHT_SYMBOL = {
    Light.RED: f"{Color.RED}●{Color.RESET}",
    Light.YELLOW: f"{Color.YELLOW}●{Color.RESET}",
    Light.GREEN: f"{Color.GREEN}●{Color.RESET}",
}

# Grid dimensions
GRID_WIDTH = 21
GRID_HEIGHT = 21
INTERSECTION_SIZE = 1
ROAD_WIDTH = 1

# Calculated dimensions
LANE_N_X = GRID_WIDTH // 2 + 1
LANE_S_X = GRID_WIDTH // 2 - 1
LANE_E_Y = GRID_HEIGHT // 2 - 1
LANE_W_Y = GRID_HEIGHT // 2 + 1
INTERSECTION_START_X = (GRID_WIDTH // 2) - INTERSECTION_SIZE
INTERSECTION_END_X = (GRID_WIDTH // 2) + INTERSECTION_SIZE
INTERSECTION_START_Y = (GRID_HEIGHT // 2) - INTERSECTION_SIZE
INTERSECTION_END_Y = (GRID_HEIGHT // 2) + INTERSECTION_SIZE


class Car:
    def __init__(self, car_id, direction):
        self.id = car_id
        self.direction = direction
        self.color = Color.GREEN
        self.stopped = False
        if direction == "north":
            self.x, self.y = LANE_N_X, GRID_HEIGHT - 1
        elif direction == "south":
            self.x, self.y = LANE_S_X, 0
        elif direction == "east":
            self.x, self.y = 0, LANE_W_Y # Corrected: Eastbound cars use the lower lane
        elif direction == "west":
            self.x, self.y = GRID_WIDTH - 1, LANE_E_Y # Corrected: Westbound cars use the upper lane

    def __repr__(self):
        return f"{self.color}■{Color.RESET}"

    def move(self):
        if self.direction == "north":
            self.y -= 1
        elif self.direction == "south":
            self.y += 1
        elif self.direction == "east":
            self.x += 1
        elif self.direction == "west":
            self.x -= 1

class Intersection:
    def __init__(self, concurrent_cars, goal_cars):
        self.lights = {
            "north": Light.RED,
            "south": Light.RED,
            "east": Light.GREEN,
            "west": Light.GREEN,
        }
        self.cars = []
        self.passed_cars = 0
        self.concurrent_cars = concurrent_cars
        self.goal_cars = goal_cars
        self.cars_created = 0
        self.grid = [[" " for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        # Spawn initial cars
        for _ in range(self.concurrent_cars):
            self.spawn_car()

    def spawn_car(self):
        if self.cars_created >= self.goal_cars:
            return

        direction = random.choice(["north", "south", "east", "west"])
        new_car = Car(self.cars_created, direction)
        
        # Check if spawn point is occupied
        is_occupied = any(c.x == new_car.x and c.y == new_car.y for c in self.cars)
        if not is_occupied:
            self.cars.append(new_car)
            self.cars_created += 1

    def get_car_at(self, x, y):
        for car in self.cars:
            if car.x == x and car.y == y:
                return car
        return None

    def update_grid(self):
        # Reset grid
        self.grid = [[" " for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Draw roads
        for i in range(GRID_HEIGHT):
            self.grid[i][LANE_S_X] = "║"
            self.grid[i][LANE_N_X] = "║"
        for i in range(GRID_WIDTH):
            self.grid[LANE_E_Y][i] = "═"
            self.grid[LANE_W_Y][i] = "═"
        
        # Draw intersection
        self.grid[LANE_E_Y][LANE_S_X] = "╬"
        self.grid[LANE_E_Y][LANE_N_X] = "╬"
        self.grid[LANE_W_Y][LANE_S_X] = "╬"
        self.grid[LANE_W_Y][LANE_N_X] = "╬"

        # Draw lights at their correct positions, on the right side from the car's perspective.
        self.grid[INTERSECTION_START_Y - 2][LANE_S_X - 2] = LIGHT_SYMBOL[self.lights['south']] # For Southbound traffic
        self.grid[INTERSECTION_END_Y + 2][LANE_N_X + 2] = LIGHT_SYMBOL[self.lights['north']]   # For Northbound traffic
        self.grid[LANE_W_Y + 2][INTERSECTION_START_X - 2] = LIGHT_SYMBOL[self.lights['east']]   # For Eastbound traffic
        self.grid[LANE_E_Y - 2][INTERSECTION_END_X + 2] = LIGHT_SYMBOL[self.lights['west']]   # For Westbound traffic

        # Place cars
        for car in self.cars:
            if 0 <= car.x < GRID_WIDTH and 0 <= car.y < GRID_HEIGHT:
                self.grid[car.y][car.x] = repr(car)

    def print_state(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        self.update_grid()
        for row in self.grid:
            print("".join(row))
        
        print("--------------")
        print(f"Traffic Simulation v{VERSION}")
        print(f"Cars passed: {self.passed_cars}/{self.goal_cars}")

    def update_cars(self):
        for car in self.cars:
            car.stopped = False
            car.color = Color.GREEN # Default to green

            # Check light status first
            car_light = self.lights[car.direction]
            if car_light == Light.RED:
                car.color = Color.RED

            # Determine next position (one step ahead)
            next_x, next_y = car.x, car.y
            if car.direction == "north": next_y -= 1
            elif car.direction == "south": next_y += 1
            elif car.direction == "east": next_x += 1
            elif car.direction == "west": next_x -= 1

            # Determine buffer position (two steps ahead)
            buffer_x, buffer_y = next_x, next_y
            if car.direction == "north": buffer_y -= 1
            elif car.direction == "south": buffer_y += 1
            elif car.direction == "east": buffer_x += 1
            elif car.direction == "west": buffer_x -= 1
            
            # Check for stopping conditions
            is_car_1_step_ahead = self.get_car_at(next_x, next_y) is not None
            is_car_2_steps_ahead = self.get_car_at(buffer_x, buffer_y) is not None

            is_at_intersection = False
            if car.direction == "north" and car.y == INTERSECTION_END_Y + 1: is_at_intersection = True
            elif car.direction == "south" and car.y == INTERSECTION_START_Y - 1: is_at_intersection = True
            elif car.direction == "east" and car.x == INTERSECTION_START_X - 1: is_at_intersection = True
            elif car.direction == "west" and car.x == INTERSECTION_END_X + 1: is_at_intersection = True

            # A car stops if there's a car 1 or 2 steps ahead, or if it's at a non-green light.
            if is_car_1_step_ahead or is_car_2_steps_ahead or (is_at_intersection and car_light != Light.GREEN):
                car.stopped = True
                car.color = Color.RED
                continue
            
            car.move()

        # Remove cars that have left the grid
        cars_on_grid = []
        for car in self.cars:
            if 0 <= car.x < GRID_WIDTH and 0 <= car.y < GRID_HEIGHT:
                cars_on_grid.append(car)
            else:
                self.passed_cars += 1
        self.cars = cars_on_grid
        
        # Potentially spawn new cars
        if len(self.cars) < self.concurrent_cars:
             if random.random() < 0.5:
                self.spawn_car()

    def cycle(self):
        # --- North/South Green Phase ---
        self.lights["north"] = self.lights["south"] = Light.GREEN
        self.lights["east"] = self.lights["west"] = Light.RED
        for _ in range(10):
            if self.passed_cars >= self.goal_cars and len(self.cars) == 0: return
            self.update_cars()
            self.print_state()
            time.sleep(0.25)

        # --- North/South Yellow Phase ---
        self.lights["north"] = self.lights["south"] = Light.YELLOW
        for _ in range(3):
            if self.passed_cars >= self.goal_cars and len(self.cars) == 0: return
            self.update_cars()
            self.print_state()
            time.sleep(0.25)

        # --- All Red Phase ---
        for d in self.lights: self.lights[d] = Light.RED
        for _ in range(2):
            if self.passed_cars >= self.goal_cars and len(self.cars) == 0: return
            self.update_cars()
            self.print_state()
            time.sleep(0.25)

        # --- East/West Green Phase ---
        self.lights["east"] = self.lights["west"] = Light.GREEN
        self.lights["north"] = self.lights["south"] = Light.RED
        for _ in range(10):
            if self.passed_cars >= self.goal_cars and len(self.cars) == 0: return
            self.update_cars()
            self.print_state()
            time.sleep(0.25)

        # --- East/West Yellow Phase ---
        self.lights["east"] = self.lights["west"] = Light.YELLOW
        for _ in range(3):
            if self.passed_cars >= self.goal_cars and len(self.cars) == 0: return
            self.update_cars()
            self.print_state()
            time.sleep(0.25)

        # --- All Red Phase ---
        for d in self.lights: self.lights[d] = Light.RED
        for _ in range(2):
            if self.passed_cars >= self.goal_cars and len(self.cars) == 0: return
            self.update_cars()
            self.print_state()
            time.sleep(0.25)


if __name__ == "__main__":
    CARS_TO_PASS = 20
    intersection = Intersection(concurrent_cars=15, goal_cars=CARS_TO_PASS)
    try:
        while intersection.passed_cars < CARS_TO_PASS:
            intersection.cycle()
        
        # One final update to clear the screen
        while len(intersection.cars) > 0:
            intersection.update_cars()
            intersection.print_state()
            time.sleep(0.5)

        print(f"\nSimulation finished: {intersection.passed_cars} cars passed.")

    except KeyboardInterrupt:
        print("\nSimulation stopped.")