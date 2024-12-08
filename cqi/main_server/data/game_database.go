package data

import (
	"context"
	_ "embed"
	"sort"
	"sync"

	"time"

	"github.com/jackc/pgx/v5"
)

const (
	LIST_CACHE_SIZE = 1000
)

type DbGame struct {
	Id         string    `json:"id"`
	StartTime  time.Time `json:"start_time"`
	EndTime    time.Time `json:"end_time"`
	Team1Id    string    `json:"team1_id"`
	Team2Id    string    `json:"team2_id"`
	WinnerId   *string   `json:"winner_id,omitempty"`
	IsError    bool      `json:"is_error"`
	Team1Score float32   `json:"team1_score"`
	Team2Score float32   `json:"team2_score"`
	ErrorData  *string   `json:"error_data,omitempty"`
	GameData   *string   `json:"game_data,omitempty"`
}

type cache struct {
	mapping map[string]*DbGame
	list    []*DbGame
	lock    sync.RWMutex
}

type Database struct {
	conn  *pgx.Conn
	lock  sync.RWMutex
	cache cache
}

//go:embed init_data/init.sql
var initSQL string

func newDatabase(connectionString string, ctx context.Context) (*Database, error) {
	conn, err := pgx.Connect(ctx, connectionString)
	if err != nil {
		return nil, err
	}

	_, err = conn.Exec(ctx, initSQL)
	if err != nil {
		return nil, err
	}

	return &Database{conn, sync.RWMutex{}, cache{mapping: make(map[string]*DbGame)}}, nil
}

func (p *Database) totalGameCount(ctx context.Context) (int, error) {
	p.lock.RLock()
	defer p.lock.RUnlock()

	rows, err := p.conn.Query(ctx, "SELECT COUNT(*) FROM games")

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

func (p *Database) getGame(id string, ctx context.Context) (*DbGame, error) {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if game := p.cache.getGame(id); game != nil {
		return game, nil
	}

	row := p.conn.QueryRow(ctx, "SELECT id, start_time, end_time, team1_id, team2_id, winner_id, is_error, team1_score, team2_score FROM games WHERE id = $1", id)

	game := DbGame{}
	err := row.Scan(&game.Id, &game.StartTime, &game.EndTime, &game.Team1Id, &game.Team2Id, &game.WinnerId, &game.IsError, &game.Team1Score, &game.Team2Score)
	if err != nil {
		return nil, err
	}

	p.cache.addGame(&game)

	return &game, nil
}

func (p *Database) getGamesWithPagination(ctx context.Context, limit int, page int) ([]*DbGame, error) {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if ok, list := p.cache.getGameList(limit, page); ok {
		return list, nil
	}

	rows, err := p.conn.Query(ctx, "SELECT id, start_time, end_time, team1_id, team2_id, winner_id, is_error, team1_score, team2_score FROM games ORDER BY start_time desc LIMIT $1 OFFSET $2", limit, page)
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

	p.cache.addGameList(games)

	return games, nil
}

func (p *Database) addGame(game *DbGame, ctx context.Context) error {
	p.lock.Lock()
	defer p.lock.Unlock()

	_, err := p.conn.Exec(ctx, "INSERT INTO games (id, start_time, end_time, team1_id, team2_id, winner_id, is_error, team1_score, team2_score, error_data, game_data) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
		game.Id, game.StartTime, game.EndTime, game.Team1Id, game.Team2Id, game.WinnerId, game.IsError, game.Team1Score, game.Team2Score, game.ErrorData, game.GameData)
	if err != nil {
		return err
	}

	p.cache.addGame(game)

	return nil
}

func (p *Database) close(ctx context.Context) {
	p.conn.Close(ctx)
}

func (p *cache) getGameList(limit, page int) (bool, []*DbGame) {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if len(p.list) >= limit*(page+1) {
		return true, p.list[limit*page : limit*page+limit]
	}

	return false, nil
}

func (p *cache) getGame(id string) *DbGame {
	p.lock.RLock()
	defer p.lock.RUnlock()

	if game, ok := p.mapping[id]; ok {
		return game
	}

	return nil
}

func (p *cache) addGame(game *DbGame) {
	p.lock.Lock()
	defer p.lock.Unlock()

	p.mapping[game.Id] = game
	p.list = append(p.list, game)

	sort.Slice(p.list, func(i, j int) bool {
		return p.list[i].StartTime.After(p.list[j].StartTime)
	})
}

func (p *cache) addGameList(games []*DbGame) {
	p.lock.Lock()
	defer p.lock.Unlock()

	if len(p.list) >= LIST_CACHE_SIZE || len(games) < len(p.list) {
		return
	}

	p.list = games
}
