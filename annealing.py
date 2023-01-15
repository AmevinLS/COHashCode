# flake8: noqa

from copy import deepcopy

import numpy as np

from baseproblems import NumpyLibraryProblem, profiletime, Instance


class AnnealingProblem(NumpyLibraryProblem):
    def __init__(self, instance: Instance):
        super().__init__(instance)
        self.stopped = False

    def stop(self):
        self.stopped = True
        print("Annealing stopped")

    def random_lib_order(self):
        lib_order = np.random.permutation(self.NUM_LIBS)
        return lib_order

    def random_change(self, lib_order):
        res_lib_order = deepcopy(lib_order)
        ind1, ind2 = np.random.choice(self.NUM_LIBS, 2, replace=False)
        res_lib_order[ind1], res_lib_order[ind2] = res_lib_order[ind2], res_lib_order[ind1]
        return res_lib_order

    def _annealing(self, num_iters, start_temp=10, start_lib_order: list = None):
        alpha = 0.997

        curr_lib_order = start_lib_order
        if curr_lib_order is None:
            curr_lib_order = self.random_lib_order()
        else:
            libs = np.arange(self.NUM_LIBS)
            lib_used = np.full(self.NUM_LIBS, False)
            lib_used[curr_lib_order] = True
            libs_left = libs[~lib_used]
            curr_lib_order = curr_lib_order + list(libs_left)
        curr_lib_order = np.array(curr_lib_order)

        curr_eval = self.evaluate_lib_order_fast(curr_lib_order)
        history = [curr_eval]
        curr_temp = start_temp
        probs = []
        for k in range(num_iters):
            if self.stopped:
                break
            next_lib_order = self.random_change(curr_lib_order)
            next_eval = self.evaluate_lib_order_fast(next_lib_order)

            prob = np.exp((next_eval - curr_eval) / curr_temp)
            if next_eval > curr_eval:
                prob = 1
            if np.random.random() <= prob:
                curr_lib_order = next_lib_order
                curr_eval = next_eval

            curr_temp = start_temp * alpha**k
            history.append(curr_eval)
            probs.append(prob)

        signupcumsum = self.signup_times[curr_lib_order].cumsum()
        mask = signupcumsum < self.NUM_DAYS
        curr_lib_order = curr_lib_order[mask]

        return curr_lib_order, history, probs

    @profiletime
    def run_annealing(self, num_iters, start_lib_order: list = None):
        _, short_hist, _ = self._annealing(num_iters=100, start_temp=1000000000, start_lib_order=start_lib_order)
        start_temp = np.mean(short_hist)
        return self._annealing(num_iters, start_temp, start_lib_order)

    ### NOT USED
    def evaluate_lib_order(self, lib_order):
        curr_lib_sums = self.lib_sums[lib_order]
        # book_lib_props = self.scores_np.reshape((-1,1)).repeat(curr_lib_sums.size, axis=1) / curr_lib_sums

        scans_left = self.NUM_DAYS - self.signup_times[lib_order].cumsum()

        lib_available = np.full(len(lib_order), True)
        book_schedules = {lib: [] for lib in lib_order}
        for book in range(self.NUM_BOOKS):
            if not lib_available.any():
                break
            lib_contains_book = np.any(self.libraries_np == book, axis=1).reshape(-1)[lib_order]
            if not (lib_available & lib_contains_book).any():
                continue
            book_lib_adj_scores = self.scores_np[book] / curr_lib_sums
            inds_sorted = (-book_lib_adj_scores).argsort()
            best_ind = inds_sorted[(lib_available[inds_sorted] & lib_contains_book[inds_sorted]).argmax()]
            best_lib = lib_order[best_ind]
            book_schedules[best_lib].append(book)
            if len(book_schedules[best_lib]) == scans_left[best_ind]:
                lib_available[best_ind] = False

        return book_schedules

    ### NOT USED
    def evaluate_lib_order2(self, lib_order):
        res_score = 0

        signupcumsum = self.signup_times[lib_order].cumsum()
        mask = signupcumsum < self.NUM_DAYS
        lib_order = lib_order[mask]

        scans_left = self.NUM_DAYS - signupcumsum
        book_available = np.full(self.NUM_BOOKS, True)
        for i, (current_lo, current_sl) in enumerate(zip(lib_order, scans_left)):
            if current_sl <= 0:
                break

            books = self.libraries[current_lo]

            books = books[np.where(book_available[books])[0]]

            scores = self.scores[books]

            if current_sl > scores.size:
                books_chosen = books
            else:
                inds_chosen = np.argpartition(scores, -current_sl)[-current_sl:]
                books_chosen = books[inds_chosen]

            book_available[books_chosen] = False
            res_score += self.scores[books_chosen].sum()

        return res_score

    def evaluate_lib_order_fast(self, lib_order):
        res_score = 0

        signupcumsum = self.signup_times[lib_order].cumsum()
        mask = signupcumsum < self.NUM_DAYS
        lib_order = lib_order[mask]

        scans_left = (self.NUM_DAYS - signupcumsum)[mask]
        avg_scans_left = int(scans_left.mean())
        
        scores = self.scores_np[self.libraries_np]
        
        if scores.shape[1] < avg_scans_left:
            pass
        else:
            scores = np.partition(scores, -avg_scans_left, axis=1)[:, -avg_scans_left:]

        res_score = scores[:, :avg_scans_left].sum()

        return res_score


class BookFillingProblem(NumpyLibraryProblem):
    def __init__(self, instance: Instance):
        super().__init__(instance)
        self.stopped = False

    def stop(self):
        self.stopped = True

    def run_book_filling(self, lib_order):
        assignments = {lib: [] for lib in lib_order}
        
        signupcumsum = self.signup_times[lib_order].cumsum()
        scans_left = self.NUM_DAYS - signupcumsum
        book_available = np.full(self.NUM_BOOKS, True)
        for i, (current_lo, current_sl) in enumerate(zip(lib_order, scans_left)):
            if self.stopped:
                break

            books = self.libraries[current_lo]
            books = books[np.where(book_available[books])[0]]

            scores = self.scores[books]

            if current_sl > scores.size:
                books_chosen = books
            else:
                inds_chosen = np.argpartition(scores, -current_sl)[-current_sl:]
                books_chosen = books[inds_chosen]

            book_available[books_chosen] = False
            assignments[current_lo] = books_chosen
        
        return assignments


if __name__ == "__main__":
    TOTAL_SUM = 0

    files = [
        "a_example", "b_read_on", "c_incunabula",
        "d_tough_choices", "e_so_many_books", "f_libraries_of_the_world"
    ]
    for file in files:
        path = f"resources/{file}.txt"
        instance = Instance(path)
        anneal_problem = AnnealingProblem(instance)
        lib_order, history, probs = anneal_problem.run_annealing(num_iters=1000)

        bookfill_problem = BookFillingProblem(instance)
        assignments = bookfill_problem.run_book_filling(lib_order)

        result = bookfill_problem.score_solution(lib_order, assignments)
        print(f"File: {file}, Results: {result}")
        TOTAL_SUM += result

    print(f"TOTAL_SUM: {TOTAL_SUM}")
