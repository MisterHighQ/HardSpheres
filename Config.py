import numpy as np

""" Config file for simulation.

All of the variables in this file MUST be defined for the simulation to run.

Attributes:
    CONTAINER_RADIUS (float = 10): The radius of the container.
    
    ANIMATION_FRAME_PAUSE (float = 0.01): The time in seconds that simulation
                                          pauses before rendering next
                                          collision frame.
    NUM_FRAMES_TO_RENDER (int = 1000): Defines how many frames
                                       (i.e. collisions) the simulation should
                                       render.
    
    DEFAULT_BALL_RADIUS (float = 1.0): The default radius of
                                       procedurally-generated balls.
    DEFAULT_MASS (float = 1.0): The default mass of procedurally-generated
                                balls.
    INITIAL_STATE_FILE_NAME (str = 'InitialState.csv'): The name of the initial
                                                        conditions file.
    NUMBER_OF_BALLS (int = 8): The number of procedurally-generated balls to
                               create in InitialState.py.
    RMS_SPEED (float = 1.0): Root mean square speed of the balls in container.

    SHOULD_OUTPUT (bool = True): Flag to indicate if simulation data should be
                                 written to a file.
    SHOULD_ANIMATE (bool = True): Flag to indicate if the animation should be
                                  shown.
"""

# Required
CONTAINER_RADIUS = 10 # Meters

# Required for App.py to run
ANIMATION_FRAME_PAUSE = 0.001 # Pause time in seconds
NUM_FRAMES_TO_RENDER = 1000

# Required for InitialState.py to run
DEFAULT_BALL_RADIUS = 1.0 # Meters
DEFAULT_MASS = 1.0 # Kilograms
INITIAL_STATE_FILE_NAME = "InitialState.csv" # DO NOT CHANGE
NUMBER_OF_BALLS = 15
RMS_SPEED = 5.0 # Meters / Second

SHOULD_OUTPUT = False
SHOULD_ANIMATE = True


"""Error validation

It's important that the values defined above are carefully validated as they
are required for the simulation to run.
"""

if not np.isfinite(CONTAINER_RADIUS) or CONTAINER_RADIUS <= 0:
    raise Exception("Invalid CONTAINER_RADIUS parameter in Config module.")

if not np.isfinite(ANIMATION_FRAME_PAUSE) or ANIMATION_FRAME_PAUSE <= 0:
    raise Exception("Invalid ANIMATION_FRAME_PAUSE parameter in Config module.")

if (not np.isfinite(NUM_FRAMES_TO_RENDER) or NUM_FRAMES_TO_RENDER <= 0 or
    np.mod(NUM_FRAMES_TO_RENDER, 1)) != 0:
    raise Exception("Invalid NUM_FRAMES_TO_RENDER parameter in Config module.")

if (not np.isfinite(DEFAULT_BALL_RADIUS) or DEFAULT_BALL_RADIUS <= 0 or
    DEFAULT_BALL_RADIUS >= CONTAINER_RADIUS):
    print("Invalid DEFAULT_BALL_RADIUS parameter in Config module.")

if not np.isfinite(DEFAULT_MASS) or DEFAULT_MASS <= 0:
    raise Exception("Invalid DEFAULT_MASS parameter in Config module.")

if (not np.isfinite(NUMBER_OF_BALLS) or NUMBER_OF_BALLS <= 0
   or np.mod(NUMBER_OF_BALLS, 1)) != 0:
    raise Exception("Invalid NUMBER_OF_BALLS parameter in Config module.")

if not np.isfinite(RMS_SPEED) or RMS_SPEED <= 0:
    raise Exception("Invalid RMS_SPEED parameter in Config module.")