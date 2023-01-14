# flake8: noqa

from greedyproblem import GreedyProblem
from annealing import AnnealingProblem
import matplotlib.pyplot as plt

if __name__ == "__main__":
    FILE = "resources/f_libraries_of_the_world.txt"
    anneal_problem = AnnealingProblem(FILE)
    greedy_problem = GreedyProblem(FILE)
    lib_order, _ = greedy_problem.greedy()
    print("Greedy finished!")
    lib_order, history, probs = anneal_problem.run_annealing(num_iters=10000, start_lib_order=lib_order)
    fig, axs = plt.subplots(2, 1, figsize=(10, 7))
    axs[0].plot(history)
    axs[0].set_title("Evaluation history")
    axs[1].scatter(range(len(probs)), probs)
    axs[1].set_title("Probabilities of accepting new lib_order")
    plt.show()