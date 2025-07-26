import unittest
import sys
import os
import io

# Add the parent directory to the path so we can import the traffic module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from traffic import (Car, Intersection, SimpleIntersection, ProtectedLeftTurn, Light, 
                     LANE_N_X, LANE_S_X, LANE_E_Y, LANE_W_Y,
                     INTERSECTION_START_Y, INTERSECTION_END_Y,
                     INTERSECTION_START_X, INTERSECTION_END_X)

class TestCar(unittest.TestCase):
    def test_car_creation(self):
        car = Car(1, "north")
        self.assertEqual(car.id, 1)
        self.assertEqual(car.direction, "north")
        self.assertIsNone(car.turn)

    def test_car_movement(self):
        car = Car(1, "north")
        initial_y = car.y
        car.move()
        self.assertEqual(car.y, initial_y - 1)

class TestIntersection(unittest.TestCase):
    def test_intersection_creation(self):
        intersection = Intersection(10, 20, SimpleIntersection, is_test_mode=True)
        self.assertEqual(intersection.concurrent_cars, 10)
        self.assertEqual(intersection.goal_cars, 20)
        self.assertIsInstance(intersection.pattern, SimpleIntersection)

    def test_spawn_car(self):
        intersection = Intersection(1, 1, SimpleIntersection, is_test_mode=True)
        intersection.cars = [] # Start with no cars for a clean test
        intersection.spawn_car()
        self.assertEqual(len(intersection.cars), 1)
        intersection.spawn_car() # Should not spawn more than concurrent_cars
        self.assertEqual(len(intersection.cars), 1)


class TestTrafficPatterns(unittest.TestCase):
    def test_simple_intersection_cycle(self):
        intersection = Intersection(1, 100, SimpleIntersection, is_test_mode=True)
        intersection.cars = [Car(0, "north")]
        initial_lights = intersection.pattern.lights.copy()
        intersection.pattern.cycle()
        self.assertNotEqual(initial_lights, intersection.pattern.lights)

    

class TestPositioning(unittest.TestCase):
    def test_car_initial_positions(self):
        self.assertEqual(Car(0, "north").x, LANE_N_X)
        self.assertEqual(Car(1, "south").x, LANE_S_X)
        self.assertEqual(Car(2, "east").y, LANE_W_Y)
        self.assertEqual(Car(3, "west").y, LANE_E_Y)

    def test_light_positions(self):
        intersection = Intersection(0, 1, ProtectedLeftTurn, is_test_mode=True)
        intersection.update_grid()
        grid = intersection.grid
        self.assertEqual(grid[INTERSECTION_START_Y - 2][LANE_S_X], "║")
        self.assertEqual(grid[INTERSECTION_END_Y + 2][LANE_N_X], "║")
        self.assertIn(grid[LANE_W_Y][INTERSECTION_START_X - 2], ["═", " "])
        self.assertIn(grid[LANE_E_Y][INTERSECTION_END_X + 2], ["═", " "])
        self.assertNotEqual(grid[INTERSECTION_START_Y - 1][LANE_S_X - 2], " ")
        self.assertNotEqual(grid[INTERSECTION_END_Y + 1][LANE_N_X + 2], " ")
        self.assertNotEqual(grid[LANE_W_Y + 2][INTERSECTION_START_X - 2], " ")
        self.assertNotEqual(grid[LANE_E_Y - 2][INTERSECTION_END_X + 2], " ")

if __name__ == '__main__':
    unittest.main()