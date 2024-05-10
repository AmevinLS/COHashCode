# Google's HashCode 2020: Book Scanning Solution

This is an attempt at solving the 2020 HashCode problem - see description [here](https://github.com/Elzawawy/hashcode-book-scanning).

## How to run:
```
git clone https://github.com/AmevinLS/COHashCode
cd COHashCode
python main.py
```

Below is a summary, but the full report going in-depth of explanations can be found in the Google Doc [here](https://docs.google.com/document/d/1yUGz2PbOh3fjdLhYSwa_1hJL84e3LhVbjQWugKaUfLw/edit?usp=sharing).


## Considered and eventually accepted algorithms:
- Branch and Bound (B&B) - *REJECTED*
- Simulated Annealing (SA) - **ACCEPTED**
- Iterative Sorting (IS) (greedy-like) - **ACCEPTED**

In the end, a combination of the two was chosen.


## Results achieved on the inputs:
| Name of input file       | Average score (10 runs) |
|--------------------------|-------------------------|
| a_example.txt            | 21                      |
| b_read_on.txt            | 5822900                 |
| c_incunabula.txt         | 5561998                 |
| d_tough_choices.txt      | 5028530                 |
| e_so_many_books.txt      | 4890022                 |
| f_libraries_of_the_wrold | 5340296                 |
