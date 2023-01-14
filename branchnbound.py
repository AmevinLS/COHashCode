# flake8: noqa
from queue import LifoQueue, PriorityQueue
from typing import Dict, List
from itertools import combinations, product
from copy import deepcopy
import numpy as np


from baseproblems import LibraryProblem
from greedyproblem import GreedyProblem


class CandidateSolutionNode:
    def __init__(self, num_days: int, lib_order: List[int], books_scan: Dict[int, set]): # noqa
        assert isinstance(lib_order, list)
        assert isinstance(books_scan, dict)
        for lib, books in books_scan.items():
            assert isinstance(lib, int)
            assert isinstance(books, set)
        self.num_days = num_days
        self.lib_order = lib_order
        self.books_scan = books_scan

    def __str__(self):
        res = f"Last day: {self.num_days-1}\n"
        res += f"Lib order: {self.lib_order}\n"
        for lib, books in self.books_scan.items():
            res += f"{lib}: {books}" + "\n"
        return res
    
    def get_scanned_books(self) -> set:
        scanned_books = set()
        for books in self.books_scan.values():
            scanned_books.update(books)
        return scanned_books

    def get_children(self, problem):
        next_poss_libs = set()
        if problem.signup_times[self.lib_order].sum() <= self.num_days:
            all_libs = set(range(len(problem.libraries)))
            next_poss_libs = all_libs.difference(set(self.lib_order))

        next_poss_books = dict()
        cumul_signup_time = 0
        for lib in self.lib_order:
            cumul_signup_time += problem.signup_times[lib]
            if cumul_signup_time > self.num_days: # the current library is still signing up
                break
            remaining_books = set(problem.libraries[lib]).difference(self.get_scanned_books())
            next_poss_books[lib] = list(combinations(remaining_books, problem.scan_speeds[lib]))
            # next_poss_books[lib].append(tuple())

        children = []
        for poss_book_schedule in product(*next_poss_books.values()):
            # Checking whether the schedule repeats books
            # schedule_list = []
            # for next_books in poss_book_schedule:
            #     schedule_list += list(next_books)
            # if len(schedule_list) != len(set(schedule_list)):
            #     continue
            
            # Adding the child (children if we can sign up a new library)
            child_books_scan = deepcopy(self.books_scan)
            libs = list(next_poss_books.keys())
            for i in range(len(libs)):
                child_books_scan[libs[i]].update(poss_book_schedule[i])
            if len(next_poss_libs) == 0:
                child = CandidateSolutionNode(
                    self.num_days+1, self.lib_order, child_books_scan
                )
                children.append(child)
            else:
                for next_poss_lib in next_poss_libs:
                    temp_books_scan = deepcopy(child_books_scan)
                    temp_books_scan.update({next_poss_lib: set()})
                    child = CandidateSolutionNode(
                        self.num_days+1, self.lib_order + [next_poss_lib],
                        temp_books_scan
                    )
                    children.append(child)        
        return children


