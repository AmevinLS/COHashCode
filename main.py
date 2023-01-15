# flake8: noqa

from baseproblems import Instance, LibraryProblem
from greedyproblem import IterativeSortingProblem
from annealing import AnnealingProblem, BookFillingProblem
from threading import Timer
import sys
import warnings

class Solver:
    def __init__(self, in_file: str|None = None, out_file: str|None = None):
        self.stopped = False
        self.instance = None
        self.greedy_problem = None
        self.anneal_problem = None
        self.bookfill_problem = None
        
        self.best_lib_order = None
        self.best_assignments = None

        self.in_file = in_file
        self.out_file = out_file
    
    def solve(self):
        self.instance = Instance(self.in_file)

        self.greedy_problem = IterativeSortingProblem(self.instance)
        lib_order, assignments = self.greedy_problem.run_greedy()
        del self.greedy_problem
        self.greedy_problem = None

        self.best_lib_order, self.best_assignments = lib_order, assignments

        if self.stopped:
            self.flush_results()
            return
        
        self.anneal_problem = AnnealingProblem(self.instance)
        lib_order, _, _ = self.anneal_problem.run_annealing(num_iters=10000, start_lib_order=self.best_lib_order)
        del self.anneal_problem
        self.anneal_problem = None

        if self.stopped:
            self.flush_results()
            return

        self.bookfill_problem = BookFillingProblem(self.instance)
        assignments = self.bookfill_problem.run_book_filling(lib_order)
        del self.anneal_problem
        self.anneal_problem = None

        if self.stopped:
            self.flush_results()
            return

        is_score = self.bookfill_problem.score_solution(self.best_lib_order, self.best_assignments)
        sa_score = self.bookfill_problem.score_solution(lib_order, assignments)
        if sa_score > is_score:
            self.best_lib_order, self.best_assignments = lib_order, assignments

        self.flush_results()
        return

    def flush_results(self):
        if self.out_file is None:
            f = sys.stdout
        else:
            f = open(self.out_file, mode="w")

        print(len(self.best_lib_order), file=f)
        for lib in self.best_lib_order:
            print(lib, len(self.best_assignments[lib]), file=f)
            print(*self.best_assignments[lib], file=f)

    def stop(self):
        self.stopped = True
        if self.greedy_problem is not None:
            self.greedy_problem.stop()
        if self.anneal_problem is not None:
            self.anneal_problem.stop()
        if self.bookfill_problem is not None:
            self.bookfill_problem.stop()

    def get_score(self):
        problem = LibraryProblem(self.instance)
        return problem.score_solution(self.best_lib_order, self.best_assignments) 

if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    solver = Solver()
    timer = Timer(270, solver.stop)
    timer.start()
    try:
        solver.solve()
    except Exception:
        pass
    finally:
        timer.cancel()