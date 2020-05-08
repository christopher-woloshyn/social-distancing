"""
This code is a rewrite and modification of the source code which was developed
by Dr. Hiroki Sayama and his 'SSIE 641: Advanced Topics in Network Science'
class on March 11, 2020.
"""

import numpy as np
import networkx as nx
from random import random


class Epidemic:


    """
    Network epidemic model used to examine the affects of social distancing.

    Args:
        size [int]: Number of nodes in the network for the simulation.
        p_infect [float]: probability a node gets infected from another node.
        p_die [float]: probability an infected node is removed from the network.
        init_infect [float]: initial infection rate of nodes.

    Attributes:
        g [Graph]: Barabasi-Albert random network representing interactions.
        p_infect [float]: probability a node gets infected from another node.
        p_die [float]: probability an infected node is removed from the network.
        capacity [int]: represents healthcare capacity at 1/4 total population.
        data [dict]: stores information about the simulation at each time step.
    """


    def __init__(self, size, p_infect=0.2, p_die=0.01, init_infect=0.01):
        """ Initialize barabasi random network and set initial infected."""
        self.g = nx.barabasi_albert_graph(size, 2)
        self.p_infect = p_infect
        self.p_die = p_die
        self.capacity = size // 4

        accum = self.set_patient0(init_infect)
        self.data = {'dead': 0,
                    'alive': size,
                    'susceptible': size - accum,
                    'infected': accum,
                    'recovered': 0
                    }

    def set_patient0(self, init_infect):
        """ Set initial infected population based on provided initial rate"""
        accum = 0
        for i in self.g.nodes:
            if random()  < init_infect:
                self.g.nodes[i]['state'] = 1
                accum += 1
            else:
                self.g.nodes[i]['state'] = 0

        return accum

    def update(self, conformity, crowd_thresh):
        """ Changes node state and edges based on neighbors and self status."""
        node_IDs = list(self.g.nodes)
        np.random.shuffle(node_IDs)

        for i in node_IDs:
            # IF INFECTED
            if self.g.nodes[i]['state'] > 0.5:

                if random() < self.death_prob():
                    self.g.remove_node(i)
                    self.data['dead'] += 1
                    self.data['alive'] -= 1
                    self.data['infected'] -= 1

                elif random() < self.recov_prob(i):
                    self.g.nodes[i]['state'] = 0.5
                    self.data['recovered'] += 1
                    self.data['infected'] -= 1

                else:
                    self.g.nodes[i]['state'] += 1

            # IF RECOVERED
            elif self.g.nodes[i]['state'] > 0:
                if 'neighbors' in self.g.nodes[i]:
                    if len(self.g.nodes[i]['neighbors']) > 0:
                        # Exit Isolation
                        j = np.random.choice(self.g.nodes[i]['neighbors'])
                        if j in self.g.nodes:
                            self.g.add_edge(i, j)

            # IF SUSCEPTIBLE
            else:
                num_inf_nbs = len([1 for j in self.g.neighbors(i)\
                                if self.g.nodes[j]['state'] > 0.5])

                if random() < self.infection_prob(num_inf_nbs):
                    # Node i gets infected
                    self.g.nodes[i]['state'] = 1
                    self.data['infected'] += 1
                    self.data['susceptible'] -= 1

                else:
                    # Node i does not get infected
                    self.g.nodes[i]['state'] = self.g.nodes[i]['state']

                # Exit Isolation
                if 'neighbors' in self.g.nodes[i]:
                    if len(self.g.nodes[i]['neighbors']) > 0:
                        if hum_inf_nbs < crowd_thresh:
                            j = choice(self.g.nodes[i]['neighbors'])

                            if j in self.g.nodes:
                                self.g.add_edge(i, j)

                # Enter Isolation
                if num_inf_nbs >= crowd_thresh:
                    past_neighbors = list(self.g.neighbors(i))

                    for neighbor in past_neighbors:
                        if random() < conformity:
                            self.g.remove_edge(i, neighbor)
                            self.g.nodes[i]['past_neighbors'] = past_neighbors

    def death_prob(self):
        """ Death probability mult. by 4 if healthcare capacity is exceeded."""
        if self.data['infected'] > self.capacity:
            return 4*self.p_die
        else:
            return self.p_die

    def recov_prob(self, idx):
        """ Recovery probability increases the longer a node is infected."""
        return self.g.nodes[idx]['state'] / 14

    def infection_prob(self, neighbors):
        """ Binomial distribution based on the number of infected neighbors."""
        return 1 - (1 - self.p_infect)**neighbors
