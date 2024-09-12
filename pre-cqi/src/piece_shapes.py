import numpy as np

# ID of the piece is the index of the shape in the list
PIECE_SHAPES = [
    {
        "piece": np.array(
            [[1]]
        ),
        "count": 3
    },
    {
        "piece": np.array(
            [[1, 0],
             [1, 0]]
        ),
        "count": 3
    },
    {
        "piece": np.array(
            [[1, 0],
             [1, 1]]
        ),
        "count": 2
    },
    {
        "piece": np.array(
            [[1, 0, 0],
             [1, 0, 0],
             [1, 0, 0]]
        ),
        "count": 2
    },
    {
        "piece": np.array(
            [[0, 1, 0],
             [0, 1, 0],
             [1, 1, 0]]
        ),
        "count": 2
    },
    {
        "piece": np.array(
            [[1, 0, 0],
             [1, 1, 0],
             [1, 0, 0]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[1, 1, 1, 1],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[1, 1],
             [1, 1]]
        ),
        "count": 2
    },
    {
        "piece": np.array(
            [[1, 1, 0],
             [0, 1, 1],
             [0, 0, 0]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[1, 0, 0, 0, 0],
             [1, 0, 0, 0, 0],
             [1, 0, 0, 0, 0],
             [1, 0, 0, 0, 0],
             [1, 0, 0, 0, 0]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[0, 1, 0],
             [1, 1, 0],
             [1, 1, 0]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[1, 1, 0],
             [0, 1, 0],
             [1, 1, 0]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[0, 1, 0],
             [0, 1, 0],
             [1, 1, 1]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[1, 0, 0],
             [1, 0, 0],
             [1, 1, 1]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[1, 0, 0],
             [1, 1, 1],
             [0, 0, 1]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[1, 0, 0],
             [1, 1, 1],
             [0, 1, 0]]
        ),
        "count": 1
    },
    {
        "piece": np.array(
            [[0, 1, 0],
             [1, 1, 1],
             [0, 1, 0]]
        ),
        "count": 1
    },
]
