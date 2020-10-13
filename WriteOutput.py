import csv
from numpy import linalg as la
import time

class WriteOutput():
    """Outputs statistical data to CSV file for analysis.
    
    Arguments:
        App (App): App object containing all information about the simulation,
                   which is used to measure observables of the system.
    """
    def __init__(self, App):
        self.__output = [] # No accessor method (not accessed outside class)
        self.App = App
        self.should_output = App.should_output

    def print_line(self):
        """Measures key observables of system."""
        if self.should_output == True:
            t = self.App.time
            state = self.continuous_measurements()
    
            # Index of state refers to different output quantities
            # 0) Total kinetic energy
            # 1) RMS speed
            # 2) Pressure
            # 3) Inner Concentration
            
            # Change the index below to output different quantities
            out = [t, state[1]] # Will output time and RMS speed
            self.__output.append(out)

    def print_state(self):
        """Measures key observables of every ball in system."""
        if self.should_output == True:
            t = self.App.time
            state = self.state_measurements()
    
            # Index of state refers to different quantities
            # 0) Particle speeds
            # 1) Kinetic energies
            # 2) Mean free paths
            # 3) Momentum
            
            # Change the index below to output different quantities
            out = state[0]
            out.insert(0, t) # Attach the time variable as the first output index
            self.__output.append(out)

    def continuous_measurements(self):
        """Measures state variables and returns array of value for each ball.
        
        This calculation is less intensive than state_measurements so may be
        performed at each collision.

        Returns:
            A list whose elements are:
            0) Total kinetic energy
            1) RMS speed
            2) Pressure
            3) Inner Concentration (R <= 50)
        """
        kinetic_energy = 0.0
        rms_speed_sum = 0.0
        pressure = ((self.App.delta_p /
                   (Self.App.self.container_circumference * self.App.time))
                   if self.App.time > 0.0 else 0.0)
        inner_concentration = 0

        for b in self.App.balls():
            kinetic_energy += b.kinetic_energy()
            rms_speed_sum += b.speed_squared()
            inner_concentration += 1 if la.norm(b.position()) <= 50 else 0

        return [kinetic_energy, rms_speed_sum / self.App.balls_in_container,
                pressure, inner_concentration]

    def state_measurements(self):
        """Measures state variables and returns array of value for each ball.
        
        Warning: This is an expensive calculation so should not be performed
                 for every collision. The state measurement is used to observe
                 the state at the start and end to determine initial and
                 equilibrium states.

        Returns:
            A list whose elements are:
            0) A list of the speeds of all particles
            1) A list of the kinetic energies of all particles
            2) A list of the mean free paths of all partciles
            3) A list of the momenta of all particles as [px, py]
        """
        speed = []
        kinetic_energy = []
        mean_free_path = []
        momentum = []
        for b in self.App.balls():
            speed.append(la.norm(b.velocity()))
            kinetic_energy.append(b.kinetic_energy())
            mean_free_path.append(b.mean_free_path())
            momentum.extend(b.momentum())

        return [speed, kinetic_energy, mean_free_path, momentum]

    def save(self):
        """Writes contents of `self.__output` to a CSV file.
        
        The name of the CSV file is dynamically generated using the current
        timestamp. This is so that previous data files are not overwritten when
        this method is called."""
        
        if self.should_output == True:
            file_name = "{}.csv".format(int(time.time()))
            
            try:
                f = open(file_name, "wt")
            except IOError:
                raise Exception("Unknown error occurred while outputting data"
                                "in WriteOutput module.")
            
            with f as csv_file:
                writer = csv.writer(csv_file, lineterminator = "\n")
                writer.writerows(self.__output)
    
    def format_output(self):
        """Outputs each row in `self.__output` for writing to file.
        
        Yields:
            line [list]: A list containing state variables where the first
                         element is the time in the simulation and subsequent
                         elements represent different state measurements.
        """

        # A yield call is more efficient than writing to the file directly
        # because it writes one row at a time (so less memory-intensive)
        for line in self.__output:
            yield line
