# flake8: noqa

import numpy as np
from baseproblems import NumpyLibraryProblem

class GreedyProblem(NumpyLibraryProblem):
    def __init__(self, filepath: str):
        super().__init__(filepath)

        self.lib_evals = np.zeros(self.num_libs)
        
        self.libs_used = np.full(self.num_libs, False)
            
    
    def evaluate_lib(self, lib, days_left: int):
        scans_left = (days_left - self.signup_times[lib]) * self.scan_speeds[lib]
        
        # books_left = set(self.libraries[lib]) - self.scanned_books
        # books_sorted = np.array(
        #     sorted(books_left, key=lambda book: self.scores[book])
        # )
        # chosen_books = books_sorted[:scans_left]

        inds = (-self.scores_np[self.libraries_np[lib]]).argsort()
        books_sorted = self.libraries_np[lib][inds]
        chosen_books = books_sorted[:scans_left]

        if len(chosen_books) == 0:
            return 0, chosen_books

        lib_eval = self.scores_np[chosen_books].sum() / self.signup_times[lib]
        return lib_eval, chosen_books[chosen_books != self.null_book]

    def _update_lib_evals(self, days_left: int):
        scans_left = (days_left - self.signup_times.astype(np.int32)) * self.scan_speeds
        scans_left[scans_left < 0] = 0
        libs_books_scores = self.scores_np[self.libraries_np]
        libs_books_scores = -np.sort(-libs_books_scores, axis=1)
        
        _inds = np.arange(libs_books_scores.shape[1])
        _inds = np.tile(_inds, libs_books_scores.shape[0]).reshape((-1, _inds.size))
        mask = _inds < scans_left.reshape((scans_left.size, 1))
        self.lib_evals = libs_books_scores.sum(axis=1, where=mask) / (self.signup_times)**2

        self.lib_evals[self.libs_used] = 0

    def select_lib(self) -> int:
        best_lib = self.lib_evals.argmax()
        return best_lib

    def remove_books(self, books):
        self.scores_np[books] = 0

    def greedy(self):
        days_left = self.num_days
        lib_order = []
        lib_books_scanned = dict()
        while days_left > 1:
            if np.all(self.libs_used):
                break
            
            self._update_lib_evals(days_left)
            best_lib = self.select_lib()
            if self.lib_evals[best_lib] == 0:
                break
            _, chosen_books = self.evaluate_lib(best_lib, days_left)
            lib_order.append(best_lib)
            lib_books_scanned[best_lib] = chosen_books
            self.libs_used[best_lib] = True
            self.remove_books(chosen_books)

            days_left -= self.signup_times[best_lib]
        
        return lib_order, lib_books_scanned


if __name__ == "__main__":
    TOTAL_SUM = 0

    files = [
        "a_example", "b_read_on", "c_incunabula", 
        "d_tough_choices", "e_so_many_books", "f_libraries_of_the_world"
    ]
    for file in files:
        path = f"resources/{file}.txt"
        problem = GreedyProblem(path)
        lib_order, lib_books_scanned = problem.greedy()
        result = problem.score_solution(lib_order, lib_books_scanned)
        print(f"File: {file}, Result: {result}")
        TOTAL_SUM += result

    print(f"TOTAL_SUM: {TOTAL_SUM}")