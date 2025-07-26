> This project was written entirely by the Gemini CLI.
>
>       *     *
>        \   /
>         \ /
>          *
>         / \
>        /   \
>       *-----*
>
> In lines of code, a story's told,
> Of traffic flowing, brave and bold.
> A digital hand, a thoughtful guide,
> Crafted this world, with Gemini inside.

# traffic

A command-line traffic simulation program that visualizes cars moving through a single intersection with traffic lights.

## Description

This program uses the terminal to display a grid representing a road intersection. Cars, represented by colored squares, are generated and move towards and through the intersection from all four directions (North, South, East, West).

The traffic lights cycle through standard green, yellow, and red phases to control the flow of traffic. The simulation continues until a predefined number of cars have successfully passed through the intersection.

## Features

*   **Two Traffic Patterns:**
    *   `simple`: A standard 4-way intersection with no protected turns.
    *   `protected-left`: An intersection with dedicated green arrow signals for protected left turns.
*   **Configurable Simulation:** Control the number of cars, the ratio of left-turning vehicles, and the distribution of cars across all four directions.
*   **Visual Appeal:** Uses ANSI escape codes for colored lights and cars, with unlit signal lights displayed in grey.

## How to Run

To run the simulation, simply execute the Python script from your terminal. You can use the following flags to customize the simulation:

```bash
python3 traffic.py [FLAGS]
```

**Flags:**

*   `--pattern` or `-p`: Choose the traffic pattern.
    *   `simple` (default)
    *   `protected-left`
*   `--cars` or `-c`: Set the total number of cars to simulate (default: 20).
*   `--turn-ratio` or `-t`: Set the ratio of cars that will turn left (from 0.0 to 1.0). Only applies to the `protected-left` pattern (default: 0.2).
*   `--distribution` or `-d`: Set the car distribution factor (from 0.0 to 1.0). 1.0 is perfectly even, 0.0 is all cars from one random direction (default: 1.0).

**Examples:**

*   Run a simulation with 50 cars and a protected-left turn pattern:
    ```bash
    python3 traffic.py -p protected-left -c 50
    ```
*   Run a simulation where 50% of cars turn left and the traffic is highly concentrated in one direction:
    ```bash
    python3 traffic.py -p protected-left -t 0.5 -d 0.1
    ```
