package data

import (
    "context"
    _ "embed"
    "encoding/json"
    "log"
    "sync"
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
    teams     []teamInfo
    stats     Stats
    scoreDB   *Database
    statsLock sync.RWMutex
}

func New(connectionString string, ctx context.Context) (*Data, error) {
    data := Data{teams: []teamInfo{}, stats: Stats{}, statsLock: sync.RWMutex{}}
    err := json.Unmarshal([]byte(teams), &data.teams)

    if err != nil {
        log.Fatalf("Error unmarshalling teams data: %v", err)
    }

    scoreDB, err := newDatabase(connectionString, ctx)
    if err != nil {
        return nil, err
    }
    data.scoreDB = scoreDB

    data.stats.TotalGames, err = scoreDB.totalGameCount(ctx)

    if err != nil {
        return nil, err
    }

    data.stats.EndTime, err = time.Parse(time.RFC3339, "2025-01-17T14:00:00Z")
    if err != nil {
        panic(err)
    }

    return &data, nil
}

func (d *Data) GetGame(id string, context context.Context) (*DbGame, error) {
    return d.scoreDB.getGame(id, context)
}

func (d *Data) GetStats() Stats {
    d.statsLock.RLock()
    defer d.statsLock.RUnlock()

    return d.stats
}

func (d *Data) ListGames(context context.Context, limit, page int) ([]*DbGame, error) {
    return d.scoreDB.getGamesWithPagination(context, limit, page)
}

func (d *Data) AddGame(game *DbGame, ctx context.Context) error {
    d.statsLock.Lock()
    d.stats.TotalGames++
    d.statsLock.Unlock()

    return d.scoreDB.addGame(game, ctx)
}

func (d *Data) GetTeamIds(isBot bool) []string {
    teamIds := make([]string, 0, len(d.teams))
    for i, team := range d.teams {
        if team.IsBot == isBot {
            teamIds = append(teamIds, d.teams[i].ID)
        }
    }
    return teamIds
}

func (d *Data) Close(ctx context.Context) {
    d.scoreDB.close(ctx)
}
