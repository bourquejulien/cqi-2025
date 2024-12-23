package settings

import (
	"context"
	"cqiprog/data/database"
	_ "embed"
	"fmt"
	"strconv"
	"sync"

	"time"
)

const (
	DEFAULT_END_TIME = "2025-01-17T12:00:00Z"
	DEFAULT_RANKING_PERIOD = 30 * time.Minute
	DEFAULT_MAX_CONCURRENT_MATCH = 10
	DEFAULT_MAX_CONCURRENT_MATCH_PER_RUNNER = 1
)

type SettingsEntries struct {
	EndTime time.Time
	RankingPeriod time.Duration
	MaxConcurrentMatch int
	MaxConcurrentMatchPerRunner int
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
	defaultEndTime, err :=  time.Parse(time.RFC3339, DEFAULT_END_TIME)

	if err != nil {
		return nil, err
	}

	entries := SettingsEntries{defaultEndTime, DEFAULT_RANKING_PERIOD, DEFAULT_MAX_CONCURRENT_MATCH, DEFAULT_MAX_CONCURRENT_MATCH_PER_RUNNER}

	endTime, err := getSetting(db, ctx, "end_time")
	if err != nil {
		return nil, err
	}

	if endTime == nil {
		setSetting(db, "end_time", entries.EndTime.Format(time.RFC3339), ctx)
	} else {
		entries.EndTime, err = time.Parse(time.RFC3339, *endTime)
		if err != nil {
			return nil, err
		}
	}

	rankingPeriod, err := getSetting(db, ctx, "ranking_period")
	if err != nil {
		return nil, err
	}

	if rankingPeriod == nil {
		setSetting(db, "ranking_period", durationToString(entries.RankingPeriod), ctx)
	} else {
		entries.RankingPeriod, err = time.ParseDuration(*rankingPeriod)
		if err != nil {
			return nil, err
		}
	}

	setNumeric := func (name string, defaultValue int) (int, error) {
		value, err := getSetting(db, ctx, name)
		if err != nil {
			return 0, nil
		}

		if value == nil {
			setSetting(db, name, fmt.Sprintf("%d", defaultValue), ctx)
			return defaultValue, nil
		}

		result, err := strconv.Atoi(*value)

		if err != nil {
			return 0, err
		}

		return result, nil
	}

	entries.MaxConcurrentMatch, err = setNumeric("max_concurrent_match", DEFAULT_MAX_CONCURRENT_MATCH)

	if err != nil {
		return nil, err
	}

	entries.MaxConcurrentMatchPerRunner, err = setNumeric("max_match_per_runner", DEFAULT_MAX_CONCURRENT_MATCH_PER_RUNNER)

	if err != nil {
		return nil, err
	}

	return &entries, nil
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

func (p* Settings) SetSettings(entries map[string]string, ctx context.Context) error {
	p.statsLock.Lock()
	defer p.statsLock.Unlock()

	currentEntries := *p.entries

	var err error

	if value, ok := entries["end_time"]; ok {
		if endTime, err := getTimeFromString(value); err != nil {
			currentEntries.EndTime = endTime
			err = setSetting(p.db, "end_time", timeToString(endTime), ctx)
		}
	}

	if value, ok := entries["ranking_period"]; ok {
		if rankingPeriod, err := getDurationFromString(value); err != nil {
			currentEntries.RankingPeriod = rankingPeriod
			err = setSetting(p.db, "ranking_period", durationToString(rankingPeriod), ctx)
		}
	}

	if value, ok := entries["max_concurrent_match"]; ok {
		if maxConcurrentMatch, err := getIntFromString(value); err != nil {
			currentEntries.MaxConcurrentMatch = maxConcurrentMatch
			err = setSetting(p.db, "max_concurrent_match", intToString(maxConcurrentMatch), ctx)
		}
	}

	if value, ok := entries["max_match_per_runner"]; ok {
		if maxMatchPerRunner, err := getIntFromString(value); err != nil {
			currentEntries.MaxConcurrentMatchPerRunner = maxMatchPerRunner
			err = setSetting(p.db, "max_match_per_runner", intToString(maxMatchPerRunner), ctx)
		}
	}

	p.entries = &currentEntries

	return err 
}
