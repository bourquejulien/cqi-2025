use base64::prelude::*;
use image::{GenericImageView, ImageReader, Rgba};
use serde::{Deserialize, Serialize};

use std::{
    collections::HashMap,
    fs::{self},
    io::Cursor,
};

use crate::{piece::Pieces, server::ResponsePiece};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum Orientation {
    UP,
    DOWN,
    LEFT,
    RIGHT,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Move {
    pub x: usize,
    pub y: usize,
    pub orientation: Orientation,
    pub piece_id: usize,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Case {
    Player,
    Opponent,
    New,
    #[default]
    Void,
}

#[derive(Debug, Clone)]
pub struct BlockusMap {
    pieces: Pieces,
    used_pieces: HashMap<usize, usize>,
    map: [[Case; 20]; 20],
    color: Rgba<u8>,
}

fn check_edge(map: &[[Case; 20]; 20], i: usize, j: usize, corner: &mut bool) -> bool {
    let borders = [[-1, 0], [1, 0], [0, -1], [0, 1]];
    let edges = [[-1, -1], [-1, 1], [1, -1], [1, 1]];

    for [dx, dy] in borders {
        let x = i as isize + dx;
        let y = j as isize + dy;
        if x < 0 || y < 0 || x > 19 || y > 19 {
            continue;
        }
        let x = x as usize;
        let y = y as usize;
        if map[x][y] == Case::Player {
            return false;
        }
    }

    for [dx, dy] in edges {
        let x = i as isize + dx;
        let y = j as isize + dy;
        if x < 0 || y < 0 || x > 19 || y > 19 {
            continue;
        }
        let x = x as usize;
        let y = y as usize;
        if map[x][y] == Case::Player {
            *corner = true;
        }
    }

    true
}

impl BlockusMap {
    pub fn new(color: &String, pieces: &Vec<ResponsePiece>) -> Self {
        let map = Default::default();
        let a = u8::from_str_radix(&color[1..3], 16).unwrap();
        let b = u8::from_str_radix(&color[3..5], 16).unwrap();
        let c = u8::from_str_radix(&color[5..7], 16).unwrap();
        let color = Rgba::from([a, b, c, 255]);
        let pieces = Pieces::new(pieces);
        let used_pieces = HashMap::new();
        BlockusMap {
            map,
            color,
            pieces,
            used_pieces,
        }
    }

    pub fn update(&mut self, board: &str) {
        let bytes = BASE64_STANDARD.decode(board).unwrap();
        fs::write("result.png", &bytes).unwrap();
        let img = ImageReader::new(Cursor::new(bytes))
            .with_guessed_format()
            .unwrap()
            .decode()
            .unwrap();
        let black: Rgba<u8> = [0, 0, 0, 255].into();
        let color = self.color;
        for (i, j, p) in img.pixels() {
            let case = if p == black {
                Case::Void
            } else if p == color {
                Case::Player
            } else {
                Case::Opponent
            };

            self.map[i as usize / 20][j as usize / 20] = case;
        }
    }

    pub fn check_move_validity(&self, next_move: &Move, need_side: bool) -> bool {
        let piece = self.pieces.get_piece(next_move.piece_id);

        if let Some(count) = self.used_pieces.get(&next_move.piece_id) {
            if *count >= piece.count {
                return false;
            }
        }

        let x = next_move.x;
        let y = next_move.y;

        let mut touch_edge = need_side;
        let mut touch_side = !need_side;

        for i in 0..piece.size {
            for j in 0..piece.size {
                let x = x + i;
                let y = y + j;
                if piece.grid[i][j] == Case::New {
                    if self.map[x][y] == Case::Opponent || self.map[x][y] == Case::Player {
                        return false;
                    }
                    if !check_edge(&self.map, x, y, &mut touch_edge) {
                        return false;
                    }
                    if x == self.map.len() - 1 || y == self.map.len() - 1 {
                        touch_side = true;
                    }
                }
            }
        }

        touch_edge && touch_side
    }

    pub fn try_position(&mut self) -> Option<Move> {
        for piece_id in self.pieces.get_order_priority() {
            let piece = self.pieces.get_piece(piece_id);
            for i in 0..20 - (piece.size - 1)  {
                for j in 0..20 - (piece.size - 1) {
                    // print!("{}, {}\n", i, j);

                    for orientation in [
                        Orientation::UP,
                        Orientation::RIGHT,
                        Orientation::DOWN,
                        Orientation::LEFT,
                    ] {
                        let next_move = Move {
                            x: i,
                            y: j,
                            orientation,
                            piece_id,
                        };
                        if self.check_move_validity(&next_move, self.used_pieces.is_empty()) {
                            *self.used_pieces.entry(next_move.piece_id).or_insert(0) += 1;
                            return Some(next_move);
                        };
                    }
                }
            }
        }
        None
    }
}
