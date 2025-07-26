# This entire script was written by the Gemini CLI.
#
#      *     *
#       \   /
#        \ /
#         *
#        / \
#       /   \
#      *-----*
#
# In lines of code, a story's told,
# Of traffic flowing, brave and bold.
# A digital hand, a thoughtful guide,
# Crafted this world, with Gemini inside.

import time
import os
import random
from enum import Enum
import argparse

VERSION = "1.0"
MAX_STEPS = 200

# ANSI escape codes for colors
def get_color(color_code):
    return os.popen(f'tput setaf {color_code}').read()

class Color:
    GREEN = get_color(2)
    RED = get_color(1)
    YELLOW = get_color(3)
    GREY = get_color(240)
    RESET = os.popen('tput sgr0').read()

class Light(Enum):
    GREEN = "GREEN"
    GREEN_ARROW = "GREEN_ARROW"
    YELLOW = "YELLOW"
    RED = "RED"

UNLIT_BULB = "⚪"
LIGHT_SYMBOL = {
    Light.RED: f"{Color.RED}●{Color.RESET}",
    Light.YELLOW: f"{Color.YELLOW}●{Color.RESET}",
    Light.GREEN: f"{Color.GREEN}●{Color.RESET}",
    Light.GREEN_ARROW: f"{Color.GREEN}◄{Color.RESET}",
    "RED_UNLIT": f"{Color.GREY}●{Color.RESET}",
    "YELLOW_UNLIT": f"{Color.GREY}●{Color.RESET}",
    "GREEN_UNLIT": f"{Color.GREY}●{Color.RESET}",
    "GREEN_ARROW_UNLIT": f"{Color.GREY}◄{Color.RESET}",
}

# Grid dimensions
GRID_WIDTH = 21
GRID_HEIGHT = 21
INTERSECTION_SIZE = 1

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
    def __init__(self, car_id, direction, turn=None):
        self.id = car_id
        self.direction = direction
        self.turn = turn
        self.color = Color.GREEN
        self.stopped = False
        
        if direction == "north":
            self.x, self.y = LANE_N_X, GRID_HEIGHT - 1
        elif direction == "south":
            self.x, self.y = LANE_S_X, 0
        elif direction == "east":
            self.x, self.y = 0, LANE_W_Y
        elif direction == "west":
            self.x, self.y = GRID_WIDTH - 1, LANE_E_Y

    def __repr__(self):
        return f"{self.color}■{Color.RESET}"

    def move(self):
        # Handle turns inside the intersection
        if self.turn == "left":
            turned = False
            # Northbound turning West
            if self.direction == "north" and self.y == LANE_E_Y:
                self.direction = "west"
                turned = True
            # Southbound turning East
            elif self.direction == "south" and self.y == LANE_W_Y:
                self.direction = "east"
                turned = True
            # Eastbound turning North
            elif self.direction == "east" and self.x == LANE_N_X:
                self.direction = "north"
                turned = True
            # Westbound turning South
            elif self.direction == "west" and self.x == LANE_S_X:
                self.direction = "south"
                turned = True
            
            if turned:
                self.turn = None

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

    def _run_phase(self, duration):
        for _ in range(duration):
            if self.intersection.is_finished():
                return True # Indicate simulation should stop
            self.intersection.steps += 1
            self.intersection.update_cars()
            if not self.intersection.is_test_mode:
                self.intersection.print_state()
                time.sleep(0.25)
        return False # Indicate phase complete, continue simulation

    def cycle(self):
        raise NotImplementedError

class SimpleIntersection(TrafficPattern):
    def __init__(self, intersection):
        super().__init__(intersection)
        self.lights = {
            "north": Light.RED, "south": Light.RED,
            "east": Light.GREEN, "west": Light.GREEN,
        }

    def cycle(self):
        self.lights.update({"north": Light.GREEN, "south": Light.GREEN, "east": Light.RED, "west": Light.RED})
        if self._run_phase(10): return
        self.lights.update({"north": Light.YELLOW, "south": Light.YELLOW})
        if self._run_phase(3): return
        self.lights.update({"north": Light.RED, "south": Light.RED, "east": Light.RED, "west": Light.RED})
        if self._run_phase(2): return
        self.lights.update({"east": Light.GREEN, "west": Light.GREEN, "north": Light.RED, "south": Light.RED})
        if self._run_phase(10): return
        self.lights.update({"east": Light.YELLOW, "west": Light.YELLOW})
        if self._run_phase(3): return
        self.lights.update({"north": Light.RED, "south": Light.RED, "east": Light.RED, "west": Light.RED})
        if self._run_phase(2): return

