import csv

from Ball import Ball

class ParseState():
    """Reads initial conditions from file and parses as an array of balls

    Responsible for:
    - Reading an initial state from file
    - Parsing variables for each ball to produce Ball object
    - Returning list of Ball objects

    Arguments:
        App (App): Takes the App object to read initial state file name

    Attributes:
        __balls (list): A list containing each ball that has been read from
                        file.
        file_name (str): The name of the initial conditions file to read from.
    """
    def __init__(self, App):
        """Class reads and parses initial conditions from CSV file."""
        self.file_name = App.initial_state_file_name
        self.__balls = [] # Private attribute
        
        for ball in self.read_file(self.file_name):
            # Extract each of the parameters in the CSV file
            position = [float(ball[0]), float(ball[1])]
            velocity = [float(ball[2]), float(ball[3])]
            mass = float(ball[4])
            radius = float(ball[5])
            
            # Create a Ball object from the parameters in the file
            b = Ball(position, velocity, mass, radius)
            self.__balls.append(b)
    
    def read_file(self, file_name):
        """Reads the CSV file and yields each row.
        
        A yield call is more efficient than reading from file directly
        because it reads one row at a time (so less memory-intensive)

        Arguments:
            file_name (str): The name of the file to be read.

        Yields:
            row (str): Each row of the CSV containing information about one
                       ball. The row contains six parameters:
                       1) Position (x)
                       2) Position (y)
                       3) Velocity (x)
                       4) Velocity (y)
                       5) Mass
                       6) Radius
        """
        try:
            f = open(file_name, "rt")
        except IOError:
            raise Exception("File not found: create an initial state file in InitialState module.")
        
        with f as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                yield row
    
    def get_balls(self):
        """Accessor method for generated balls.

        Returns:
            __balls (list): A list containing all of the Ball objects generated
                            from initial conditions.
        """
        return self.__balls