import csv
import numpy as np
from numpy import linalg as la
from numpy import random

import Config

class InitialState():
    """Generates initial conditions and saves to file.

    This is a standalone module which does not interact with the App.py or
    Ball.py modules. Its job is to procedurally create an initial state and
    store it in a file so that the same state can be simulated multiple times.

    To run this module, specify the required variables in Config.py then execute this
    file. This will generate a CSV file with the name specified in Config.py.

    The position and velocity of the ball is randomly generated using a uniform
    distribution. To change this distribution, change the `np.uniform` to its
    your required distribution as specified in the `generate_position` and
    `generate_velocity` methods. See `https://docs.scipy.org/doc/numpy-1.15.1/reference/routines.random.html`
    for more details of possible distributions.

    Responsible for:
    - Procedurally generating an initial state
    - Calculating ball position so that no balls are overlapping
    - Outputting initial conditions to a CSV file

    Arguments:
        container_radius (float): The radius of the container.
        default_radius (float): Default radius of the ball.
        default_mass (float): Default mass of each ball.
        initial_state_file_name (str): The name of the output file for initial conditions.
        num_balls (int): The number of balls to generate for simulation.

    Attributes:
        balls (list): A list containing each ball that has been generated.
        container_radius (float): The radius of the container.
        file_name (str): The name of the output file for initial conditions.
        num_balls (int): The number of balls to generate for simulation.
        default_mass (float): The default mass of the balls.
        default_radius (float): The default radius of the balls.
        rms_speed (float): Root mean square speed of the balls.
    """
    def __init__(self, container_radius, initial_state_file_name, num_balls, default_mass, default_radius, rms_speed):
        """Initialises the InitialState class with the required variables."""
        self.container_radius = container_radius
        self.file_name = initial_state_file_name
        self.num_balls = num_balls
        self.default_mass = default_mass
        self.default_radius = default_radius
        self.rms_speed = rms_speed
        
        self.balls = []
        
        for i in range(self.num_balls):
            b = self.generate_ball()
            # Append as a flat array for storage in CSV file
            self.balls.append([i for i in b])
        
        self.write_to_csv()
        print("Initial state created successfully. Run App.py module.")
    
    def generate_ball(self):
        """Generates a single ball."""
        mass = self.default_mass
        ball_radius = self.default_radius
        position = self.generate_position(self.container_radius, ball_radius)
        velocity = self.generate_velocity()
        
        return [position[0], position[1], velocity[0], velocity[1], mass, ball_radius]
    
    def generate_position(self, container_radius, ball_radius):
        """Generates the position of a ball."""
        timeout = 0
        bounds = container_radius - ball_radius
        position = None

        # We make a maximum of 500 attempts per ball to recalculate the position
        # if the ball is overlapping or outside the container. After this, the
        # while loop is broken to prevent an infinite loop. By the end of the
        # loop, either timeout > 500 or we have generated a valid position.
        while True:
            timeout += 1
            position = random.uniform(-bounds, bounds, 2)
            if timeout > 500 or ((self.is_colliding(position, ball_radius) == False
              and self.is_outside_container(position, ball_radius) == False)):
                  break
        
        if timeout > 500:
            # If the procedure has timed-out raise an exception
            raise Exception(("There are too many balls in the simulation."
                            "Consider increasing the size of the container"
                            "or reducing the number of balls in Config module."))
        else:
            # Otherwise return the generated position
            return position
    
    def generate_velocity(self):
        """Generates the velocity of a ball."""
        
        # The method below creates balls with a fixed magnitude of velocity
        # (fixed RMS_SPEED specified in Config.py). For a Rayleigh distribution,
        # use random.normal() for both velocity_x and velocity_y. Then the
        # resultant velocity will have a Rayleigh distribution.
        speed = self.rms_speed
        multiplier_y = random.choice([-1.0, 1.0])
        velocity_x = random.uniform(-speed, speed)
        velocity_y = multiplier_y * np.sqrt(self.rms_speed ** 2 - velocity_x ** 2)
        v = [velocity_x, velocity_y]
        return v
    
    def is_colliding(self, position, ball_radius):
        """Checks if `position` of a ball is colliding with another ball.
        
        Arguments:
            position (np.array): [x, y] containing the position of the ball.
            ball_radius (float): The radius of the ball.

        Returns:
            is_colliding (bool): Flag to indicate if `position` is colliding
                                 with another ball.
        """
        is_colliding = False
        
        for b in self.balls:
            b_position = [b[0], b[1]]
            dr = b_position - position
            dr_magnitude = la.norm(dr)
            if dr_magnitude <= b[5] + ball_radius:
                is_colliding = True
                break # Break from loop early if collision detected
        
        return is_colliding
    
    def is_outside_container(self, position, ball_radius):
        """Checks if `position` of a ball is outside of container.
        
        Arguments:
            position (np.array): [x, y] containing the position of the ball.
            ball_radius (float): The radius of the ball.

        Returns:
            is_outside_container (bool): Flag to indicate if `position` is
                                         outside of the container.
        """
        
        # IMPORTANT: This method will check if a ball is outside of the
        # container. To generate balls within an inner circle of
        # radius r (float) (i.e. for diffusion experiments), replace the
        # last line with:
        # return position_magnitude + ball_radius >= r
        
        # Example: To restrict balls to an inner container of radius 200, use:
        # return position_magnitude + ball_radius >= 200
        position_magnitude = la.norm(position)
        return position_magnitude + ball_radius >= self.container_radius
    
    def write_to_csv(self):
        """Writes contents of `self.balls` to a CSV file."""
        try:
            f = open(self.file_name, "wt")
        except IOError:
            raise Exception("File cannot be created: ensure file name is of"
                            "format `ExampleFile.csv` in Config module.")
        with f as csv_file:
            writer = csv.writer(csv_file, lineterminator = "\n")
            writer.writerows(self.format_ball_output())
    
    def format_ball_output(self):
        """Outputs each row in `self.balls` for writing to file.
        
        Yields:
            ball [list]: A list containing variables defining the position,
                         velocity, mass and radius of a ball.
        """

        # A yield call is more efficient than writing to the file directly
        # because it writes one row at a time (so less memory-intensive).
        for ball in self.balls:
            yield ball

# Initialise the state generator with parameters from Config.py
InitialState(Config.CONTAINER_RADIUS, Config.INITIAL_STATE_FILE_NAME,
             Config.NUMBER_OF_BALLS, Config.DEFAULT_MASS,
             Config.DEFAULT_BALL_RADIUS, Config.RMS_SPEED)
