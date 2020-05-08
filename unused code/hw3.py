"""
This code is a modification of the source code which was developed by Dr.
Hiroki Sayama and his 'SSIE 641: Advanced Topics in Network Science' class on
March 11, 2020.
"""

import pycxsimulator
from pylab import *
import networkx as nx

# Logistical Parameters
n = 500
capacity = .25*n

# Probabilistic Parameters
P_inf = 0.2
P_die = .01

# Social Distancing Parameters
conformity = .8
crowd_thresh = 3

# Functions used in the update process
#####################################
def death_prob():
    if data['infected'] > capacity:
        return 4*P_die
    else:
        return P_die

def recov_prob(x):
    return x / 14

def infection_prob(x, s):
    return 1 - (1 - P_inf)**x
#######################################

def initialize():
    global g, layout, data, tseries
    g = nx.barabasi_albert_graph(n, 2)

    # Setting an initial population of infected agents.
    accum = 0
    for i in g.nodes:
        if random() < 0.01:
            g.nodes[i]['state'] = 1
            accum += 1
        else:
            g.nodes[i]['state'] = 0

    layout = nx.spring_layout(g)
    data = {'dead': 0,
            'alive': n,
            'susceptible': n - accum,
            'infected': accum,
            'recovered': 0
           }
    tseries = {'dead': [data['dead']],
            'alive': [data['alive']],
            'susceptible': [data['susceptible']],
            'infected': [data['infected']],
            'recovered': [data['recovered']]
            }

    print(data)

def observe():
    global g, layout, data, tseries
    style.use('ggplot')

    if n > 500:
        title('TITLE')
        gs = GridSpec(1, 2)
        subplot(gs[0])
        cla() # to clear the visualization space
        hlines(capacity, 0, len(tseries['dead']), lw=2, colors='coral',\
                linestyles='dashed', label='Healthcare capacity')
        plot(tseries['susceptible'], 'g', label='susceptible')
        plot(tseries['infected'], 'r', label='infected')
        plot(tseries['recovered'], 'b', label='recovered')
        legend()

        subplot(gs[1])
        cla()
        plot(tseries['alive'], 'g', label='alive')
        plot(tseries['dead'], 'r', label='dead')
        legend()

    else:
        gs = GridSpec(2, 2)

        subplot(gs[:, 0])
        suptitle('Social distancing crowd threshold: ' + str(crowd_thresh)\
                + '\n Conformity to social distancing: '\
                + str(int(conformity*100)) + '%')

        cla() # to clear the visualization space
        if data['infected'] < capacity:
            nx.draw(g, node_color=[g.nodes[i]['state'] for i in g.nodes],
                    vmin=0, vmax=1, pos=layout)

        else:
            nx.draw(g, node_color=[g.nodes[i]['state'] for i in g.nodes],
                    edge_color=['red' for i in g.edges],
                    width=[log10(data['infected']) for i in g.edges],
                    vmin = 0, vmax = 1, pos = layout)

        subplot(gs[0, 1])
        cla() # to clear the visualization space
        hlines(capacity, 0, len(tseries['dead']), lw=2, colors='coral',\
                linestyles='dashed', label='Healthcare capacity')
        plot(tseries['susceptible'], 'g', label='susceptible')
        plot(tseries['infected'], 'r', label='infected')
        plot(tseries['recovered'], 'b', label='recovered')
        legend()

        subplot(gs[1, 1])
        cla()
        plot(tseries['alive'], 'g', label='alive')
        plot(tseries['dead'], 'r', label='dead')
        legend()

def update():
    global g, layout, data, tseries

    node_IDs = list(g.nodes)
    shuffle(node_IDs)

    for i in node_IDs:
        # IF INFECTED
        if g.nodes[i]['state'] > 0.5:

            if random() < death_prob(): # Death
                g.remove_node(i)
                data['dead'] += 1
                data['alive'] -= 1
                data['infected'] -= 1

            elif random() < recov_prob(g.nodes[i]['state']):
                g.nodes[i]['state'] = 0.5 # Recovery
                data['recovered'] += 1
                data['infected'] -= 1

            else:
                g.nodes[i]['state'] = g.nodes[i]['state'] + 1 # Still ill

        # IF RECOVERED
        elif g.nodes[i]['state'] > 0:
            if 'past_neighbors' in g.nodes[i]\
            and len(g.nodes[i]['past_neighbors']) > 0: # Exit Isolation
                j = choice(g.nodes[i]['past_neighbors'])
                if j in g.nodes:
                    g.add_edge(i, j)

        # IF SUSCEPTIBLE
        else:

            # Calculate the number of infected neighbors for each node
            x = len([1 for j in g.neighbors(i) if g.nodes[j]['state'] > 0.5])

            if random() < infection_prob(x, g.nodes[i]['state']): # Infection
                g.nodes[i]['state'] = 1
                data['infected'] += 1
                data['susceptible'] -= 1

            else: # No Infection
                g.nodes[i]['state'] = g.nodes[i]['state']

            if 'past_neighbors' in g.nodes[i]\
            and len(g.nodes[i]['past_neighbors']) > 0: # Exit Isolation
                if x < crowd_thresh:
                    j = choice(g.nodes[i]['past_neighbors'])
                    if j in g.nodes:
                        g.add_edge(i, j)

            if x >= crowd_thresh: # Enter Isolation
                past_neighbors = list(g.neighbors(i))
                for j in past_neighbors:
                    if random() < conformity:
                        g.remove_edge(i, j)
                        g.nodes[i]['past_neighbors'] = past_neighbors

    # Update the Time Series data.
    print(data)

    tseries['dead'].append(data['dead'])
    tseries['alive'].append(data['alive'])
    tseries['susceptible'].append(data['susceptible'])
    tseries['infected'].append(data['infected'])
    tseries['recovered'].append(data['recovered'])

    layout = nx.spring_layout(g, pos = layout, iterations = 2)

pycxsimulator.GUI().start(func=[initialize, observe, update])
