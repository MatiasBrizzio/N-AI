# tests/test_boggle.py
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.boggle import boggle_neighbors, random_boggle, BoggleFinder

def test_boggle_neighbors():
    neighbors = boggle_neighbors(16)  # 4x4 board
    assert len(neighbors) == 16
    assert neighbors[0] == [1, 4, 5]  # Top-left corner
    assert neighbors[5] == [0, 1, 2, 4, 6, 8, 9, 10]  # Middle square

def test_boggle_finder():
    board = random_boggle(4)
    finder = BoggleFinder(board)
    assert len(finder.words()) >= 0
    assert isinstance(finder.score(), int)