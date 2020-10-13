"""

Usman Siddiqui
19 Nov 2018

Thermodynamics Snooker

"""

import numpy as np
from numpy import linalg as la
import pylab as pl

from Ball import Ball
import Config
from ParseState import ParseState
from WriteOutput import WriteOutput

class App(object):
    """Simulation agent for hard balls simulation.

    Responsible for:
    - Declaring initial state of simulation
    - Updating position and velocity of balls for each frame
    - Rendering each frame
    - Calculating state measurements at each frame

    Attributes:
        __container_radius (float): Radius of container.
        num_frames (int): The number of collisions to be rendered.
        should_output (bool): Should data be output to CSV file?
        should_animate (bool): Should the simulation produce an animation?
        animation_frame_pause (float): The pause time in seconds between frames.
        initial_state_file_name (str): Name of CSV file containing initial state.
        
        time (float): The time of the simulation.
        num_balls (int): The number of balls in the container.
        kinetic_energy (float): Sum of kinetic energy of all particles.
        rms_speed (float): The root mean square speed of all particles.
        pressure (float): The pressure exerted on the container.
        delta_p (float): The total change in momentum of balls in container.
        ball_collisions (int): The total number of ball-ball collisions.
        wall_collisions (int): The total number of ball-wall collisions.
        
        __balls (list): An array of each ball in the simulation.
        b2b_table (list): A 2-D array of collision times for each pair of balls.
        b2w_table (list): A 1-D array of collision times for wall collisions.
        
        container_circumference (float): The circumference of the container.
        container_patch (object): A pylab patch object for rendering container.
        
        output (WriteOutput): WriteOutput class that measures observables of
                              system and outputs to CSV file for data analysis.
    """
    def __init__(self, container_radius, num_frames, should_output,
                 should_animate, animation_frame_pause, initial_state_file_name):
        """Initialises the application."""
        self.__container_radius = container_radius
        self.num_frames = num_frames
        self.should_output = should_output
        self.should_animate = should_animate
        self.animation_frame_pause = animation_frame_pause
        self.initial_state_file_name = initial_state_file_name
        
        # Initialise simulation variables
        self.time = 0.0
        self.num_balls = 0
        self.kinetic_energy = 0.0
        self.rms_speed = 0.0
        self.pressure = 0.0
        self.delta_p = 0.0
        self.ball_collisions = 0
        self.wall_collisions = 0

        # Initialise balls list
        self.__balls = ParseState(self).get_balls()
        self.num_balls = len(self.balls())

        # Initialise collision time tables
        self.b2b_table = np.full((self.num_balls, self.num_balls), np.inf)
        self.b2w_table = np.full(self.num_balls, np.inf)
        self.init_table()

        # Initialise container parameters
        self.container_circumference = 2 * np.pi * self.__container_radius
        self.container_patch = pl.Circle([0, 0], self.__container_radius,
                                         ec = "b", fill = False, ls = "solid")

        # Initialise data output mechanism
        self.output = WriteOutput(self)
        self.output.print_state() # Print initial state of system
        self.update_state(0.0) # Calculates state measurements at t = 0
        
        # Run simulation
        self.render(num_frames = num_frames, animate = should_animate)

        self.output.print_state() # Print final state of system
        self.output.save() # Save CSV data file

    def balls(self):
        """Accessor method for balls in simulation."""
        return self.__balls

    def container_radius(self):
        """Accessor method for container radius."""
        return self.__container_radius

    def init_table(self):
        """Populate the collision table for B2B and B2W collisions."""
        balls = self.balls()
        l = self.num_balls

        for i in range(l):
            collision_time = balls[i].next_wall_collision(self.container_radius())
            self.b2w_table[i] = collision_time

            for j in range(i + 1, l):
                collision_time = balls[i].next_ball_collision(balls[j])
                self.b2b_table[i][j] = collision_time

    def update_table(self, dt):
        """Update the collision times table after elapsed time dt."""
        l = len(self.b2b_table)
        
        self.b2w_table -= dt
        
        # Only operate operate on half of the array so improves efficiency from
        # N^2 updated values to N(N+1)/2 updates.
        for i in range(0, l):
            for j in range (i + 1, l):
                # Subtracting from np.inf values leaves their value unchanged
                self.b2b_table[i][j] -= dt

    def recalculate_collision(self, ball_ids):
        """Recalculate the B2W and B2B collisions for colliding balls."""
        balls = self.balls()
        l = self.num_balls
        
        # Only collision times for the balls in ball_ids is recalculated.
        for i in ball_ids:
            # Recalculate B2W collision for colliding balls
            b2w_time = balls[i].next_wall_collision(self.container_radius())
            self.b2w_table[i] = b2w_time

            for j in range(0, l):
                # Recalculate B2B collision for pairs of balls
                if (i != j):
                    x = np.amin([i, j]) # Find row
                    y = np.amax([i, j]) # Find column
                    b2b_time = balls[i].next_ball_collision(balls[j])

                    # Ensures only upper-right side of table is updated
                    self.b2b_table[x][y] = b2b_time

    def next_collision(self):
        """Determines if next collision is ball-ball or ball-wall collision.

        Returns:
            A collision object. The first element is a list containing the IDs
            of all colliding balls (1 ID for B2W collision, 2 IDs for B2B
            collision). The second element is the time of collision.
            
            [[id1], t1] or [[id1, id2], t2]
        """
        
        # Get index of next ball to collide with wall
        b2w = np.argmin(self.b2w_table)
        b2w_time = self.b2w_table[b2w]

        # Get indices of next balls to collide with each other
        b2b = np.unravel_index(np.argmin(self.b2b_table), self.b2b_table.shape)
        b2b_time = self.b2b_table[b2b]

        if b2w_time < b2b_time:
            # Wall collision
            return [[b2w], b2w_time]
        else:
            # Ball collision
            return [[b2b[0], b2b[1]], b2b_time]

    def collide(self, collision):
        """Executes the collision and updates ball position and velocity.

        Arguments:
            collision (list): The return value from next_collision() method
                              which is a collision object for the current
                              time-step.
        """

        dt = collision[1] # Stores time of next collision
        self.update_table(dt) # Update collision table
        balls = self.balls()

        for b in self.balls():
            # Updates position of each ball to position at collision time
            b.update_position(dt)
        
        if len(collision[0]) == 1:
            # Wall collision
            b2w = collision[0][0] # Store index of colliding ball
            ball = balls[b2w] # Store reference to colliding ball
            u = ball.velocity()
            v = ball.velocity_after_wall_collision()
            ball.update_velocity(v)
                
            # Impulse calculation for determining pressure
            delta_p = ball.mass() * (v - u)
            self.delta_p += la.norm(delta_p)

            # Recalculate collision table for colliding ball
            self.recalculate_collision([b2w])

            # Increment collision counters
            ball.wall_collisions += 1
            self.wall_collisions += 1
        else:
            # Ball collision
            b_i, b_j = collision[0] # Store indices of colliding balls

            # Store references to colliding balls
            b1 = balls[b_i]
            b2 = balls[b_j]

            v1, v2 = b1.velocity_after_ball_collision(b2)
            b1.update_velocity(v1)
            b2.update_velocity(v2)

            # Recalculate collision table for colliding balls
            self.recalculate_collision([b_i, b_j])

            # Increment collision counters
            b1.ball_collisions += 1
            b2.ball_collisions += 1
            self.ball_collisions += 1

        # Calculate new state variables (i.e KE, RMS Speed)
        self.update_state(dt)

    def render(self, num_frames, animate = False):
        """Renders each frame of the simulation at collision time.

        Arguments:
            num_frames (int): The number of collision frames to render.
            animate (bool): Flag to indicate if output should be animated.
        """

        # For rendering purposes
        if animate:
            bounds = self.container_radius() + 5 # Defines bounds of axis
            pl.figure()
            ax = pl.axes(xlim = (-bounds, bounds), ylim = (-bounds, bounds))
            ax.set_aspect("equal") # Sets equal aspect ratio
            ax.add_artist(self.container_patch)
            time_txt = ax.text(0.05, 0.01, self.format_debug_text(),
                               fontsize = 7, transform = ax.transAxes)
            for b in self.balls():
                b.render(ax)
            pl.pause(self.animation_frame_pause)

        for frame in range(num_frames):
            next_collision = self.next_collision() # Determines next collision
            self.collide(next_collision) # Executes collision
            if animate:
                for b in self.balls():
                    b.render(ax)
                time_txt.set_text(self.format_debug_text()) # Debug string
                pl.pause(self.animation_frame_pause)

        if animate:
            pl.show()

    def format_debug_text(self):
        """Formats debug string for rendering on animation.
        
        Returns:
            A formatted string containing the state variables for each
            time-step.
        """
        total_collisions = self.wall_collisions + self.ball_collisions
        txt_str = ("Time: {:.2f}s\nBalls: {:d}\nBall Collisions: {:d}"
                   "\nWall Collisions: {:d}\nTotal Collisions: {:d}"
                   "\nKE: {:.2f}J\nRMS Speed: {:.2f}m/s\nPressure: {:.2f}Pa")
        return txt_str.format(self.time, self.num_balls, self.ball_collisions,
                              self.wall_collisions, total_collisions,
                              self.kinetic_energy, self.rms_speed, self.pressure)

    def update_state(self, dt):
        """Updates the state variables of the simulation after a time dt.

        Arguments:
            dt (float): The time which has elapsed since the last update.
        """
        kinetic_energy = 0.0
        rms_speed_sum = 0.0
        for b in self.balls():
            kinetic_energy += b.kinetic_energy()
            rms_speed_sum += b.speed_squared()

        # Update state variables
        self.time += dt
        self.kinetic_energy = kinetic_energy
        self.rms_speed = np.sqrt(rms_speed_sum / self.num_balls)
        self.pressure = (self.delta_p / (self.container_circumference * self.time)
                        if self.time > 0.0 else 0.0)
        Ball.rms_speed = self.rms_speed # Used for scaling of velocity vectors
        self.output.print_line()

# Initialises simulation agent
app = App(Config.CONTAINER_RADIUS, Config.NUM_FRAMES_TO_RENDER,
          Config.SHOULD_OUTPUT, Config.SHOULD_ANIMATE,
          Config.ANIMATION_FRAME_PAUSE, Config.INITIAL_STATE_FILE_NAME)
