from queue import LifoQueue
from reader import read_file


class CandidateSolutionNode:
    def __init__(self):
        pass

    def get_children(self):
        pass


class LibraryProblem:
    def __init__(self, filepath: str):
        n, t, m, libs, s = read_file(filepath)
        self.num_books, self.signup_times = n, t
        self.scan_speeds, self.libraries, self.scores = m, libs, s

    def populate_stack_with_candidates(self, stack: LifoQueue):
        pass

    def is_single_candidate(self, node) -> bool:
        pass

    def objective_func(self, node) -> int:
        pass

    def upper_bound_func(self, node) -> int:
        pass


def branch_and_bound_solve(problem: LibraryProblem):
    problem_lower_bound = float("-inf")
    candidate_stack = LifoQueue()
    current_optimum = None
    problem.populate_stack_with_candidates(candidate_stack)

    while not candidate_stack.empty():
        node: CandidateSolutionNode = candidate_stack.get()
        if problem.is_single_candidate(node):
            if problem.objective_func(node) > problem_lower_bound:
                current_optimum = node
                problem_lower_bound = problem.objective_func(node)
        else:
            for child_node in node.get_children():
                if problem.upper_bound_func(child_node) >= problem_lower_bound:
                    candidate_stack.put(child_node)

    return current_optimum


print(read_file("resources/a_example.txt"))
