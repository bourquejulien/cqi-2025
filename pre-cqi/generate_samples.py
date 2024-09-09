#!/bin/env python3

import os.path as path
from src.piece import Piece

def generate_pieces(base_path: str):
    pieces = Piece.create_pieces(1)

    for i, (piece, _) in enumerate(pieces):
        img = piece.to_img(Piece.Orientation.UP, "#000FFF")

        image_name = f"piece_{i}.png"
        with open(path.join(base_path, image_name), "wb") as f:
            img.save(f, "PNG")

if __name__ == "__main__":
    generate_pieces("piece")
