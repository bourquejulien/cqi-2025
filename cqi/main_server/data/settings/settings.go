package settings

import (
	"context"
	"cqiprog/data/database"
	_ "embed"
	"encoding/json"
	"sync"

	"time"
)

const (
	DEFAULT_SETTINGS = `{
		"endTime": "2025-01-17T13:00:00Z",
		"rankingPeriod": "30m",
		"maxConcurrentMatch": "10",
		"maxMatchPerRunner": "1",
		"matchTimeout": "5m"
	}`
)

type SettingsEntries struct {
	EndTime            *time.Time    `json:"endTime,omitempty"`
	RankingPeriod      time.Duration `json:"rankingPeriod,omitempty"`
	MaxConcurrentMatch int           `json:"maxConcurrentMatch,omitempty"`
	MaxMatchPerRunner  int           `json:"maxMatchPerRunner,omitempty"`
	MatchTimeout       time.Duration `json:"matchTimeout,omitempty"`
}

func (s *SettingsEntries) MarshalJSON() ([]byte, error) {
	return json.Marshal(&struct {
		EndTime            string `json:"endTime,omitempty"`
		RankingPeriod      string `json:"rankingPeriod,omitempty"`
		MaxConcurrentMatch string `json:"maxConcurrentMatch,omitempty"`
		MaxMatchPerRunner  string `json:"maxMatchPerRunner,omitempty"`
		MatchTimeout       string `json:"matchTimeout,omitempty"`
	}{
		EndTime:            s.EndTime.Format(time.RFC3339),
		RankingPeriod:      s.RankingPeriod.String(),
		MaxConcurrentMatch: intToString(s.MaxConcurrentMatch),
		MaxMatchPerRunner:  intToString(s.MaxMatchPerRunner),
		MatchTimeout:       s.MatchTimeout.String(),
	})
}

func (s *SettingsEntries) UnmarshalJSON(data []byte) error {
	var m map[string]*string = make(map[string]*string)

	if err := json.Unmarshal(data, &m); err != nil {
		return err
	}

	return fromMap(s, m)
}

type Settings struct {
	db        *database.Database
	statsLock sync.RWMutex
	entries   *SettingsEntries
}

func getSetting(db *database.Database, ctx context.Context, key string) (*string, error) {
	conn, err := db.AcquireConnection(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Release()

	var value string
	err = conn.QueryRow(ctx, "SELECT setting FROM settings WHERE id = $1", key).Scan(&value)
	if err != nil {
		return nil, nil
	}

	return &value, nil
}

func setSetting(db *database.Database, key string, value string, ctx context.Context) error {
	conn, err := db.AcquireConnection(ctx)
	if err != nil {
		return err
	}

	defer conn.Release()

	_, err = conn.Exec(ctx, "INSERT INTO settings (id, setting) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET setting = $2", key, value)
	if err != nil {
		return err
	}

	return nil
}

func loadSettings(db *database.Database, ctx context.Context) (*SettingsEntries, error) {
	entries := make(map[string]*string)
	json.Unmarshal([]byte(DEFAULT_SETTINGS), &entries)

	for key, value := range entries {
		dbValue, err := getSetting(db, ctx, key)
		if err != nil {
			return nil, err
		}

		if dbValue == nil {
			setSetting(db, key, *value, ctx)
		} else {
			entries[key] = value
		}
	}

	settingsEntries := SettingsEntries{}
	err := fromMap(&settingsEntries, entries)

	return &settingsEntries, err
}

func NewSettings(db *database.Database, ctx context.Context) (*Settings, error) {
	settings := Settings{db: db, entries: nil, statsLock: sync.RWMutex{}}

	entries, err := loadSettings(db, ctx)
	if err != nil {
		return nil, err
	}

	settings.entries = entries
	return &settings, nil
}

func (p *Settings) GetSettings() *SettingsEntries {
	p.statsLock.RLock()
	defer p.statsLock.RUnlock()

	return p.entries
}

func (p *Settings) SetSettings(m map[string]*string, ctx context.Context) error {
	p.statsLock.Lock()
	defer p.statsLock.Unlock()

	settingsEntries := *p.entries
	err := fromMap(&settingsEntries, m)
	if err != nil {
		return err
	}

	for key, value := range m {
		setSetting(p.db, key, *value, ctx)
	}

	p.entries = &settingsEntries

	return err
}