class ProtectedLeftTurn(TrafficPattern):
    def __init__(self, intersection):
        super().__init__(intersection)
        self.lights = {
            "north": Light.RED, "south": Light.RED,
            "east": Light.RED, "west": Light.RED,
        }

    def cycle(self):
        # --- North/South Cycle ---
        self.lights.update({"north": Light.GREEN_ARROW, "south": Light.GREEN_ARROW, "east": Light.RED, "west": Light.RED})
        if self._run_phase(5): return
        self.lights.update({"north": Light.GREEN, "south": Light.GREEN})
        if self._run_phase(8): return
        self.lights.update({"north": Light.YELLOW, "south": Light.YELLOW})
        if self._run_phase(3): return
        self.lights.update({"north": Light.RED, "south": Light.RED, "east": Light.RED, "west": Light.RED})
        if self._run_phase(2): return

        # --- East/West Cycle ---
        self.lights.update({"east": Light.GREEN_ARROW, "west": Light.GREEN_ARROW, "north": Light.RED, "south": Light.RED})
        if self._run_phase(5): return
        self.lights.update({"east": Light.GREEN, "west": Light.GREEN})
        if self._run_phase(8): return
        self.lights.update({"east": Light.YELLOW, "west": Light.YELLOW})
        if self._run_phase(3): return
        self.lights.update({"north": Light.RED, "south": Light.RED, "east": Light.RED, "west": Light.RED})
        if self._run_phase(2): return

def get_light_parts(light_state, is_protected_turn=False):
    parts = []
    parts.append(LIGHT_SYMBOL[Light.RED] if light_state == Light.RED else LIGHT_SYMBOL["RED_UNLIT"])
    parts.append(LIGHT_SYMBOL[Light.YELLOW] if light_state == Light.YELLOW else LIGHT_SYMBOL["YELLOW_UNLIT"])
    if is_protected_turn:
        parts.append(LIGHT_SYMBOL[Light.GREEN] if light_state == Light.GREEN else LIGHT_SYMBOL["GREEN_UNLIT"])
        parts.append(LIGHT_SYMBOL[Light.GREEN_ARROW] if light_state == Light.GREEN_ARROW else LIGHT_SYMBOL["GREEN_ARROW_UNLIT"])
    else:
        parts.append(LIGHT_SYMBOL[Light.GREEN] if light_state == Light.GREEN else LIGHT_SYMBOL["GREEN_UNLIT"])
    return parts