class BandBProblem(LibraryProblem):
    def __init__(self, filepath: str):
        super().__init__(filepath)

    def populate_stack_with_candidates(self, stack: LifoQueue):
        for lib in range(len(self.libraries)):
            node = CandidateSolutionNode(1, [lib], {lib: set()})
            stack.put(node)

    def is_single_candidate(self, node: CandidateSolutionNode) -> bool:
        return (node.num_days == self.num_days)

    def objective_func(self, node: CandidateSolutionNode) -> int:
        res = 0
        scanned_books = set()
        for books in node.books_scan.values():
            for book in books:
                if book in scanned_books:
                    continue
                res += self.scores[book]
                scanned_books.add(book)
        return res

    def upper_bound_func(self, node: CandidateSolutionNode) -> int:
        # POSSIBLY COME UP WITH BETTER UPPER BOUND FUNCTION
        # return float("inf")
        print("Started upper_bound_func")
        res = 0
        days_left = self.num_days - node.num_days
        for lib in node.lib_order:
            scans_left = days_left * self.scan_speeds[lib]
            unscanned_books = set(self.libraries[lib]).difference(
                set(node.books_scan[lib])
            )
            unscanned_scores = np.array(
                self.scores[list(unscanned_books)]
            )
            unscanned_scores[::-1].sort()
            res += unscanned_scores[:scans_left].sum()
        
        temp_days_left = days_left
        while temp_days_left > 0:
            best_lib, best_score = self._get_best_lib_greedy(
                set(node.lib_order), node.get_scanned_books(), temp_days_left
            )
            if best_lib is None:
                break
            res += best_score
            temp_days_left -= self.signup_times[best_lib]
        print("Finished upper_bound_func")
        return res

    def _get_books_sorted_by_score(self, books):
        # SOMETHING'S REALLY WRONG HERE
        res = (-self.scores[list(books)]).argsort()
        return res
    
    def _get_best_lib_greedy(self, signed_libs, scanned_books: set, days_left: int):
        best_lib = None
        best_score = 0
        for curr_lib in range(len(self.libraries)):
            if curr_lib in signed_libs:
                continue

            curr_signup_t = self.signup_times[curr_lib]
            if curr_signup_t >= days_left:
                continue
            curr_books = self._get_books_sorted_by_score(
                set(self.libraries[curr_lib]).difference(scanned_books)
            )[:(days_left-curr_signup_t)]
            curr_score = self.scores[curr_books].sum()
            if curr_score > best_score:
                best_lib = curr_lib
                best_score = curr_score
        return best_lib, best_score

    def branch_and_bound_solve(self):
        problem_lower_bound = float("-inf")
        candidate_stack = LifoQueue()
        current_optimum = None
        self.populate_stack_with_candidates(candidate_stack)

        i = 0
        while not candidate_stack.empty():
            i+=1
            if i == 20:
                break
            print(f"Stack size: {len(candidate_stack.queue)}")
            node: CandidateSolutionNode = candidate_stack.get()
            if self.is_single_candidate(node):
                print("Arrived in leaf")
                if self.objective_func(node) > problem_lower_bound:
                    current_optimum = node
                    problem_lower_bound = self.objective_func(node)
                    print(f"New lower bound: {problem_lower_bound}")
            else:
                for child_node in node.get_children(self):
                    if self.upper_bound_func(child_node) >= problem_lower_bound:
                        candidate_stack.put(child_node)

        return current_optimum
  

def bad_greedy(problem: LibraryProblem):
    TOTAL_SCORE = 0

    book_counts = np.zeros(problem.num_books)
    for books in problem.libraries:
        for book in books:
            book_counts[book] += 1
    
    adj_book_scores = problem.scores # / book_counts
    lib_scores = np.zeros(problem.num_libs)
    for lib in range(problem.num_libs):
        lib_scores[lib] = adj_book_scores[problem.libraries[lib]].sum() / problem.signup_times[lib]
    lib_order = (-lib_scores).argsort()

    book_queues = []
    for lib in range(problem.num_libs):
        pq = PriorityQueue()
        for book in problem.libraries[lib]:
            pq.put((-adj_book_scores[book], book))
        book_queues.append(pq)

    scanned_status = {book: False for book in range(problem.num_books)}
    lib_is_scanning = np.full(problem.num_libs, False)
    curr_signup_ind = 0
    next_signup_day = problem.signup_times[lib_order[curr_signup_ind]]
    for day in range(problem.num_days):
        if day == next_signup_day:
            lib_is_scanning[curr_signup_ind] = True
        for lib in np.where(lib_is_scanning)[0]:
            books_to_scan = []
            while len(books_to_scan) < problem.scan_speeds[lib]:
                if book_queues[lib].empty():
                    lib_is_scanning[lib] = False
                    break
                _, book = book_queues[lib].get()
                if not scanned_status[book]:
                    books_to_scan.append(book)
            for book in books_to_scan:
                scanned_status[book] = True
                TOTAL_SCORE += problem.scores[book]

    return TOTAL_SCORE


if __name__ == "__main__":
    pass