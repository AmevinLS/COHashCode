#include <algorithm>
#include <iostream>
#include <fstream>
#include <queue>
#include <tuple>
#include <vector>
#include <numeric>

using namespace std;

typedef unsigned int uint;

struct Library {
  uint id;
  uint signup_time;
  uint books_per_day;
  vector<uint> books;
  vector<uint> score;
  double score_per_day;
};

struct Node {
  uint library_id;
  uint signup_days;
  vector<uint> scanned_books;
  uint score;
  uint upper_bound;
};

int calculate_upper_bound(Node node, vector<Library> libraries, uint total_days) {
  // Sort libraries in decreasing order of score per day
  sort(libraries.begin(), libraries.end(),
       [](const Library& a, const Library& b) {
         return a.score_per_day > b.score_per_day;
       });

  // Initialize upper bound to the current score
  uint upper_bound = node.score;

  // For each library
  for (const auto& library : libraries) {
    // Calculate maximum number of days that can be spent on scanning books from this library
    uint max_days = (total_days - node.signup_days - library.signup_time) * library.books_per_day;
    // Calculate maximum number of books that can be scanned from this library
    uint max_books = min((uint)library.books.size(), max_days);
    // Add the scores of the maximum number of books to the upper bound
    upper_bound += accumulate(library.books.begin(), library.books.begin() + max_books, 0,
                              [&](uint a, uint b) { return a + library.score[b]; });
  }

  return upper_bound;
}

vector<Node> generate_children(Node node, vector<Library> libraries, uint total_days) {
  vector<Node> children;
  // For each remaining library
  for (uint i = 0; i < libraries.size(); ++i) {
    // Skip libraries that have already been signed up
    if (node.library_id == i) continue;

    // Create a child node by signing up the current library
    Node child;
    child.library_id = i;
    child.signup_days = node.signup_days + libraries[i].signup_time;
    child.scanned_books = node.scanned_books;
    child.score = node.score;
    child.upper_bound = calculate_upper_bound(child, libraries, total_days);
    // Add the child node to the list of children
    children.push_back(child);
  }
  return children;
}

int main() {
  ifstream fin("../resources/a_example.txt");


  uint B, L, D;
  fin >> B >> L >> D;
  vector<uint> score(B);
  for (uint i = 0; i < B; ++i) fin >> score[i];
  vector<Library> libraries(L);
  for (uint i = 0; i < L; ++i) {
    uint N, T, M;
    fin >> N >> T >> M;
    libraries[i].id = i;
    libraries[i].signup_time = T;
    libraries[i].books_per_day = M;
    libraries[i].books.resize(N);
    libraries[i].score.resize(N);
    for (uint j = 0; j < N; ++j) {
      fin >> libraries[i].books[j];
      libraries[i].score[j] = score[libraries[i].books[j]];
    }
    libraries[i].score_per_day =
        (double)accumulate(libraries[i].score.begin(), libraries[i].score.end(), 0) / T;
  }

  // Initialize search tree with a root node
  Node root;
  root.library_id = -1;
  root.signup_days = 0;
  root.scanned_books.clear();
  root.score = 0;
  root.upper_bound = calculate_upper_bound(root, libraries, D);

  // Initialize maximum score and corresponding library selection
  uint max_score = 0;
  vector<pair<uint, vector<uint>>> selection;

  // Perform breadth-first search
  queue<Node> q;
  q.push(root);
  while (!q.empty()) {
    Node node = q.front();
    q.pop();

    // Update maximum score and library selection if necessary
    if (node.score > max_score) {
      max_score = node.score;
      selection.clear();
      selection.push_back({node.library_id, node.scanned_books});
    } else if (node.score == max_score) {
      selection.push_back({node.library_id, node.scanned_books});
    }

    // Generate children of the current node
    vector<Node> children = generate_children(node, libraries, D);
    // Add children to the queue if their upper bound is greater than the maximum score
    for (const auto& child : children) {
      if (child.upper_bound > max_score) q.push(child);
    }
  }

  // Print results
  cout << selection.size() << endl;
  for (const auto& [library_id, scanned_books] : selection) {
    cout << library_id << " " << scanned_books.size() << endl;
    for (uint book : scanned_books) cout << book << " ";
    cout << endl;
  }

  return 0;
}

