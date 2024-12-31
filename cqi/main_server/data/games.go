package data

import (
	"context"
	"cqiprog/data/database"
	_ "embed"
	"sync"

	"time"
)

type DbGame struct {
	Id         string    `json:"id"`
	StartTime  time.Time `json:"startTime"`
	EndTime    time.Time `json:"endTime"`
	Team1Id    string    `json:"team1Id"`
	Team2Id    string    `json:"team2Id"`
	WinnerId   *string   `json:"winnerId,omitempty"`
	IsError    bool      `json:"isError"`
	Team1Score float32   `json:"team1Score"`
	Team2Score float32   `json:"team2Score"`
	ErrorData  *string   `json:"errorData,omitempty"`
	GameData   *string   `json:"gameData,omitempty"`
}

type cache struct {
	mapping map[string]*DbGame
	list    []*DbGame
	lock    sync.RWMutex
}

type gamesDB struct {
	db    *database.Database
	cache *cache
	lock  sync.RWMutex

	totalGameCount int
}

func newGamesDB(db *database.Database, ctx context.Context) (*gamesDB, error) {
	games := gamesDB{
		db: db,
		cache: &cache{
			mapping: map[string]*DbGame{},
			list:    []*DbGame{},
			lock:    sync.RWMutex{},
		},
		lock: sync.RWMutex{},
	}

	totalGameCount, err := getTotalGameCount(db, ctx)

	if err != nil {
		return nil, err
	}

	games.totalGameCount = totalGameCount

	games.getGamesWithPagination(ctx, LIST_CACHE_SIZE, 0)

	return &games, nil
}

func getTotalGameCount(db *database.Database, ctx context.Context) (int, error) {
	conn, err := db.AcquireConnection(ctx)

	if err != nil {
		return 0, err
	}

	defer conn.Release()

	rows, err := conn.Query(ctx, "SELECT COUNT(*) FROM games")

	if err != nil {
		return 0, err
	}

	var count int
	if rows.Next() {
		err := rows.Scan(&count)
		if err != nil {
			return 0, err
		}
	}

	return count, nil
}

func (p *gamesDB) getGame(id string, ctx context.Context) (*DbGame, error) {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if game := p.cache.getGame(id); game != nil {
		return game, nil
	}

	conn, err := p.db.AcquireConnection(ctx)

	if err != nil {
		return nil, err
	}

	defer conn.Release()

	row := conn.QueryRow(ctx, "SELECT * FROM games WHERE id = $1", id)
	game := DbGame{}

	err = row.Scan(&game.Id, &game.StartTime, &game.EndTime, &game.Team1Id, &game.Team2Id, &game.WinnerId, &game.IsError, &game.Team1Score, &game.Team2Score, &game.ErrorData, &game.GameData)
	if err != nil {
		return nil, err
	}

	p.cache.addGame(&game)

	return &game, nil
}

func (p *gamesDB) getGamesWithPagination(ctx context.Context, limit int, page int) ([]*DbGame, error) {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if ok, list := p.cache.getGameList(limit, page); ok {
		return list, nil
	}

	conn, err := p.db.AcquireConnection(ctx)

	if err != nil {
		return nil, err
	}

	defer conn.Release()

	offset := page * limit
	rows, err := conn.Query(ctx, "SELECT id, start_time, end_time, team1_id, team2_id, winner_id, is_error, team1_score, team2_score FROM games ORDER BY end_time desc LIMIT $1 OFFSET $2", limit, offset)
	if err != nil {
		return nil, err
	}

	games := []*DbGame{}
	for rows.Next() {
		game := DbGame{}
		err := rows.Scan(&game.Id, &game.StartTime, &game.EndTime, &game.Team1Id, &game.Team2Id, &game.WinnerId, &game.IsError, &game.Team1Score, &game.Team2Score)
		if err != nil {
			return nil, err
		}

		games = append(games, &game)
	}

	p.cache.addGameList(games, offset)

	return games, nil
}

func (p *gamesDB) getGamesSince(ctx context.Context, since time.Time) ([]*DbGame, error) {
	p.lock.RLock()
	defer p.lock.RUnlock()

	return p.cache.getGamesSince(since), nil
}

func (p *gamesDB) addGame(game *DbGame, ctx context.Context) error {
	p.lock.Lock()
	defer p.lock.Unlock()

	conn, err := p.db.AcquireConnection(ctx)

	if err != nil {
		return err
	}

	defer conn.Release()

	_, err = conn.Exec(ctx, "INSERT INTO games (id, start_time, end_time, team1_id, team2_id, winner_id, is_error, team1_score, team2_score, error_data, game_data) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
		game.Id, game.StartTime, game.EndTime, game.Team1Id, game.Team2Id, game.WinnerId, game.IsError, game.Team1Score, game.Team2Score, game.ErrorData, game.GameData)
	if err != nil {
		return err
	}

	p.cache.addGame(game)
	p.totalGameCount++

	return nil
}