class Intersection:
    def __init__(self, concurrent_cars, goal_cars, pattern_class, is_test_mode=False, left_turn_percentage=None, distribution_factor=1.0, ignore_crashes=False):
        self.cars = []
        self.passed_cars = 0
        self.concurrent_cars = concurrent_cars
        self.goal_cars = goal_cars
        self.cars_created = 0
        self.grid = [[" " for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.pattern = pattern_class(self)
        self.is_test_mode = is_test_mode
        self.steps = 0
        self.crashes = 0
        self.left_turn_percentage = left_turn_percentage
        self.distribution_factor = distribution_factor
        self.ignore_crashes = ignore_crashes
        self._spawn_direction_pool = []
        self._generate_spawn_pool()
        if not is_test_mode:
            for _ in range(self.concurrent_cars):
                self.spawn_car()

    def _generate_spawn_pool(self):
        directions = ["north", "south", "east", "west"]
        pool = []
        
        num_even_cars = round(self.goal_cars * self.distribution_factor)
        num_random_cars = self.goal_cars - num_even_cars

        # Add evenly distributed cars
        for i in range(num_even_cars):
            pool.append(directions[i % 4])
        
        # Add randomly distributed cars
        if num_random_cars > 0:
            random_direction = random.choice(directions)
            for _ in range(num_random_cars):
                pool.append(random_direction)
        
        random.shuffle(pool)
        self._spawn_direction_pool = pool

    def is_finished(self):
        return self.passed_cars >= self.goal_cars or self.steps >= MAX_STEPS or (self.crashes > 0 and not self.ignore_crashes)

    def spawn_car(self):
        if len(self.cars) >= self.concurrent_cars or not self._spawn_direction_pool:
            return

        direction = self._spawn_direction_pool[-1]
        temp_car = Car(self.cars_created, direction)
        if any(c.x == temp_car.x and c.y == temp_car.y for c in self.cars):
            random.shuffle(self._spawn_direction_pool)
            return

        self._spawn_direction_pool.pop()
        turn = None
        if isinstance(self.pattern, ProtectedLeftTurn):
            if self.left_turn_percentage and random.random() < self.left_turn_percentage:
                turn = "left"
        
        new_car = Car(self.cars_created, direction, turn)
        self.cars.append(new_car)
        self.cars_created += 1

    def get_car_at(self, x, y):
        return next((car for car in self.cars if car.x == x and car.y == y), None)

    def update_grid(self):
        self.grid = [[" " for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for i in range(GRID_HEIGHT):
            self.grid[i][LANE_S_X] = "║"; self.grid[i][LANE_N_X] = "║"
        for i in range(GRID_WIDTH):
            self.grid[LANE_E_Y][i] = "═"; self.grid[LANE_W_Y][i] = "═"
        self.grid[LANE_E_Y][LANE_S_X] = "╬"; self.grid[LANE_E_Y][LANE_N_X] = "╬"
        self.grid[LANE_W_Y][LANE_S_X] = "╬"; self.grid[LANE_W_Y][LANE_N_X] = "╬"

        is_protected = isinstance(self.pattern, ProtectedLeftTurn)
        light_parts_s = get_light_parts(self.pattern.lights['south'], is_protected)
        for i, p in enumerate(light_parts_s): self.grid[INTERSECTION_START_Y - 1 - i][LANE_S_X - 2] = p
        light_parts_n = get_light_parts(self.pattern.lights['north'], is_protected)
        for i, p in enumerate(light_parts_n): self.grid[INTERSECTION_END_Y + 1 + i][LANE_N_X + 2] = p
        light_parts_e = get_light_parts(self.pattern.lights['east'], is_protected)
        self.grid[LANE_W_Y + 2][INTERSECTION_START_X - 1 - len(light_parts_e) : INTERSECTION_START_X - 1] = light_parts_e
        light_parts_w = get_light_parts(self.pattern.lights['west'], is_protected)
        self.grid[LANE_E_Y - 2][INTERSECTION_END_X + 2 : INTERSECTION_END_X + 2 + len(light_parts_w)] = light_parts_w

        for car in self.cars:
            if 0 <= car.y < GRID_HEIGHT and 0 <= car.x < GRID_WIDTH:
                self.grid[car.y][car.x] = repr(car)

    def print_state(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        self.update_grid()
        print(f"Running pattern: {self.pattern.__class__.__name__}")
        for row in self.grid: print("".join(row))
        print("--------------")
        print(f"Traffic Simulation v{VERSION} (Step: {self.steps})")
        print(f"Cars Started: {self.cars_created}/{self.goal_cars}")
        print(f"Cars Finished: {self.passed_cars}/{self.goal_cars}")
        if self.crashes > 0:
            print(f"Crashes: {self.crashes}")

    def update_cars(self):
        intended_moves = {}
        for car in self.cars:
            car.stopped = False; car.color = Color.GREEN
            light = self.pattern.lights[car.direction]
            should_stop_for_light = (car.turn == "left" and light != Light.GREEN_ARROW) or \
                                    (car.turn is None and light not in [Light.GREEN, Light.GREEN_ARROW])
            at_intersection = (car.direction == "north" and car.y == INTERSECTION_END_Y + 1) or \
                              (car.direction == "south" and car.y == INTERSECTION_START_Y - 1) or \
                              (car.direction == "east" and car.x == INTERSECTION_START_X - 1) or \
                              (car.direction == "west" and car.x == INTERSECTION_END_X + 1)
            next_x, next_y, buffer_x, buffer_y = car.x, car.y, car.x, car.y
            if car.direction == "north": next_y -= 1; buffer_y -= 2
            elif car.direction == "south": next_y += 1; buffer_y += 2
            elif car.direction == "east": next_x += 1; buffer_x += 2
            elif car.direction == "west": next_x -= 1; buffer_x -= 2
            is_car_ahead = self.get_car_at(next_x, next_y) or self.get_car_at(buffer_x, buffer_y)
            if is_car_ahead or (at_intersection and should_stop_for_light):
                intended_moves[car.id] = (car.x, car.y)
            else:
                intended_moves[car.id] = (next_x, next_y)

        final_positions = {}; occupied_next_spots = set()
        for car in self.cars:
            intended_pos = intended_moves[car.id]
            if intended_pos == (car.x, car.y):
                final_positions[car.id] = (car.x, car.y); car.stopped = True; car.color = Color.RED
                continue
            if intended_pos in occupied_next_spots:
                self.crashes += 1
                final_positions[car.id] = (car.x, car.y); car.stopped = True; car.color = Color.RED
            else:
                final_positions[car.id] = intended_pos; occupied_next_spots.add(intended_pos)

        for car in self.cars:
            car.x, car.y = final_positions[car.id]
            if (car.x, car.y) != intended_moves[car.id]:
                 car.stopped = True; car.color = Color.RED
            if car.turn == "left":
                turned = False
                if car.direction == "north" and car.y == LANE_E_Y: car.direction = "west"; turned = True
                elif car.direction == "south" and car.y == LANE_W_Y: car.direction = "east"; turned = True
                elif car.direction == "east" and car.x == LANE_N_X: car.direction = "north"; turned = True
                elif car.direction == "west" and car.x == LANE_S_X: car.direction = "south"; turned = True
                if turned: car.turn = None

        cars_on_grid = [c for c in self.cars if 0 <= c.x < GRID_WIDTH and 0 <= c.y < GRID_HEIGHT]
        self.passed_cars += len(self.cars) - len(cars_on_grid)
        self.cars = cars_on_grid
        
        if len(self.cars) < self.concurrent_cars:
            if random.random() < 0.5: self.spawn_car()

    def cycle(self): self.pattern.cycle()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traffic Simulation")
    parser.add_argument('--pattern', '-p', type=str, default='simple', choices=['simple', 'protected-left'], help='Traffic pattern to simulate.')
    parser.add_argument('--cars', '-c', type=int, default=20, help='Total number of cars to simulate.')
    parser.add_argument('--turn-ratio', '-t', type=float, default=0.2, help='Ratio of cars that will turn left (0.0 to 1.0). Only for protected-left pattern.')
    parser.add_argument('--distribution', '-d', type=float, default=1.0, help='Distribution of cars across directions (0.0=random, 1.0=even).')
    parser.add_argument('--ignore-crashes', action='store_true', help='Continue simulation even after a crash.')
    args = parser.parse_args()

    if not 0.0 <= args.turn_ratio <= 1.0: raise ValueError("Turn ratio must be between 0.0 and 1.0.")
    if not 0.0 <= args.distribution <= 1.0: raise ValueError("Distribution must be between 0.0 and 1.0.")

    pattern_class = {'simple': SimpleIntersection, 'protected-left': ProtectedLeftTurn}[args.pattern]
    concurrent_cars = 15
    if args.cars < 15: concurrent_cars = args.cars

    intersection = Intersection(concurrent_cars, args.cars, pattern_class, 
                                left_turn_percentage=args.turn_ratio, 
                                distribution_factor=args.distribution,
                                ignore_crashes=args.ignore_crashes)

    try:
        while not intersection.is_finished():
            intersection.cycle()
        
        cleanup_steps = 0
        while len(intersection.cars) > 0:
            if cleanup_steps > 50: break
            intersection.update_cars()
            if not intersection.is_test_mode:
                intersection.print_state()
                time.sleep(0.5)
            cleanup_steps += 1

        if intersection.crashes > 0 and not intersection.ignore_crashes:
            print(f"\nSimulation Halted: A crash occurred after {intersection.steps} steps.")
        elif intersection.steps >= MAX_STEPS:
            print(f"\nSimulation finished: Reached step limit of {MAX_STEPS}.")
        else:
            print(f"\nSimulation finished.")
        print(f"Cars Started: {intersection.cars_created}/{intersection.goal_cars}")
        print(f"Cars Finished: {intersection.passed_cars}/{intersection.goal_cars}")
        if intersection.crashes > 0:
            print(f"Crashes: {intersection.crashes}")
            
    except KeyboardInterrupt:
        print("\nSimulation stopped.")