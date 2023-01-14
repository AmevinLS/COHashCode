# flake8: noqa

import cProfile
import pstats
from copy import deepcopy

import numpy as np

from reader import read_file


def profiletime(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        stream = open("test.txt", "w")
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumtime")
        stats.print_stats()
        stream.close()

        return result

    return wrapper


class BadSolutionException(Exception):
    pass

class LibraryProblem:
    def __init__(self, filepath: str):
        n, t, m, libs, s, d = read_file(filepath)
        _, self.signup_times = n, t
        self.scan_speeds, self.libraries, self.scores = m, libs, s
        self.NUM_DAYS = d
        self.books_ordered = (-self.scores).argsort()
        self.NUM_LIBS = len(self.libraries)
        self.NUM_BOOKS = len(self.scores)

    def score_solution(self, lib_order, assignment: dict):
        if len(lib_order) != len(set(lib_order)):
            raise BadSolutionException("Trying to signup a library more than once")

        if (self.signup_times[lib_order].sum() > self.NUM_DAYS):
            raise BadSolutionException(
                f"Signup times ({self.signup_times[lib_order].sum()}) greater than num_days ({self.NUM_DAYS})"
            )

        days_left = self.NUM_DAYS
        books_scanned = set()
        for lib in lib_order:
            books = assignment[lib]
            days_left -= self.signup_times[lib]
            scans_left = self.scan_speeds[lib] * days_left
            if len(books) > scans_left:
                raise BadSolutionException("More books than available scans")
            for book in books:
                if book not in self.libraries[lib]:
                    raise BadSolutionException("Trying to scan book not in library")
            books_scanned.update(books)
        return self.scores[list(books_scanned)].sum()


class NumpyLibraryProblem(LibraryProblem):
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.orig_scores = deepcopy(self.scores)

        self.null_book = len(self.scores)
        self.scores_np = np.append(self.scores, 0)
        self.scores_np = self.scores_np.astype(np.int32)
        self.signup_times = np.array(self.signup_times, dtype=np.int32)

        self.libraries_np = deepcopy(self.libraries)
        max_libsize = max([library.size for library in self.libraries_np])
        for i in range(self.NUM_LIBS):
            self.libraries_np[i] = np.append(self.libraries_np[i], np.full(max_libsize - self.libraries_np[i].size, self.null_book))
        self.libraries_np = np.array(self.libraries_np)