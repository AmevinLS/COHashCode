if __name__ == '__main__':
    import numpy as np

    from reader import read_file

    FILE = 'resources/a_example.txt'

    n, t, m, libraries, s = read_file(FILE)

    print(n)
    print(t)
    print(m)
    for library in libraries:
        print(library)
