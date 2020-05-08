import epidemic
import json

class Simulations:


    """
    Controller for running many epidemic simulations and saving data.

    Args:
        size [int]: Number of nodes for each simulation.
        num_of_sims [int]: Number of simulations for a given set of parameters.
        len_of_sims [int]: Number of time steps until the simulation ends.

    Attributes:
        all_data [dict]: a dictionary to store all simulation data.
        size [int]: Number of simulations for a given set of parameters.
        sims [int]: Number of time steps until the simulation ends.
    """


    def __init__(self, size, num_of_sims, len_of_sims=50):
        """ Runs simluations while scanning through the two main parameters."""
        self.all_data = {}
        self.size = size
        self.sims = num_of_sims

        for i in range(5):
            conformity = 0.2 * (5 - i)

            for j in range(5):
                crowd = j + 1
                simulations = []
                self.print_info(conformity, crowd)

                for k in range(num_of_sims):
                    print("Simulation # " + str(k+1))
                    E = epidemic.Epidemic(size)

                    for l in range(len_of_sims):
                        E.update(conformity, crowd)

                    simulations.append(E.data)
                self.all_data[str(i) + ', ' + str(j)] = simulations

        print()
        print("COMPLETE")

    def print_info(self, conformity, crowd):
        """ Prints information about the next set of simulations."""
        print("==============================")
        print("Conformity set to: " + str(round(conformity, 1)))
        print("Crowd Threshold set to: " +str(crowd))
        print("==============================")
        print()

    def export_data(self):
        """ Saves all_data as a json file to be used for visualization."""
        f = open("simulation-data-%d-%d.json." % (self.size, self.sims), 'w')
        json.dump(self.all_data, f, indent=4)
        f.close()
