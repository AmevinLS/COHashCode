# flake8: noqa

from copy import deepcopy

import numpy as np

from baseproblems import NumpyLibraryProblem, profiletime


class AnnealingProblem(NumpyLibraryProblem):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.lib_sums = self.scores_np[self.libraries_np].sum(axis=1).reshape((-1,))

    def random_lib_order(self):
        lib_order = np.arange(0, self.num_libs)
        np.random.shuffle(lib_order)
        return lib_order

    def random_change(self, lib_order):
        res_lib_order = deepcopy(lib_order)
        # ind1 = np.random.randint(len(lib_order)-1)
        # ind2 = ind1+1
        inds = np.arange(self.num_libs)
        np.random.shuffle(inds)
        ind1, ind2 = inds[:2]

        res_lib_order[ind1], res_lib_order[ind2] = res_lib_order[ind2], res_lib_order[ind1]
        return res_lib_order

    def _annealing(self, num_iters, start_temp=10, start_lib_order: list = None):
        leniency = 0.001
        power = np.log(np.log(100)/leniency) / np.log(num_iters)
        alpha = 0.995

        curr_lib_order = start_lib_order
        if curr_lib_order is None:
            curr_lib_order = self.random_lib_order()
        else:
            libs = np.arange(self.num_libs)
            lib_used = np.full(self.num_libs, False)
            lib_used[curr_lib_order] = True
            libs_left = libs[~lib_used]
            curr_lib_order = curr_lib_order + list(libs_left)
        curr_lib_order = np.array(curr_lib_order)

        curr_eval = self.evaluate_lib_order2(curr_lib_order)
        history = [curr_eval]
        temps = [start_temp]
        curr_temp = start_temp
        probs = []
        for k in range(num_iters):
            next_lib_order = self.random_change(curr_lib_order)
            next_eval = self.evaluate_lib_order2(next_lib_order)

            prob = np.exp(-(curr_eval - next_eval) / curr_temp)
            if next_eval > curr_eval:
                prob = 1
            if (next_eval > curr_eval) or np.random.random() < prob:
                curr_lib_order = next_lib_order
                curr_eval = next_eval

            # curr_temp = start_temp / (k+1)**power
            curr_temp = start_temp * alpha**k
            history.append(curr_eval)
            temps.append(curr_temp)
            probs.append(prob)

        return curr_lib_order, history, probs

    @profiletime
    def run_annealing(self, num_iters, start_lib_order: list = None):
        _, short_hist, _ = self._annealing(num_iters=100, start_temp=1000000000, start_lib_order=start_lib_order)
        start_temp = np.mean(short_hist)
        return self._annealing(num_iters, start_temp, start_lib_order)


    def evaluate_lib_order(self, lib_order):
        curr_lib_sums = self.lib_sums[lib_order]
        # book_lib_props = self.scores_np.reshape((-1,1)).repeat(curr_lib_sums.size, axis=1) / curr_lib_sums

        scans_left = self.num_days - self.signup_times[lib_order].cumsum()

        lib_available = np.full(len(lib_order), True)
        book_schedules = {lib: [] for lib in lib_order}
        for book in range(self.num_books):
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

    def evaluate_lib_order2(self, lib_order):
        res_score = 0

        signupcumsum = self.signup_times[lib_order].cumsum()
        mask = signupcumsum < self.num_days
        lib_order = lib_order[mask]

        scans_left = self.num_days - signupcumsum
        book_available = np.full(self.num_books, True)
        days_left = self.num_days
        # for i in range(len(lib_order)):
        for i, (current_lo, current_sl) in enumerate(zip(lib_order, scans_left)):
            # if scans_left[i] <= 0:
            #     break
            if current_sl <= 0:
                break

            # lib = lib_order[i]

            # books = self.libraries[lib]
            books = self.libraries[current_lo]

            # books = books[book_available[books]]
            books = books[np.where(book_available[books])[0]]

            scores = self.scores[books]
            # inds_sorted = scores.argsort()
            # inds_chosen = inds_sorted[:scans_left[i]]

            # if scans_left[i] > scores.size:
            if current_sl > scores.size:
                books_chosen = books
            else:
                # inds_chosen = np.argpartition(scores, -scans_left[i])[-scans_left[i]:]
                inds_chosen = np.argpartition(scores, -current_sl)[-current_sl:]
                books_chosen = books[inds_chosen]

            book_available[books_chosen] = False
            res_score += self.scores[books_chosen].sum()

            # days_left -= self.signup_times[lib]
            days_left -= self.signup_times[current_lo]

        return res_score


class BookFillingProblem(NumpyLibraryProblem):
    def __init__(self, filepath: str):
        super().__init__(filepath)

    def run_book_filling(self, lib_order):
        pass


if __name__ == "__main__":
    TOTAL_SUM = 0

    files = [
        "a_example", "b_read_on", "c_incunabula",
        "d_tough_choices", "e_so_many_books", "f_libraries_of_the_world"
    ]
    for file in files:
        path = f"resources/{file}.txt"

        anneal_problem = AnnealingProblem(path)
        lib_order, history, probs = anneal_problem.run_annealing(num_iters=10000)

        eval = anneal_problem.evaluate_lib_order2(lib_order)
        print(f"File: {file}, Approx_eval: {eval}")
        TOTAL_SUM += eval

    print(f"TOTAL_SUM: {TOTAL_SUM}")
