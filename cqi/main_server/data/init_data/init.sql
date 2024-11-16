CREATE TABLE IF NOT EXISTS games (
  id TEXT PRIMARY KEY,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  team1_id VARCHAR(100),
  team2_id VARCHAR(100),
  winner_id VARCHAR(100),
  is_error BOOLEAN,
  error_data VARCHAR(100),
  team1_score REAL,
  team2_score REAL,
  game_data TEXT
);
