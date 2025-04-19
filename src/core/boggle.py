# src/core/boggle.py
import math
import random
import bisect
from typing import List, Dict, Optional, TextIO
from src.utils.utils import open_data

# ______________________________________________________________________________
# Inverse Boggle: Search for a high-scoring Boggle board. A good domain for
# iterative-repair and related search techniques, as suggested by Justin Boyan.

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
cubes16 = ['FORIXB', 'MOQABJ', 'GURILW', 'SETUPL',
           'CMPDAE', 'ACITAO', 'SLCRAE', 'ROMASH',
           'NODESW', 'HEFIYE', 'ONUDTK', 'TEVIGN',
           'ANEDVZ', 'PINESH', 'ABILYT', 'GKYLEU']

boyan_best = list('RSTCSDEIAEGNLRPEATESMSSID')


def random_boggle(n: int = 4) -> List[str]:
    """Return a random Boggle board of size n x n.
    We represent a board as a linear list of letters.

    Args:
        n: Size of the board (n x n).

    Returns:
        List of letters representing the board.
    """
    cubes = [cubes16[i % 16] for i in range(n * n)]
    random.shuffle(cubes)
    return list(map(random.choice, cubes))


def print_boggle(board: List[str]) -> None:
    """Print the board in a 2D array format.

    Args:
        board: List of letters representing the Boggle board.
    """
    n2 = len(board)
    n = exact_sqrt(n2)
    for i in range(n2):
        if i % n == 0 and i > 0:
            print()
        if board[i] == 'Q':
            print('Qu', end=' ')
        else:
            print(str(board[i]) + ' ', end=' ')
    print()


def boggle_neighbors(n2: int, cache: Optional[Dict[int, List[List[int]]]] = None) -> List[List[int]]:
    """Return a list of lists, where the i-th element is the list of indexes
    for the neighbors of square i. Neighbors are ordered as: up-left, up, up-right,
    left, right, down-left, down, down-right (where applicable).

    Args:
        n2: Number of squares in the board (n * n).
        cache: Optional cache to store previously computed neighbors.

    Returns:
        List of lists, where each inner list contains neighbor indices for square i.
    """
    if cache is None:
        cache = {}
    if n2 in cache:
        return cache[n2]

    n = exact_sqrt(n2)
    neighbors: List[List[int]] = [[] for _ in range(n2)]

    for i in range(n2):
        on_top = i < n
        on_bottom = i >= n2 - n
        on_left = i % n == 0
        on_right = (i + 1) % n == 0

        # Order: up-left, up, up-right, left, right, down-left, down, down-right
        if not on_top and not on_left:
            neighbors[i].append(i - n - 1)  # Up-left
        if not on_top:
            neighbors[i].append(i - n)  # Up
        if not on_top and not on_right:
            neighbors[i].append(i - n + 1)  # Up-right
        if not on_left:
            neighbors[i].append(i - 1)  # Left
        if not on_right:
            neighbors[i].append(i + 1)  # Right
        if not on_bottom and not on_left:
            neighbors[i].append(i + n - 1)  # Down-left
        if not on_bottom:
            neighbors[i].append(i + n)  # Down
        if not on_bottom and not on_right:
            neighbors[i].append(i + n + 1)  # Down-right

    cache[n2] = neighbors
    return neighbors

def exact_sqrt(n2: int) -> int:
    """If n2 is a perfect square, return its square root, else raise error.

    Args:
        n2: Number to compute square root of.

    Returns:
        Integer square root of n2.

    Raises:
        AssertionError: If n2 is not a perfect square.
    """
    n = int(math.sqrt(n2))
    assert n * n == n2, f"{n2} is not a perfect square"
    return n


