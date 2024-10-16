use serde::{Deserialize, Serialize};

use crate::map::{BlockusMap, Move};

const START_GAME_PATH: &str = "/start_game";
const SEND_MOVE_PATH: &str = "/send_move";
const END_GAME_PATH: &str = "/end_game";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResponsePiece {
    pub id: u32,
    pub count: u32,
    pub shape: Vec<Vec<u32>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NewResponse {
    pub board: String,
    pub color: String,
    pub pieces: Vec<ResponsePiece>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct GameResponse {
    pub game_over: bool,
    pub score: f64,
    pub board: String,
}

pub struct Server {
    base_address: String,
    request: reqwest::blocking::Client,
}

impl Server {
    pub fn new(base_address: String) -> Server {
        let request = reqwest::blocking::Client::new();
        Server {
            base_address: format!("http://{}", base_address),
            request,
        }
    }

    pub fn start_game(&self) -> BlockusMap {
        let req = self
            .request
            .post(self.base_address.clone() + START_GAME_PATH)
            .send()
            .unwrap()
            .text()
            .unwrap();
        let rep: NewResponse = serde_json::from_str(&req).unwrap();
        let mut blockus = BlockusMap::new(&rep.color, &rep.pieces);
        blockus.update(&rep.board);
        blockus
    }

    pub fn send_move(&self, next_move: Move, map: &mut BlockusMap) -> bool {
        let req = self
            .request
            .post(self.base_address.clone() + SEND_MOVE_PATH)
            .json(&next_move)
            .send()
            .unwrap()
            .text()
            .unwrap();
        if req == "The game is over" {
            println!("The game is over!");
            return true;
        }
        let rep: GameResponse = serde_json::from_str(&req).unwrap();
        map.update(&rep.board);
        if rep.game_over {
            println!("Game over!");
            println!("Score: {:?}", rep.score);
            return true;
        }
        false
    }

    pub fn end_game(&self) -> Option<GameResponse> {
        let req = self
            .request
            .post(self.base_address.clone() + END_GAME_PATH)
            .send()
            .unwrap()
            .text()
            .unwrap();
        if &req == "No game currently running" || &req == "The game is already over" {
            Default::default()
        } else {
            serde_json::from_str(&req).unwrap()
        }
    }
}
