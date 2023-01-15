import numpy as np


def read_file(filepath: str):
    """
    Reads a library problem file and returns a tuple of 'np.array's
    Returns: (nums_books, signup_times, scan_speeds, libraries, scores)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        B, L, D = map(int, f.readline().split(' '))
        n = np.zeros(L, dtype=np.uintc)
        t = np.zeros(L, dtype=np.uintc)
        m = np.zeros(L, dtype=np.uintc)
        libraries = []

        params = tuple(map(int, f.readline().split(' ')))
        s = np.array(params, dtype=np.uintc)

        is_odd = True
        i = 0
        for line in f:
            if is_odd:
                n[i], t[i], m[i] = map(int, line.split(' '))
            else:
                params = tuple(map(int, line.split(' ')))
                libraries.append(np.array(params, dtype=np.uintc))
                i += 1
                if i == L:
                    break
            is_odd = not is_odd

    del params
    del is_odd
    del i

    return n, t, m, libraries, s, D


def read_console():
    B, L, D = map(int, input().split(' '))
    n = np.zeros(L, dtype=np.uintc)
    t = np.zeros(L, dtype=np.uintc)
    m = np.zeros(L, dtype=np.uintc)
    libraries = []

    params = tuple(map(int, input().split(' ')))
    s = np.array(params, dtype=np.uintc)

    is_odd = True
    i = 0
    while True:
        line = input()
        if is_odd:
            n[i], t[i], m[i] = map(int, line.split(' '))
        else:
            params = tuple(map(int, line.split(' ')))
            libraries.append(np.array(params, dtype=np.uintc))
            i += 1
            if i == L:
                break
        is_odd = not is_odd

    del params
    del is_odd
    del i

    return n, t, m, libraries, s, D
