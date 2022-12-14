import numpy as np

FILE = 'resources/a_example.txt'

with open(FILE, 'r', encoding='utf-8') as f:
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
        is_odd = not is_odd

del params
del is_odd
del i

print(n)
print(t)
print(m)
for library in libraries:
    print(library)