class Wordlist:
    """This class holds a list of words. You can use (word in wordlist)
    to check if a word is in the list, or wordlist.lookup(prefix)
    to see if prefix starts any of the words in the list.
    """

    def __init__(self, file: TextIO, min_len: int = 3):
        """Initialize with a file containing words.

        Args:
            file: File object containing words (one per line).
            min_len: Minimum length of words to include.
        """
        lines = file.read().upper().split()
        self.words: List[str] = [word for word in lines if len(word) >= min_len]
        self.words.sort()
        self.bounds: Dict[str, tuple[int, int]] = {}
        for c in ALPHABET:
            c2 = chr(ord(c) + 1)
            self.bounds[c] = (bisect.bisect(self.words, c),
                              bisect.bisect(self.words, c2))

    def lookup(self, prefix: str, lo: int = 0, hi: Optional[int] = None) -> tuple[Optional[int], bool]:
        """See if prefix is in dictionary, as a full word or as a prefix.

        Args:
            prefix: Prefix or word to look up.
            lo: Lower bound for binary search.
            hi: Upper bound for binary search (optional).

        Returns:
            Tuple of (index, is_word), where index is the lowest i such that
            words[i].startswith(prefix) or None, and is_word is True if prefix
            is a full word in the list.
        """
        words = self.words
        if hi is None:
            hi = len(words)
        i = bisect.bisect_left(words, prefix, lo, hi)
        if i < len(words) and words[i].startswith(prefix):
            return i, (words[i] == prefix)
        return None, False

    def __contains__(self, word: str) -> bool:
        return self.lookup(word)[1]

    def __len__(self) -> int:
        return len(self.words)


class BoggleFinder:
    """A class that allows you to find all the words in a Boggle board."""

    wordlist: Optional[Wordlist] = None  # A class variable, holding a wordlist

    def __init__(self, board: Optional[List[str]] = None):
        """Initialize the Boggle finder.

        Args:
            board: Optional Boggle board (list of letters).
        """
        self.board: Optional[List[str]] = None
        self.neighbors: Optional[List[List[int]]] = None
        if BoggleFinder.wordlist is None:
            BoggleFinder.wordlist = Wordlist(open_data("EN-text/wordlist.txt"))
        self.found: Dict[str, bool] = {}
        if board:
            self.set_board(board)

    def set_board(self, board: Optional[List[str]] = None) -> 'BoggleFinder':
        """Set the board, and find all the words in it.

        Args:
            board: Optional Boggle board (list of letters).

        Returns:
            Self, for method chaining.
        """
        if board is None:
            board = random_boggle()
        self.board = board
        self.neighbors = boggle_neighbors(len(board))
        self.found = {}
        for i in range(len(board)):
            lo, hi = self.wordlist.bounds[board[i]]
            self.find(lo, hi, i, [], '')
        return self

    def find(self, lo: int, hi: int, i: int, visited: List[int], prefix: str) -> None:
        """Looking in square i, find the words that continue the prefix,
        considering the entries in self.wordlist.words[lo:hi], and not
        revisiting the squares in visited.

        Args:
            lo: Lower bound for wordlist search.
            hi: Upper bound for wordlist search.
            i: Current square index.
            visited: List of visited square indices.
            prefix: Current word prefix.
        """
        if i in visited:
            return
        wordpos, is_word = self.wordlist.lookup(prefix, lo, hi)
        if wordpos is not None:
            if is_word:
                self.found[prefix] = True
            visited.append(i)
            c = self.board[i]
            if c == 'Q':
                c = 'QU'
            prefix += c
            for j in self.neighbors[i]:
                self.find(wordpos, hi, j, visited, prefix)
            visited.pop()

    def words(self) -> List[str]:
        """Return the words found."""
        return list(self.found.keys())

    scores = [0, 0, 0, 0, 1, 2, 3, 5] + [11] * 100

    def score(self) -> int:
        """Return the total score for the words found, according to the rules."""
        return sum(self.scores[len(w)] for w in self.words())

    def __len__(self) -> int:
        """Return the number of words found."""
        return len(self.found)


def boggle_hill_climbing(board: Optional[List[str]] = None, ntimes: int = 100, verbose: bool = True) -> tuple[
    List[str], int]:
    """Solve inverse Boggle by hill-climbing: find a high-scoring board by
    starting with a random one and changing it.

    Args:
        board: Optional starting board.
        ntimes: Number of iterations to attempt.
        verbose: Whether to print progress.

    Returns:
        Tuple of (best board, best score).
    """
    finder = BoggleFinder()
    if board is None:
        board = random_boggle()
    best = len(finder.set_board(board))
    for _ in range(ntimes):
        i, oldc = mutate_boggle(board)
        new = len(finder.set_board(board))
        if new > best:
            best = new
            if verbose:
                print(best, _, board)
        else:
            board[i] = oldc  # Change back
    if verbose:
        print_boggle(board)
    return board, best


def mutate_boggle(board: List[str]) -> tuple[int, str]:
    """Mutate the board by changing one letter.

    Args:
        board: Boggle board to mutate.

    Returns:
        Tuple of (index changed, old letter).
    """
    i = random.randrange(len(board))
    oldc = board[i]
    board[i] = random.choice(random.choice(cubes16))
    return i, oldc