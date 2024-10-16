use crate::map::Case;
use crate::server::ResponsePiece;

#[derive(Debug, Clone)]
pub struct Pieces {
    pub pieces: Vec<Piece>,
}

fn grid_from_shape(shape: &Vec<Vec<u32>>) -> Grid {
    shape
        .iter()
        .map(|x| {
            x.iter()
                .map(|y| if *y == 0 { Case::Void } else { Case::New })
                .collect::<Vec<Case>>()
        })
        .collect::<Grid>()
}

impl Pieces {
    pub fn new(response_pieces: &Vec<ResponsePiece>) -> Self {
        let pieces = response_pieces
            .iter()
            .map(|x| Piece {
                size: x.shape.len(),
                count: usize::try_from(x.count).unwrap(),
                grid: grid_from_shape(&x.shape),
            })
            .collect::<Vec<Piece>>();
        Self { pieces }
    }
    pub fn get_piece(&self, piece_id: usize) -> &Piece {
        &self.pieces[piece_id]
    }
    pub fn get_order_priority(&self) -> Vec<usize> {
        let mut pieces: Vec<_> = self
            .pieces
            .iter()
            .enumerate()
            .map(|p| {
                (
                    p.0,
                    p.1.grid
                        .iter()
                        .flatten()
                        .filter(|p| **p == Case::New)
                        .count(),
                    p.1.size,
                )
            })
            .collect();
        pieces.sort_unstable_by(|a, b| (b.1.cmp(&a.1).then(b.2.cmp(&a.2))));
        pieces.iter().map(|(i, _, _)| *i).collect()
    }
}

type Grid = Vec<Vec<Case>>;

#[derive(Clone, Debug)]
pub struct Piece {
    pub size: usize,
    pub count: usize,
    pub grid: Vec<Vec<Case>>,
}
