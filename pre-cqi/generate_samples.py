#!/bin/env python3

import os
import os.path as path
import shutil

from src.piece import Piece, PieceWithMetadata

def generate_pieces(base_path: str):
    if path.exists(base_path) and path.isdir(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)

    pieces = PieceWithMetadata.create_pieces(1)

    piece_count = 0
    max_score = 0

    for i, data in enumerate(pieces):
        image_name = f"piece_{i}.png"
        count = data.count
        piece_value = data.piece.value
        
        print(f"Sample: {image_name}, pieces available: {count}, value: {piece_value}, shape:")
        print(data.piece.shape)
        
        piece_count += count
        max_score += piece_value * count

        img = data.piece.to_img(Piece.Orientation.UP, "#000FFF")
        with open(path.join(base_path, image_name), "wb") as f:
            img.save(f, "PNG")

    print(f"Generated {len(pieces)} samples, total pieces: {piece_count}, max score: {max_score}")

if __name__ == "__main__":
    generate_pieces("piece")
