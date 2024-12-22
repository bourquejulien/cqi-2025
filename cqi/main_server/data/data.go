package data

import (
	"context"
	_ "embed"
	"encoding/json"
	"log"
	"time"
)

//go:embed init_data/teams.json
var teams string

type teamInfo struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	IsBot bool   `json:"isBot"`
}

type Stats struct {
	TotalGames int
	EndTime    time.Time
}

type Data struct {
	db          *Database
	settings    *settings
	gamesDB     *gamesDB
	stopDeamon  *context.CancelFunc
	rankingInfo *RankingInfo

	teams []*teamInfo
}

func New(connectionString string, ctx context.Context) (*Data, error) {
	data := Data{teams: []*teamInfo{}}
	err := json.Unmarshal([]byte(teams), &data.teams)

	if err != nil {
		log.Fatalf("Error unmarshalling teams data: %v", err)
	}

	db, err := newDatabase(connectionString, ctx)
	if err != nil {
		return nil, err
	}
	data.db = db

	data.gamesDB, err = newGamesDB(db, ctx)

	if err != nil {
		return nil, err
	}

	data.settings, err = newSettings(db, ctx)
	if err != nil {
		return nil, err
	}

	ctx, cancel := context.WithCancel(context.Background())
	data.stopDeamon = &cancel
	data.startDeamon(ctx)

	return &data, nil
}

func (d *Data) GetGame(id string, context context.Context) (*DbGame, error) {
	return d.gamesDB.getGame(id, context)
}

func (d *Data) GetStats() *Stats {
	return &Stats{d.gamesDB.totalGameCount, d.settings.EndTime()}
}

func (d *Data) IsExpired() bool {
	return time.Now().After(d.settings.EndTime())
}

func (d *Data) ListGames(context context.Context, limit, page int) ([]*DbGame, error) {
	return d.gamesDB.getGamesWithPagination(context, limit, page)
}

func (d *Data) AddGame(game *DbGame, ctx context.Context) error {
	return d.gamesDB.addGame(game, ctx)
}

func (d *Data) GetTeamIds(isBot bool) []string {
	teamIds := make([]string, 0, len(d.teams))
	for _, team := range d.teams {
		if team.IsBot == isBot {
			teamIds = append(teamIds, team.ID)
		}
	}
	return teamIds
}

func (d *Data) GetTeamMapping() map[string]string {
	teamIds := make(map[string]string)
	for _, team := range d.teams {
		teamIds[team.ID] = team.Name
	}
	return teamIds
}

func (d *Data) SetEndTime(endTime time.Time, ctx context.Context) error {
	return d.settings.SetEndTime(endTime, ctx)
}

func (d *Data) Close(ctx context.Context) {
	d.db.close()
	(*d.stopDeamon)()
}
