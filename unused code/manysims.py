import pycxsimulator
from pylab import *
import networkx as nx

# Logistical Parameters
n = 1000
capacity = .25*n

# Probabilistic Parameters
P_inf = 0.2
P_die = .01

# Social Distancing Parameters
# conformity = .8
# crowd_thresh = 3

# Functions used in the update process
#####################################
def death_prob():
    if data['infected'] > capacity:
        return 4*P_die
    else:
        return P_die

def recov_prob(x):
    return x / 14

def infection_prob(neighbors):
    return 1 - (1 - P_inf)**neighbors
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

def update(conformity, crowd_thresh):
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

            if random() < infection_prob(x): # Infection
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

    tseries['dead'].append(data['dead'])
    tseries['alive'].append(data['alive'])
    tseries['susceptible'].append(data['susceptible'])
    tseries['infected'].append(data['infected'])
    tseries['recovered'].append(data['recovered'])

    #layout = nx.spring_layout(g, pos = layout, iterations = 2)

def print_info(crowd, conform):
    print("==============================")
    print("Conformity set to: " + str(conform))
    print("Crowd Threshold set to: " +str(crowd))
    print("==============================")
    print()

def run_simulation(num_of_sims=100, len_of_sims=50):
    global data
    all_data = {}

    for i in range(5):
        conform = 0.2 * (5 - i) # 1.0 -> 0.2 conformity

        for j in range(5):
            crowd = j + 1 # crowd threshold 1 -> 5
            simulation = []
            print_info(crowd, conform)

            for k in range(num_of_sims):
                print("Simulation # " + str(k+1))
                initialize()

                for l in range(len_of_sims):
                    update(conform, crowd)

                simulation.append(data)

            all_data[str(i) + ', ' + str(j)] = simulation

    print(all_data)
    return all_data

def plot_all_data_death(data):
    plt.style.use('ggplot')
    gs = GridSpec(5, 5)

    for i in range(5):
        for j in range(5):
            arr = []
            subplot(gs[i, j])

            for result in data[str(i) + ', ' + str(j)]:
                arr.append(result['dead'])

            m, bins, patches = plt.hist(arr, color='skyblue')
            #plt.hlines(0, 0, 80, alpha=0)
            plt.vlines(np.mean(arr), 0, max(m), color='red', linestyles='dashed')
            if i == 4:
                plt.xlabel("Crowd Threshold: " + str(j+1))
            if j == 0:
                plt.ylabel("Conformity:\n" + str(20*(5-i)) + '%')
    plt.show()

def plot_all_data_infected(data, num_of_sims=1000):
    plt.style.use('ggplot')
    gs = GridSpec(5, 5)

    for i in range(5):
        for j in range(5):
            arr = []
            subplot(gs[i, j])

            for result in data[str(i) + ', ' + str(j)]:
                arr.append(result['dead'])

            m, bins, patches = plt.hist(arr, color='green')
            #plt.hlines(0, 0, 80, alpha=0)
            plt.vlines(np.mean(arr), 0, max(m), color='red', linestyles='dashed')
            if i == 4:
                plt.xlabel("Crowd Threshold: " + str(j+1))
            if j == 0:
                plt.ylabel("Conformity:\n" + str(20*(5-i)) + '%')
    plt.show()

def main():
    data = run_simulation(num_of_sims=150)
    plot_all_data_death(data)
    plot_all_data_infected(data)
main()
