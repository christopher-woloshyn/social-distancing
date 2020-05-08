import matplotlib.pyplot as plt
from numpy import mean
import json

def plot_data_death(data):
    """ Plot death histograms for each parameter combination in the sims."""
    plt.style.use('ggplot')
    gs = plt.GridSpec(5, 5)
    plt.suptitle('Comparison of Different Social Distancing Parameters ', fontsize='x-large')

    for i in range(5):
        for j in range(5):
            arr = []
            plt.subplot(gs[i, j])

            for result in data[str(i) + ', ' + str(j)]:
                arr.append(result['dead'])

            m, bins, patches = plt.hist(arr, color='skyblue')
            plt.hlines(0, 0, 600, alpha=0)
            plt.vlines(mean(arr), 0, max(m), color='red', linestyles='dashed')
            if i == 4:
                plt.xlabel("Crowd Threshold: " + str(j+1))
            if j == 0:
                plt.ylabel("Conformity:\n" + str(20*(5-i)) + '%')
    plt.show()

def main():
    file = 'simulation-data-5000-1000.json'
    with open(file) as json_file:
        data = json.load(json_file)

    plot_data_death(data)

main()
