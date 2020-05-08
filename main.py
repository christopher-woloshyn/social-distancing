import simulations

def main():
    N = 5000
    sims = 1000
    S = simulations.Simulations(N, sims)
    S.export_data()
main()
