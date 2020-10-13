import pylab as pl
import numpy as np
from numpy import linalg as la

class Ball():
    """Ball object representing each colliding entity in simulation.

    Responsible for:
    - Tracking own position, velocity, mass and radius
    - Calculates expected collisions times with wall and other balls
    - Contains methods for calculating velocities after collision
    - Stores patches for ball and velocity arrow (graphics rendering)

    Arguments:
        position (np.array): The position of the center of mass of the ball
                             relative to the centre of the container.
        velocity (np.array): The velocity of the ball.
        mass (float = 1.0): The mass of the ball.
        radius (float = 1.0): The radius of the ball.

    Attributes:
        __position (np.array): The position of the ball.
        __velocity (np.array): The velocity of the ball.
        __mass (float): The mass of the ball.
        __radius (float): The radius of the ball.
        __ball_patch (patches.Cirlce): Circle patch to render ball position.
        __arrow_patch (patches.Arrow): Arrow patch to render ball velocity.
        distance_travelled (float): Tracks total distance travelled by ball.
        ball_collisions (int): Counts number of collisions with other balls.
        wall_collisions (int): Counts number of collisions with wall.
    """
    rms_speed = 1.0 # Used for scaling of velocity vector graphic
    
    def __init__(self, position, velocity, mass = 1.0, radius = 1.0):
        """Initialises ball object with position, velocity, mass and radius."""
        if len(position) != 2 or len(velocity) != 2:
            raise Exception("Unexpected position or velocity format in Ball"
                            "module.")
        
        self.__position = np.array(position) # Private attribute
        self.__velocity = np.array(velocity) # Private attribute
        self.__mass = mass # Private attribute
        self.__radius = radius # Private attribute
        self.__ball_patch = None
        self.__arrow_patch = None

        # Statistical variables, not relevant to functioning of simulation
        self.distance_travelled = 0.0
        self.ball_collisions = 0
        self.wall_collisions = 0

    def position(self):
        """Accessor method for ball position.
        
        Returns:
            An np.array of the center of mass of the ball relative to the
            center of the container.
        """
        return self.__position

    def velocity(self):
        """Accessor method for ball velocity.
        
        Returns:
            An np.array of the velocity of the ball.
        """
        return self.__velocity

    def mass(self):
        """Accessor method for ball mass.
        
        Returns:
            A  float specifying the mass of the ball.
        """
        return self.__mass

    def radius(self):
        """Accessor method for ball radius.
        
        Returns:
            A  float specifying the radius of the ball.
        """
        return self.__radius

    def kinetic_energy(self):
        """Calculates the kinetic energy of the ball.
        
        Returns:
            A float specifying the kinetic energy of the ball.
        """
        v = self.velocity()
        return 0.5 * self.mass() * np.dot(v, v)

    def speed_squared(self):
        """Calculates the squared speed of the ball (for RMS calculations).
        
        Returns:
            A float specifying the magnitude squared of the speed of the ball.
        """
        v = self.velocity()
        return np.dot(v, v)

    def mean_free_path(self):
        """Calculates the mean free path of the ball.
        
        Returns:
            A float specifying the distance travelled divided by the number of
            ball-ball collisions.
        """
        if self.ball_collisions > 0:
            return self.distance_travelled / self.ball_collisions
        else:
            return 0.0

    def momentum(self):
        """Calculates the momentum of the ball.
        
        Returns:
            An np.array of the momentum of the ball.
        """
        return self.velocity() * self.mass()

    def update_position(self, dt):
        """Updates position of the ball after elapsed time dt.
        
        Arguments:
            dt (float): Elapsed time since last update.
        """
        dp = self.velocity() * dt # Displacement of ball after time dt
        self.__position += dp

        # Increment the distance travelled by the magnitude of dp
        self.distance_travelled += la.norm(dp)

    def update_velocity(self, v):
        """Updates velocity of the ball.

        Arguments:
            v (np.array): New velocity of the ball.
        """
        self.__velocity = v

    def next_wall_collision(self, container_radius):
        """Calculates the time at which the ball will next collide with a wall.

        Arguments:
            container_radius (float): The radius of the container.

        Returns:
            The time (float) of the next wall collision.
        """
        x = self.position()
        v = self.velocity()

        a = np.dot(v, v)
        b = 2 * np.dot(x, v)
        c = np.dot(x, x) - (container_radius - self.radius()) ** 2

        t = Ball.predict_collision_time(a, b, c)
        return t

    def next_ball_collision(self, ball):
        """Calculates the time at which the ball will next collide with `ball`.

        Arguments:
            ball (Ball): The other colliding ball with which to determine
                         collision time.

        Returns:
            The time (float) of the next collision with ball (Ball).
        """
        r1 = self.radius()
        r2 = ball.radius()

        x1 = self.position()
        x2 = ball.position()

        v1 = self.velocity()
        v2 = ball.velocity()

        dx = x1 - x2
        dv = v1 - v2

        a = np.dot(dv, dv)
        b = 2 * np.dot(dx, dv)
        c = np.dot(dx, dx) - (r1 + r2) ** 2

        t = Ball.predict_collision_time(a, b, c)
        return t

    @classmethod
    def predict_collision_time(cls, a, b, c):
        """Calculates time when the ball will collide by solving quadratic.

        Responsible for:
        - Solving quadratic of the form at^2 + bt + c = 0
        - Returns the smallest positive time of collision if one exists
        - If no collision (no roots) returns np.inf as time of collision

        Arguments:
            a (float): The coefficient of t^2 in quadratic.
            b (float): The coefficient of t in quadratic.
            c (float): The constant term in quadratic.

        Returns:
            The smallest, positive time of next collision (float) or np.inf
            if no collision is expected (i.e. quadatic has no solutions).
        """

        # Variable `roots` holds all possible roots of polynomial equation of
        # the form at^2 + bt + c = 0, including complex and negative roots. We
        # extract the real and positive roots in `time_roots`. We neglect
        # values of t < 1e-12 as these are likely equivalent to t = 0 with
        # floating point arithmetic errors.
        roots = np.roots([a, b, c])
        time_roots = [t for t in roots if np.isreal(t) and t > 1e-12]

        # Sets `collision_time` to np.inf if no collision occurs or to the
        # smallest, positive root in `time_roots` if there is a collision time.
        time = np.inf if len(time_roots) == 0 else np.amin(time_roots)
        return time

    def velocity_after_wall_collision(self):
        """Calculates rebound velocity of ball after a wall collision.

        Returns:
            An np.array of the rebound velocity of the ball after collision
            with the container.
        """
        r = self.position()
        u = self.velocity()

        R = r * (2 * np.dot(u, r) / np.dot(r, r))
        v = u - R
        return v

    def velocity_after_ball_collision(self, b):
        """Calculates rebound velocities of balls after a collision with `b`.

        Arguments:
            b (Ball): The other colliding ball.

        Returns:
            A list containing two np.array elements of the rebound velocities
            of `self` and other ball `b`.

            [v1 (np.array), v2 (np.array)]
        """
        m1 = self.mass()
        m2 = b.mass()

        x1 = self.position()
        x2 = b.position()

        u1 = self.velocity()
        u2 = b.velocity()

        dx = x1 - x2
        dv = u1 - u2

        s = (2 * np.dot(dx, dv)) / ((m1 + m2) * np.dot(dx, dx))

        v1 = u1 - (dx * m2 * s)
        v2 = u2 + (dx * m1 * s)

        return [v1, v2]
    
    def render(self, ax):
        """Draws the ball and its velocity vector to screen.

        Arguments:
            ax (axes.Axes): Axes object to draw the ball on.
        """
        self.draw_ball(ax)
        self.draw_arrow(ax)
    
    def draw_ball(self, ax):
        """Draws the ball outline to screen.

        Arguments:
            ax (axes.Axes): Axes object to draw the ball on.
        """
        r = self.position()
        
        # If the ball is already drawn on screen, just update its position
        if self.__ball_patch:
            self.__ball_patch.center = r
        else:
            # Otherwise draw a new ball onto the screen
            ball_patch = pl.Circle(r, self.radius(), ec = "r", fill = False)
            self.__ball_patch = ax.add_patch(ball_patch)
    
    def draw_arrow(self, ax):
        """Draws the velocity vector to screen.

        Arguments:
            ax (axes.Axes): Axes object to draw the velocity vector on.
        """
        
        # If a velocity vector already exists on screen, remove it
        if self.__arrow_patch:
            self.__arrow_patch.remove()
        
        # Draw the velocity vector
        r = self.position()
        u = self.velocity() / Ball.rms_speed
        arrow_patch = pl.Arrow(r[0], r[1], u[0], u[1], width = 0.2, ec = "b")
        self.__arrow_patch = ax.add_patch(arrow_patch)
            
            
