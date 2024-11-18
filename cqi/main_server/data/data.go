package data

import (
	"context"
	_ "embed"
	"encoding/json"
	"log"
)

//go:embed init_data/teams.json
var teams string

type teamInfo struct {
	id   int    `json:"id"`
	name string `json:"name"`
}

type Team struct {
	teamInfo teamInfo
}

type Data struct {
	teams   []teamInfo
	scoreDB *Database
}

func New(connectionString string) (*Data, error) {
	data := Data{teams: []teamInfo{}}
	err := json.Unmarshal([]byte(teams), &data.teams)
	if err != nil {
		log.Fatalf("Error unmarshalling teams data: %v", err)
	}

	scoreDB, err := newDatabase(connectionString, context.Background())
	if err != nil {
		return nil, err
	}
	data.scoreDB = scoreDB

	return &data, nil
}

func (d *Data) GetGame(id string, context context.Context) (*DbGame, error) {
	return d.scoreDB.getGame(id, context)
}

func (d *Data) ListGames(context context.Context, limit, page int) ([]*DbGame, error) {
	return d.scoreDB.getGamesWithPagination(context, limit, page)
}

func (d *Data) AddGame(game *DbGame, ctx context.Context) error {
	return d.scoreDB.addGame(game, ctx)
}

func (d *Data) GetTeamIds() []string {
	teamIds := make([]string, len(d.teams))
	for i, team := range d.teams {
		teamIds[i] = team.name
	}
	return teamIds
}

func (d *Data) Close(ctx context.Context) {
	d.scoreDB.close(ctx)
}
