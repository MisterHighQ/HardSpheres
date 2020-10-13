Usman Siddiqui
02 December 2018
Computing Project Cycle 2

Thermodynamics Snooker

######## INSTRUCTIONS ########

- Extract .zip to a folder

- Open Config.py, set the desired parameters, and save the file

- Open InitialState.py and run it by pressing F5 in Spyder (this produces an `InitialState.csv` file according to the parameters specified in Config.py, which is necessary for the simulation to run)

- (Optional) If outputting data to file, open WriteOutput.py, customize output data according to instructions, and save the file

- Open App.py and run it by pressing F10 in Spyder

- After animation has concluded, close the animation window (important if outputting data)

- Output data will be saved in a CSV file with a numerical timestamp (e.g. `1542627068.csv`)

NOTE: The initial state of the system is loaded from `InitialState.csv` file each time. This is
      important so that the experiment can be repeated multiple times from the same
      initial state. To generate a new state, InitialState.py MUST be run before running App.py         each time.


######## FILES INCLUDED ########

- App.py [Application entry point]

- Ball.py [Ball class containing methods for collision prediction, rebound velocity calculation and ball rendering]

- Config.py [Configuration file containing parameters that can be modified by the user]

- InitialState.py [Standalone module which generates an initial state according to the configurations in Config.py and saves this arrangement to a CSV file (e.g. `InitialState.csv`)]

- ParseState.py [Loads the initial state from a CSV file]

- WriteOutput.py [Outputs data to a CSV file for data analysis in other software]