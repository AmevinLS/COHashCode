#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <stack>
#include <set>
#include <map>
#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <numeric>

using namespace std;

typedef unsigned int uint;

class LibraryProblem;
class Node;

class LibraryProblem {
public:
    uint num_days;
    uint num_books;
    uint num_libs;
    uint* signup_times;
    uint* scan_speeds;
    uint** libraries;
    uint* lib_sizes;
    uint* scores;

    LibraryProblem(string path) {
        readFromFile(path);
    }

    void readFromFile(string path) {
        ifstream fin(path);
        uint B, L, D;
        fin >> B >> L >> D;
        uint* n = new uint[L];
        uint* t = new uint[L];
        uint* m = new uint[L];
        uint** libs = new uint*[L];

        uint* s = new uint[B];
        for(int i=0; i<B; i++) {
            fin >> s[i];
        }

        for(uint lib=0; lib<L; lib++) {
            fin >> n[lib] >> t[lib] >> m[lib];
            uint* books = new uint[n[lib]];
            for(int i=0; i<n[lib]; i++) {
                fin >> books[i];
            }
            libs[lib] = books;
        }

        num_books = B;
        num_libs = L;
        num_days = D;
        signup_times = t;
        scan_speeds = m;
        libraries = libs;
        scores = s;
        lib_sizes = n;
    }
};

class GreedyProblem : public LibraryProblem {
public:
    GreedyProblem(string path)
        : LibraryProblem(path) 
    {
    
    }

    void remove_books(vector<uint> books) {
        for (auto book : books) {
            scores[book] = 0;
        }
    }

    uint select_lib(unordered_set<uint> libs, uint days_left) {
        uint sel_lib = 0;
        double max_score = 0;
        for (auto lib : libs) {
            double score;
            uint scans_left = (days_left - signup_times[lib]) * scan_speeds[lib];
            vector<uint> books_sorted(libraries[lib], libraries[lib] + lib_sizes[lib]);
            sort(
                books_sorted.begin(), books_sorted.end(),
                [&](uint a, uint b) { return scores[a] > scores[b]; }
            );
            uint total_score = 0;
            for (uint i = 0; i < scans_left && i < lib_sizes[lib]; i++) {
                total_score += scores[books_sorted[i]];
            }
            score = (double)total_score / scan_speeds[lib];
            if (score > max_score) {
                max_score = score;
                sel_lib = lib;
            }
        }
        return sel_lib;
    }

    uint greedy() {
        uint TOTAL_SCORE = 0;
        
        uint days_left = num_days;
        vector<uint> lib_order;
        unordered_map<uint, vector<uint>> lib_books_scanned;
        unordered_set<uint> libs_left(num_libs);
        for(uint lib=0; lib<num_libs; lib++) {
            libs_left.insert(lib);
        }
        while (days_left > 0) {
            if (libs_left.empty())
                break;

            uint curr_lib = select_lib(libs_left, days_left);
            // score, chosen_books = evaluate_lib(curr_lib, days_left)
            
            uint scans_left = (days_left - signup_times[curr_lib]) * scan_speeds[curr_lib];
            vector<uint> books_sorted(libraries[curr_lib], libraries[curr_lib] + lib_sizes[curr_lib]);
            sort(
                books_sorted.begin(), books_sorted.end(),
                [&](uint a, uint b) { return scores[a] > scores[b]; }
            );
            
            vector<uint> chosen_books;
            for (uint i = 0; i < scans_left && i < lib_sizes[curr_lib]; i++) {
                TOTAL_SCORE += scores[books_sorted[i]];
                chosen_books.push_back(books_sorted[i]);
            }


            lib_order.push_back(curr_lib);
            lib_books_scanned[curr_lib] = chosen_books;
            remove_books(chosen_books);
            libs_left.erase(curr_lib);
            days_left -= signup_times[curr_lib];
        }
        return TOTAL_SCORE;
    }
};


class Node {
    uint library_id;
    uint signup_days;
    unordered_set<uint> scanned_books;
    uint score;
    uint upper_bound;
};

class BBProblem : public LibraryProblem {

    // int calculate_upper_bound(Node node, vector<Library> libraries, int total_days) {
    //     // Sort libraries in decreasing order of score per day
    //     sort(libraries.begin(), libraries.end(),
    //         [](const Library& a, const Library& b) {
    //             return a.score_per_day > b.score_per_day;
    //         });

    //     // Initialize upper bound to the current score
    //     int upper_bound = node.score;

    //     // For each library
    //     for (const auto& library : libraries) {
    //         // Calculate maximum number of days that can be spent on scanning books from this library
    //         int max_days = (total_days - node.signup_days - library.signup_time) * library.books_per_day;
    //         // Calculate maximum number of books that can be scanned from this library
    //         int max_books = min(library.books.size(), max_days);
    //         // Add the scores of the maximum number of books to the upper bound
    //         upper_bound += accumulate(library.books.begin(), library.books.begin() + max_books, 0,
    //                                 [](int a, int b) { return a + library.score[b]; });
    //     }

    //     return upper_bound;
    // }

};

// class Node {
// public:
//     vector<Node*> get_children(BBProblem problem) {
//         return vector<Node*>();
//     }
// };


// Node* branchAndBound(BBProblem problem) {
//     int problem_lower_bound = -1;
//     stack<Node*> candidate_stack = stack<Node*>();
//     Node* current_optimum = nullptr;
//     problem.populate_stack_with_candidates(candidate_stack);

//     while (!candidate_stack.empty()) {
//         Node* node = candidate_stack.top();
//         candidate_stack.pop();
//         if (problem.is_single_candidate(node)) {
//             if (problem.objective_func(node) > problem_lower_bound) {
//                 current_optimum = node;
//                 problem_lower_bound = problem.objective_func(node);
//             }
//         }
//         else {
//             for (Node* child_node : node->get_children(problem)) {
//                 if (problem.upper_bound_func(child_node) >= problem_lower_bound)
//                     candidate_stack.push(child_node);
//             }
//         }
//     }
//     return current_optimum;
// } 


int main()
{
    GreedyProblem problem("../resources/f_libraries_of_the_world.txt");
    cout << problem.greedy() << endl;
    return 0;
}