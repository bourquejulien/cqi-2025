use server::Server;

pub mod map;
pub mod piece;
pub mod server;

fn main() {
    let server = Server::new(std::env::args().nth(1).unwrap_or("localhost:5000".to_string()));
    server.end_game();
    let mut board = server.start_game();

    while let Some(next_move) = board.try_position() {
        println!("{:?}", next_move);
        if server.send_move(next_move, &mut board) {
            break;
        };
    }

    if let Some(response) = server.end_game() {
        println!("Unable to play, final score: {:?}", response.score);
    }
}
