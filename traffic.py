import time
import os
import random
from enum import Enum
import argparse

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
GRID_WIDTH = 25
GRID_HEIGHT = 25
INTERSECTION_SIZE = 1
ROAD_WIDTH = 1

# Calculated dimensions
LANE_N_X = GRID_WIDTH // 2 + 2
LANE_N_LEFT_X = GRID_WIDTH // 2 + 1
LANE_S_X = GRID_WIDTH // 2 - 2
LANE_S_LEFT_X = GRID_WIDTH // 2 - 1
LANE_E_Y = GRID_HEIGHT // 2 - 2
LANE_E_LEFT_Y = GRID_HEIGHT // 2 - 1
LANE_W_Y = GRID_HEIGHT // 2 + 2
LANE_W_LEFT_Y = GRID_HEIGHT // 2 + 1

INTERSECTION_START_X = (GRID_WIDTH // 2) - INTERSECTION_SIZE
INTERSECTION_END_X = (GRID_WIDTH // 2) + INTERSECTION_SIZE
INTERSECTION_START_Y = (GRID_HEIGHT // 2) - INTERSECTION_SIZE
INTERSECTION_END_Y = (GRID_HEIGHT // 2) + INTERSECTION_SIZE


class Car:
    def __init__(self, car_id, direction, turn=None):
        self.id = car_id
        self.direction = direction
        self.turn = turn
        self.color = Color.GREEN
        self.stopped = False
        
        if direction == "north":
            self.x = LANE_N_LEFT_X if self.turn == "left" else LANE_N_X
            self.y = GRID_HEIGHT - 1
        elif direction == "south":
            self.x = LANE_S_LEFT_X if self.turn == "left" else LANE_S_X
            self.y = 0
        elif direction == "east":
            self.x = 0
            self.y = LANE_E_LEFT_Y if self.turn == "left" else LANE_E_Y
        elif direction == "west":
            self.x = GRID_WIDTH - 1
            self.y = LANE_W_LEFT_Y if self.turn == "left" else LANE_W_Y

    def __repr__(self):
        return f"{self.color}■{Color.RESET}"

    def move(self):
        # Handle turns inside the intersection
        if self.turn == "left":
            if self.direction == "north" and self.y == LANE_W_LEFT_Y:
                self.direction = "west"
            elif self.direction == "south" and self.y == LANE_E_LEFT_Y:
                self.direction = "east"
            elif self.direction == "east" and self.x == LANE_N_LEFT_X:
                self.direction = "north"
            elif self.direction == "west" and self.x == LANE_S_LEFT_X:
                self.direction = "south"

        if self.direction == "north":
            self.y -= 1
        elif self.direction == "south":
            self.y += 1
        elif self.direction == "east":
            self.x += 1
        elif self.direction == "west":
            self.x -= 1

class TrafficPattern:
    def __init__(self, intersection):
        self.intersection = intersection
        self.lights = {}

    def cycle(self):
        raise NotImplementedError

class SimpleIntersection(TrafficPattern):
    def __init__(self, intersection):
        super().__init__(intersection)
        self.lights = {
            "north": Light.RED,
            "south": Light.RED,
            "east": Light.GREEN,
            "west": Light.GREEN,
        }

    def cycle(self):
        # --- North/South Green Phase ---
        self.lights["north"] = self.lights["south"] = Light.GREEN
        self.lights["east"] = self.lights["west"] = Light.RED
        for _ in range(10):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        # --- North/South Yellow Phase ---
        self.lights["north"] = self.lights["south"] = Light.YELLOW
        for _ in range(3):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        # --- All Red Phase ---
        for d in self.lights: self.lights[d] = Light.RED
        for _ in range(2):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        # --- East/West Green Phase ---
        self.lights["east"] = self.lights["west"] = Light.GREEN
        self.lights["north"] = self.lights["south"] = Light.RED
        for _ in range(10):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        # --- East/West Yellow Phase ---
        self.lights["east"] = self.lights["west"] = Light.YELLOW
        for _ in range(3):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        # --- All Red Phase ---
        for d in self.lights: self.lights[d] = Light.RED
        for _ in range(2):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

class ProtectedLeftTurn(TrafficPattern):
    def __init__(self, intersection):
        super().__init__(intersection)
        self.lights = {
            "north": Light.RED, "north_left": Light.RED,
            "south": Light.RED, "south_left": Light.RED,
            "east": Light.RED, "east_left": Light.RED,
            "west": Light.RED, "west_left": Light.RED,
        }

    def cycle(self):
        # Phase 1: North/South protected left turns
        self.lights["north_left"] = self.lights["south_left"] = Light.GREEN
        for _ in range(5):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)
        
        self.lights["north_left"] = self.lights["south_left"] = Light.YELLOW
        for _ in range(2):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        for d in self.lights: self.lights[d] = Light.RED
        for _ in range(2):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        # Phase 2: North/South straight traffic
        self.lights["north"] = self.lights["south"] = Light.GREEN
        for _ in range(8):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        self.lights["north"] = self.lights["south"] = Light.YELLOW
        for _ in range(3):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        for d in self.lights: self.lights[d] = Light.RED
        for _ in range(2):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        # Phase 3: East/West protected left turns
        self.lights["east_left"] = self.lights["west_left"] = Light.GREEN
        for _ in range(5):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        self.lights["east_left"] = self.lights["west_left"] = Light.YELLOW
        for _ in range(2):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        for d in self.lights: self.lights[d] = Light.RED
        for _ in range(2):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        # Phase 4: East/West straight traffic
        self.lights["east"] = self.lights["west"] = Light.GREEN
        for _ in range(8):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        self.lights["east"] = self.lights["west"] = Light.YELLOW
        for _ in range(3):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)

        for d in self.lights: self.lights[d] = Light.RED
        for _ in range(2):
            if self.intersection.is_finished(): return
            self.intersection.update_cars()
            self.intersection.print_state()
            time.sleep(0.25)


class Intersection:
    def __init__(self, concurrent_cars, goal_cars, pattern_class):
        self.cars = []
        self.passed_cars = 0
        self.concurrent_cars = concurrent_cars
        self.goal_cars = goal_cars
        self.cars_created = 0
        self.grid = [[" " for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.pattern = pattern_class(self)

        # Spawn initial cars
        for _ in range(self.concurrent_cars):
            self.spawn_car()

    def is_finished(self):
        return self.passed_cars >= self.goal_cars and len(self.cars) == 0

    def spawn_car(self):
        if self.cars_created >= self.goal_cars:
            return

        direction = random.choice(["north", "south", "east", "west"])
        turn = random.choice(["left", None]) if self.pattern.__class__ == ProtectedLeftTurn else None
        new_car = Car(self.cars_created, direction, turn)
        
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
        self.grid = [[" " for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Draw roads
        for i in range(GRID_HEIGHT):
            self.grid[i][LANE_S_X] = "║"
            self.grid[i][LANE_N_X] = "║"
            if self.pattern.__class__ == ProtectedLeftTurn:
                self.grid[i][LANE_S_LEFT_X] = "║"
                self.grid[i][LANE_N_LEFT_X] = "║"

        for i in range(GRID_WIDTH):
            self.grid[LANE_E_Y][i] = "═"
            self.grid[LANE_W_Y][i] = "═"
            if self.pattern.__class__ == ProtectedLeftTurn:
                self.grid[LANE_E_LEFT_Y][i] = "═"
                self.grid[LANE_W_LEFT_Y][i] = "═"
        
        # Draw intersection
        self.grid[LANE_E_Y][LANE_S_X] = "╬"
        self.grid[LANE_E_Y][LANE_N_X] = "╬"
        self.grid[LANE_W_Y][LANE_S_X] = "╬"
        self.grid[LANE_W_Y][LANE_N_X] = "╬"
        if self.pattern.__class__ == ProtectedLeftTurn:
            self.grid[LANE_E_LEFT_Y][LANE_S_LEFT_X] = "╬"
            self.grid[LANE_E_LEFT_Y][LANE_N_LEFT_X] = "╬"
            self.grid[LANE_W_LEFT_Y][LANE_S_LEFT_X] = "╬"
            self.grid[LANE_W_LEFT_Y][LANE_N_LEFT_X] = "╬"

        # Draw lights
        if isinstance(self.pattern, SimpleIntersection):
            self.grid[INTERSECTION_START_Y - 2][LANE_S_X - 2] = LIGHT_SYMBOL[self.pattern.lights['south']]
            self.grid[INTERSECTION_END_Y + 2][LANE_N_X + 2] = LIGHT_SYMBOL[self.pattern.lights['north']]
            self.grid[LANE_W_Y + 2][INTERSECTION_START_X - 2] = LIGHT_SYMBOL[self.pattern.lights['east']]
            self.grid[LANE_E_Y - 2][INTERSECTION_END_X + 2] = LIGHT_SYMBOL[self.pattern.lights['west']]
        elif isinstance(self.pattern, ProtectedLeftTurn):
            # Straight lights
            self.grid[INTERSECTION_START_Y - 2][LANE_S_X - 2] = LIGHT_SYMBOL[self.pattern.lights['south']]
            self.grid[INTERSECTION_END_Y + 2][LANE_N_X + 2] = LIGHT_SYMBOL[self.pattern.lights['north']]
            self.grid[LANE_W_Y + 2][INTERSECTION_START_X - 2] = LIGHT_SYMBOL[self.pattern.lights['east']]
            self.grid[LANE_E_Y - 2][INTERSECTION_END_X + 2] = LIGHT_SYMBOL[self.pattern.lights['west']]
            # Left turn lights
            self.grid[INTERSECTION_START_Y - 2][LANE_S_LEFT_X - 2] = LIGHT_SYMBOL[self.pattern.lights['south_left']]
            self.grid[INTERSECTION_END_Y + 2][LANE_N_LEFT_X + 2] = LIGHT_SYMBOL[self.pattern.lights['north_left']]
            self.grid[LANE_W_Y + 2][INTERSECTION_START_X - 2] = LIGHT_SYMBOL[self.pattern.lights['east_left']]
            self.grid[LANE_E_Y - 2][INTERSECTION_END_X + 2] = LIGHT_SYMBOL[self.pattern.lights['west_left']]


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
            car.color = Color.GREEN

            light_key = f"{car.direction}_left" if car.turn == "left" else car.direction
            car_light = self.pattern.lights.get(light_key, self.pattern.lights.get(car.direction))

            if car_light == Light.RED:
                car.color = Color.RED

            next_x, next_y = car.x, car.y
            if car.direction == "north": next_y -= 1
            elif car.direction == "south": next_y += 1
            elif car.direction == "east": next_x += 1
            elif car.direction == "west": next_x -= 1

            buffer_x, buffer_y = next_x, next_y
            if car.direction == "north": buffer_y -= 1
            elif car.direction == "south": buffer_y += 1
            elif car.direction == "east": buffer_x += 1
            elif car.direction == "west": buffer_x -= 1
            
            is_car_1_step_ahead = self.get_car_at(next_x, next_y) is not None
            is_car_2_steps_ahead = self.get_car_at(buffer_x, buffer_y) is not None

            is_at_intersection = False
            if car.direction == "north" and car.y == INTERSECTION_END_Y + 1: is_at_intersection = True
            elif car.direction == "south" and car.y == INTERSECTION_START_Y - 1: is_at_intersection = True
            elif car.direction == "east" and car.x == INTERSECTION_START_X - 1: is_at_intersection = True
            elif car.direction == "west" and car.x == INTERSECTION_END_X + 1: is_at_intersection = True

            if is_car_1_step_ahead or is_car_2_steps_ahead or (is_at_intersection and car_light != Light.GREEN):
                car.stopped = True
                car.color = Color.RED
                continue
            
            car.move()

        cars_on_grid = []
        for car in self.cars:
            if 0 <= car.x < GRID_WIDTH and 0 <= car.y < GRID_HEIGHT:
                cars_on_grid.append(car)
            else:
                self.passed_cars += 1
        self.cars = cars_on_grid
        
        if len(self.cars) < self.concurrent_cars:
             if random.random() < 0.5:
                self.spawn_car()

    def cycle(self):
        self.pattern.cycle()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traffic Simulation")
    parser.add_argument('--pattern', type=str, default='simple', choices=['simple', 'protected-left'],
                        help='Traffic pattern to simulate.')
    args = parser.parse_args()

    patterns = {
        'simple': SimpleIntersection,
        'protected-left': ProtectedLeftTurn
    }
    pattern_class = patterns[args.pattern]

    CARS_TO_PASS = 20
    intersection = Intersection(concurrent_cars=15, goal_cars=CARS_TO_PASS, pattern_class=pattern_class)
    try:
        while not intersection.is_finished():
            intersection.cycle()
        
        while len(intersection.cars) > 0:
            intersection.update_cars()
            intersection.print_state()
            time.sleep(0.5)

        print(f"\nSimulation finished: {intersection.passed_cars} cars passed.")

    except KeyboardInterrupt:
        print("\nSimulation stopped.")
